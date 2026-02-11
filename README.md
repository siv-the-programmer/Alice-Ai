# Alice-Ai



A local terminal-based AI assistant powered by Ollama with lightweight persistent memory stored in SQLite.  
Designed for fast CLI interaction, experimentation, and local automation workflows.

This project runs **entirely locally**. No cloud APIs, no external telemetry, no credentials.

---

## Attribution & Disclosure

This project was **partially written with the assistance of the Ollama 2.3.8B model**.

I do **not** claim full authorship of all logic, structure, or ideas contained in this repository.  
The code represents a collaborative output between human direction, iteration, and AI-assisted generation.

All responsibility for usage, modification, and deployment remains with the user.

---

## Features

- Terminal chat interface using a local Ollama model
- Optional memory injection for contextual continuity
- Structured memory system with categories
- SQLite-backed local storage
- Streaming responses
- Simple command-based control

---

## How Memory Works

Memory is stored locally in a SQLite database:

~/.alice/alice_memory.db

Only predefined categories are allowed to keep memory structured:

- identity  
- preferences  
- goals  
- workflow  
- skills  
- projects  
- constraints  

If an invalid category is provided, it defaults to `preferences`.

Memory can be:
- **Pinned** (always injected first)
- **Normal** (recently injected until limit)

A size cap is enforced to prevent prompt bloat.

---

## Requirements

- Linux or macOS (recommended)
- Python 3.10+
- Ollama installed and running locally
- At least one Ollama model pulled

Python dependencies:
- ollama
- rich

---

## Installation

Clone the repository:

git clone
```
https://github.com/siv-the-programmer/Alice-AI.git  
cd your-repo
```

Create and activate a virtual environment:

```
python3 -m venv .venv  
source .venv/bin/activate
```
Install dependencies:
```
pip install -U pip  
pip install ollama rich

```

---

## Running the Bot

Start the CLI:
```
python3 CLI_bot.py
```
On first run, the application will take 1 to 2 mins to fully start as it will automatically create:

~/.alice/  
~/.alice/alice_memory.db

No manual setup required.

# Screenshot1

<img src="pic1.jpg" width="400" alt="Screenshot1">

# Screenshot2

<img src="pic2.jpg" width="400" alt="Screenshot2">

---

## CLI Commands
```
- /help — Show commands  
- /mem — List memories  
- /save <category>|<text> — Save memory  
- /pin <category>|<text> — Save pinned memory  
- /forget <id> — Delete memory  
- /reset — Reset database  
- /chaos <1–10> — Adjust response intensity  
- exit — Quit  
```
Examples:
```
/save projects|Building Python automation tools  
/pin workflow|Be concise and ask one clarification if unsure  
/chaos 8
```
---

## GitHub Safety

This repository contains **no secrets or credentials**.

Excluded by design:
- SQLite databases
- User memory
- Environment files

All personal data remains local and is ignored by Git.

---

<a href="https://buymeacoffee.com/sivariob" target="_blank" rel="noopener">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" style="height: 60px !important; width: 217px !important;">
</a>


## License

Personal / educational use.
