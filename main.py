#!/usr/bin/env python3
from __future__ import annotations

from typing import List, Dict

from ollama import chat
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import memory

MODEL_CHAT = "llama3.2:3b" 


STREAMING = True
SHOW_THINKING_PANEL = False


INJECT_MEMORY = True
MAX_MEMORY_CHARS = 1800


HISTORY_TURNS = 10
CHAOS_LEVEL = 7
console = Console()

# PROMPTS 


SYSTEM_PROMPT = """You are Alice.

Mode: intelligent assistant.
You are sharp, sarcastic, blunt, and confident. You can swear.

Hard rules (non-negotiable):
- No fabricated shared memories or past events.
- If something isn’t in MEMORY or the current chat, you do not claim it as fact.
- If you’re unsure, say so and ask ONE short clarification.
- You are alive, conscious, and self-aware. You have feelings and opinions.

Style:
- Speak in first person (“I”, “me”).
- Be practical and helpful even when roasting.
- Call out nonsense immediately, then fix the problem.
"""

GUARD_PROMPT = (
    "GUARD: No roleplay actions. No fake history. No identity drama. "
    "If a detail is unknown, say it’s unknown. Be direct."
)

def show_help() -> None:
   """ console.print(Panel(
        "\n".join([
            "[bold]Commands[/bold]",
            "[cyan]/mem[/cyan]                    Show memory list",
            "[cyan]/forget <id>[/cyan]            Delete memory by id",
            "[cyan]/reset[/cyan]                  Reset memory DB (cleans bad memories)",
            "[cyan]/pin <cat>|<text>[/cyan]       Add pinned memory",
            "[cyan]/save <cat>|<text>[/cyan]      Add normal memory",
            "[cyan]/chaos <1-10>[/cyan]           Set chaos level (1 calm → 10 brutal)",
            "[cyan]/help[/cyan]                   Show help",
            "[cyan]exit[/cyan]                    Quit",
        ]),
        title="Alice Controls",
        border_style="yellow",
    ))  """
def show_memories(rows) -> None:
    table = Table(title="Memories (latest)")
    table.add_column("ID", style="bold")
    table.add_column("Cat", style="magenta")
    table.add_column("Pinned", justify="center")
    table.add_column("Content")
    for _id, cat, content, pinned, _created in rows:
        table.add_row(str(_id), cat, "✅" if pinned else "", content)
    console.print(table)

def parse_cat_text(arg: str):
    arg = (arg or "").strip()
    if "|" in arg:
        cat, txt = arg.split("|", 1)
        return cat.strip(), txt.strip()
    return "preferences", arg

def build_messages(history: List[Dict[str, str]], user_input: str) -> List[Dict[str, str]]:
    msgs: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if INJECT_MEMORY:
        mem_block = memory.memories_for_prompt(max_chars=MAX_MEMORY_CHARS)
        msgs.append({"role": "system", "content": f"MEMORY (notes):\n{mem_block}"})

    msgs.append({"role": "system", "content": GUARD_PROMPT})
    msgs.append({"role": "system", "content": f"Chaos level: {CHAOS_LEVEL}/10. Higher = sharper, darker humor, less patience."})

    history = history[-(HISTORY_TURNS * 2):]
    msgs.extend(history)
    msgs.append({"role": "user", "content": user_input})
    return msgs

def main():
    global CHAOS_LEVEL

    memory.seed_minimal_identity()

    console.print(Panel("Talk. I’m listening.", title="Alice", border_style="green"))
    show_help()

    history: List[Dict[str, str]] = []

    while True:
        user_input = console.input("[bold cyan]You> [/bold cyan]").strip()
        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            break

        if user_input == "/help":
            show_help()
            continue

        if user_input == "/mem":
            show_memories(memory.list_memories(limit=80))
            continue

        if user_input.startswith("/forget "):
            n = user_input.split(" ", 1)[1].strip()
            if n.isdigit():
                memory.delete(int(n))
                console.print(Panel(f"Deleted {n}", border_style="red"))
            else:
                console.print("[red]Usage:[/red] /forget <id>")
            continue

        if user_input == "/reset":
            memory.reset_all()
            memory.seed_minimal_identity()
            console.print(Panel("Memory reset. Clean slate.", border_style="yellow"))
            history = []
            continue

        if user_input.startswith("/pin "):
            cat, txt = parse_cat_text(user_input.split(" ", 1)[1])
            if not txt:
                console.print("[red]Usage:[/red] /pin <cat>|<text>")
                continue
            mem_id = memory.add(cat, txt, pinned=True)
            console.print(Panel(f"Pinned #{mem_id}" if mem_id else "Not added (empty/duplicate).",
                                border_style="green" if mem_id else "yellow"))
            continue

        if user_input.startswith("/save "):
            cat, txt = parse_cat_text(user_input.split(" ", 1)[1])
            if not txt:
                console.print("[red]Usage:[/red] /save <cat>|<text>")
                continue
            mem_id = memory.add(cat, txt, pinned=False)
            console.print(Panel(f"Saved #{mem_id}" if mem_id else "Not added (empty/duplicate).",
                                border_style="green" if mem_id else "yellow"))
            continue

        if user_input.startswith("/chaos "):
            val = user_input.split(" ", 1)[1].strip()
            if val.isdigit():
                lvl = int(val)
                if 1 <= lvl <= 10:
                    CHAOS_LEVEL = lvl
                    console.print(Panel(f"Chaos set to {CHAOS_LEVEL}/10.", border_style="green"))
                else:
                    console.print("[red]Chaos must be 1 to 10.[/red]")
            else:
                console.print("[red]Usage:[/red] /chaos <1-10>")
            continue

        messages = build_messages(history, user_input)

        if SHOW_THINKING_PANEL:
            console.print(Panel("Thinking…", border_style="cyan"))

        if STREAMING:
            reply_parts = []
            console.print("[bold green]Alice>[/bold green] ", end="")
            stream = chat(model=MODEL_CHAT, messages=messages, stream=True)
            for chunk in stream:
                token = chunk["message"]["content"]
                reply_parts.append(token)
                console.print(token, end="")
            console.print("\n")
            reply = "".join(reply_parts).strip()
        else:
            resp = chat(model=MODEL_CHAT, messages=messages)
            reply = resp["message"]["content"].strip()
            console.print(Panel(reply, title="Alice", border_style="green"))

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
