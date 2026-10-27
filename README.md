# 👻 GhostShell

> **A spooky, local-first AI developer assistant for the “Ghost in the Machine” open-source AI challenge.**

```text
        .-"-.     _____ _               _   ____  _          _ _ 
       /     \   / ____| |             | | / ___|| |        | | |
      | () () | | |  __| |__   ___  ___| |_\___ \| |__   ___| | |
       \  ^  /  | | |_ | '_ \ / _ \/ __| __|___) | '_ \ / _ \ | |
        |||||   | |__| | | | | (_) \__ \ |_|____/| | | |  __/ | |
       '-----'   \_____|_| |_|\___/|___/\__|     |_| |_|\___|_|_|

    ⚡ GHOST IN THE MACHINE • LOCAL-FIRST AI COMPANION • PHASE 2 ⚡
```

GhostShell is a haunted terminal companion that observes your command history, Git activity, and coding mistakes, translating them into eerie, intelligent commentary from a fictional ghost dwelling inside your machine.

---

## 🔮 Phase 2: Local Gemma 3 1B Integration

Phase 2 binds GhostShell to an on-device **Google Gemma 3 1B Instruct** model via a local `llama.cpp` server, achieving **100% private, local-first execution with zero cloud telemetry**:

- 🧠 **Target Model: Gemma 3 1B Instruct (GGUF Quantization):** Specially optimized for 8 GB RAM Windows laptops without dedicated GPUs. Quantizations like `Q4_K_M` (~1.0 GB disk footprint, ~1.8 GB active RAM) run blazingly fast purely on CPU.
- 🔌 **OpenAI-Compatible Local Endpoint:** Integrates seamlessly with `http://127.0.0.1:8080/v1/chat/completions`.
- ⏳ **Haunted Loading Spinner:** Dynamic phosphor green CRT spinner animates while Gemma inscribes its response.
- 🛡️ **Zero-Execution Security Sandbox:** GhostShell **never** executes commands suggested by Gemma or typed by the user. Responses are rendered safely as Markdown with syntax highlighting.
- 💡 **Resilient Offline Fallback:** If the `llama.cpp` server is not running, GhostShell catches the condition without crashing, displaying clear startup commands while remaining fully interactive.
- 📜 **Built-in Grimoire Rites:** Complete support for `/help`, `/model`, `/clear`, `/quit`, `/exit`, `/status`, and `/about`.

---

## 📂 Project Architecture

```text
GhostShell/
├── main.py                     # Entry point & interactive REPL loop
├── requirements.txt            # Python package dependencies (Rich, Pytest)
├── .gitignore                  # Git ignore rules for Python & environments
├── README.md                   # Complete documentation & Windows setup guide
│
├── ghostshell/                 # Core GhostShell package
│   ├── __init__.py             # Exports & version metadata (v0.2.0)
│   ├── client.py               # Modular HTTP client for local OpenAI-compatible endpoint
│   ├── config.py               # Themes, model endpoints, and security invariants
│   ├── ui.py                   # Rich terminal UI, ASCII banners, panels, spinner & prompt
│   ├── commands.py             # Slash command registry (/help, /model, /status, etc.)
│   └── engine.py               # Response engines (GemmaEngine & PlaceholderEngine)
│
└── tests/                      # Automated test suite (46 passing tests)
    ├── __init__.py
    ├── test_client.py          # Mocked HTTP client tests (success, offline, timeouts)
    ├── test_commands.py        # Slash command parsing and model probe tests
    ├── test_config.py          # Configuration and security immutability tests
    ├── test_engine.py          # GemmaEngine and PlaceholderEngine unit tests
    ├── test_integration.py     # End-to-end mock server integration test
    ├── test_repl.py            # REPL loop, signal handling (Ctrl+C, EOF) tests
    ├── test_security.py        # Strict command execution prevention tests
    └── test_ui.py              # Visual UI rendering and panel tests
```

---

## 🚀 Windows PowerShell Setup Instructions

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.10 through 3.14)
- **Windows PowerShell** or **Windows Terminal** (recommended for TrueColor support)
- **Git**

### 2. Clone and Setup Environment
Open Windows PowerShell in your projects directory:

```powershell
git clone https://github.com/RudraBhullar/GhostShell.git
cd GhostShell

# Create and activate virtual environment
python -m venv venv

# If execution policy blocks script activation:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

.\venv\Scripts\Activate.ps1

# Install lightweight dependencies
pip install -r requirements.txt
```

---

### 3. Setting Up Local Gemma 3 1B via `llama.cpp`

GhostShell connects to any local OpenAI-compatible server at `http://127.0.0.1:8080`. Here is the recommended setup for an 8 GB RAM Windows laptop:

#### Step A: Download `llama.cpp` for Windows
1. Download the latest Windows release (`llama-bXXXX-bin-win-avx2-x64.zip` or `llama-server.exe`) from the [llama.cpp GitHub releases](https://github.com/ggerganov/llama.cpp/releases).
2. Extract `llama-server.exe` into a folder (for example, `C:\llama.cpp\`).

#### Step B: Download Gemma 3 1B Instruct GGUF
Download the `Q4_K_M` quantization of Gemma 3 1B Instruct (~1.0 GB):
- **Model:** `gemma-3-1b-it-Q4_K_M.gguf`
- Place it in a `models/` directory:
```powershell
New-Item -ItemType Directory -Force -Path models
# Download the model GGUF (e.g., from Hugging Face):
# https://huggingface.co/google/gemma-3-1b-it-GGUF
```

#### Step C: Start the Local Model Server
In a separate PowerShell window, start `llama-server`:
```powershell
.\llama-server.exe -m .\models\gemma-3-1b-it-Q4_K_M.gguf --port 8080 -c 2048 -ngl 0
```
> **Tip for 8 GB RAM Laptops:** `-ngl 0` ensures 100% CPU inference, keeping GPU VRAM clear and memory footprint at ~1.8 GB.

---

### 4. Launching GhostShell

Once your virtual environment is active, start GhostShell:

```powershell
# Standard launch
python main.py

# Launch without boot animation
python main.py --no-animation

# Launch with custom endpoint or model
python main.py --endpoint http://127.0.0.1:8080/v1/chat/completions --model gemma-3-1b-it

# Launch in Phase 1 standalone UI Dev mode (no model required)
python main.py --placeholder
```

---

### 5. CLI Flags & Diagnostics

```powershell
# Check diagnostics and probe model server status
python main.py --diagnostics

# Display version
python main.py --version

# Display CLI help
python main.py --help
```

---

## 📜 Built-in Slash Commands

| Command | Usage | Description | Aliases |
| :--- | :--- | :--- | :--- |
| `/help` | `/help [command]` | Summon the grimoire of available rites and commands. | `/?` |
| `/model` | `/model` | Inspect the local model endpoint, name, and connection status. | `/gemma` |
| `/status` | `/status` | Inspect conduit health, live server connectivity, and locks. | `/diag` |
| `/clear` | `/clear` | Banish previous screen spirits and refresh the viewport. | `/cls` |
| `/exit` | `/exit` | Release the ghost and return safely to host OS. | `/quit`, `/q` |
| `/about` | `/about` | View the lore behind the Ghost in the Machine challenge. | — |

---

## 🛡️ Security Model

In strict accordance with the challenge guidelines:
1. **Never Execute User or AI Commands:** GhostShell will never invoke `subprocess`, `os.system`, `exec`, `eval`, or shell interpreters on user inputs or assistant responses.
2. **Hardcoded Containment Flag:** `GhostConfig.allow_command_execution` is immutable and hardcoded to `False`. Attempting to alter it at runtime raises an immediate `ValueError`.
3. **Markdown Code Blocks:** Any code snippets produced by Gemma are rendered purely as styled text/Markdown within the terminal.

---

## 🧪 Automated Test Suite

GhostShell includes **46 automated tests** using mocked HTTP responses and a simulated local server, requiring **zero model downloads** to run:

```powershell
pytest
```
*Result: 46 passed in 1.38s.*
