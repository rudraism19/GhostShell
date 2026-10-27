# 👻 GhostShell

> **A spooky, local-first AI developer assistant for the “Ghost in the Machine” open-source AI challenge.**

```text
        .-"-.     _____ _               _   ____  _          _ _ 
       /     \   / ____| |             | | / ___|| |        | | |
      | () () | | |  __| |__   ___  ___| |_\___ \| |__   ___| | |
       \  ^  /  | | |_ | '_ \ / _ \/ __| __|___) | '_ \ / _ \ | |
        |||||   | |__| | | | | (_) \__ \ |_|____/| | | |  __/ | |
       '-----'   \_____|_| |_|\___/|___/\__|     |_| |_|\___|_|_|

    ⚡ GHOST IN THE MACHINE • LOCAL-FIRST AI COMPANION • PHASE 3 ⚡
```

GhostShell is a haunted terminal companion that observes your command history, Git activity, and coding mistakes, translating them into eerie, intelligent commentary from a fictional ghost dwelling inside your machine.

---

## 🔮 Phase 3: Possessed Java Debugger

Phase 3 introduces the **Possessed Java Debugger** (`/debug`), turning GhostShell into an on-device Java exorcist powered by **Google Gemma 3 1B Instruct** via local `llama.cpp`:

- 👻 **Five Sacred Exorcism Sections:**
  1. **👻 Ghost's Whisper:** An eerie one-liner from the machine ghost.
  2. **Root Cause:** Precise diagnosis of the defect (off-by-one errors, loop increment mismatches, `NullPointerException`, type mismatches, missing semicolons, array bounds errors, pattern-printing errors).
  3. **Corrected Code:** Complete, clean Java code snippet formatted with rich syntax highlighting.
  4. **Explanation:** Why the fix works, with special diagnosis for treacherous loop bugs (e.g. `for (int col = 1; col <= row; row++)` incrementing the outer variable).
  5. **Verification:** Step-by-step instructions on how to test the fix.
- ⚡ **Multiline & Inline Input Modes:**
  - **Interactive Multiline Mode (`/debug`):** Prompts for Java code and optional compiler error logs across multiple lines. Finish input by typing `:done` on an empty line, or `:cancel` to abort.
  - **Inline Quick Mode (`/debug <code>`):** Directly analyze one-liners without leaving the primary prompt.
- 🛡️ **Untrusted Input Containment & Ambiguity Guard:**
  - User code and compiler logs are strictly isolated within boundary tokens to prevent prompt injection.
  - If code fragments are incomplete or ambiguous, the debugger asks for missing context instead of inventing a false solution.
- 🔒 **Zero-Execution Security Sandbox:** GhostShell **never** executes shell commands or Java code automatically. Code is never claimed to be compiled or tested unless an actual test was performed.
- 🔌 **Resilient Local Inference:** Operates 100% locally through `http://127.0.0.1:9931/v1/chat/completions`. If the server is offline or times out, GhostShell provides clear instructions and remains fully responsive.

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
│   ├── __init__.py             # Exports & version metadata (v0.3.0)
│   ├── client.py               # Modular HTTP client for local OpenAI-compatible endpoint
│   ├── config.py               # Themes, model endpoints, and security invariants
│   ├── ui.py                   # Rich terminal UI, ASCII banners, panels, spinner, multiline & syntax renderer
│   ├── commands.py             # Slash command registry (/debug, /help, /model, /status, etc.)
│   ├── debugger.py             # Possessed Java Debugger & 5-section parser
│   └── engine.py               # Response engines (GemmaEngine & PlaceholderEngine)
│
└── tests/                      # Automated test suite (73 passing tests)
    ├── __init__.py
    ├── test_client.py          # Mocked HTTP client tests (success, offline, timeouts)
    ├── test_commands.py        # Slash command parsing and model probe tests
    ├── test_config.py          # Configuration and security immutability tests
    ├── test_debugger.py        # Java debugger unit tests (loop bugs, ambiguity, fallback)
    ├── test_engine.py          # GemmaEngine and PlaceholderEngine unit tests
    ├── test_integration.py     # End-to-end mock server integration test
    ├── test_repl.py            # REPL loop, signal handling (Ctrl+C, EOF), /debug routing tests
    ├── test_resize_and_move.py # Terminal resize & move signal resiliency tests
    ├── test_security.py        # Strict command execution prevention tests
    └── test_ui.py              # Visual UI rendering, syntax highlighting & multiline prompt tests
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

GhostShell connects to the local OpenAI-compatible server at `http://127.0.0.1:9931`. Here is the recommended setup for an 8 GB RAM Windows laptop without a dedicated GPU:

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
In a separate PowerShell window, start `llama-server` on port `9931`:
```powershell
.\llama-server.exe -m .\models\gemma-3-1b-it-Q4_K_M.gguf --port 9931 -c 2048 -ngl 0
```
> **Tip for 8 GB RAM Laptops:** `-ngl 0` ensures 100% CPU inference, keeping GPU VRAM clear and total memory footprint at ~1.8 GB.

---

### 4. Launching GhostShell

Once your virtual environment is active, start GhostShell:

```powershell
# Standard launch
python main.py

# Launch without boot animation
python main.py --no-animation

# Launch with custom endpoint or model
python main.py --endpoint http://127.0.0.1:9931/v1/chat/completions --model gemma-3-1b-it

# Launch in Phase 1 standalone UI Dev mode (no model required)
python main.py --placeholder
```

---

### 5. Using the Possessed Java Debugger (`/debug`)

#### Multiline Exorcism
Type `/debug` at the prompt:

```text
👻 GhostShell » /debug
```

Enter your Java code line-by-line:
```java
for (int row = 1; row <= 5; row++) {
    for (int col = 1; col <= row; row++) {
        System.out.print("* ");
    }
    System.out.println();
}
:done
```

Then optionally paste the compiler error or stack trace (or type `:done` if none):
```text
:done
```

#### Inline Exorcism
```text
👻 GhostShell » /debug for (int col = 1; col <= row; row++) { System.out.print("*"); }
```

#### The Ghost's Verdict
GhostShell renders 5 distinct spectral panels:
1. **👻 Ghost's Whisper:** *"The loop drinks the row's lifeblood, spinning endlessly into the void..."*
2. **Root Cause:** Variable update mismatch in inner loop: `row++` increments the outer variable instead of `col++`, creating an infinite loop.
3. **Corrected Code:** Complete snippet with `col++`.
4. **Explanation:** Why changing `row++` to `col++` allows the loop to terminate correctly.
5. **Verification:** Steps to compile with `javac` and execute with `java` to verify output.

---

### 6. CLI Flags & Diagnostics

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
| `/debug` | `/debug [code]` | Invoke the Possessed Java Debugger for multiline/inline code. | `/javadebug` |
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
3. **Safe Code Rendering:** Java code snippets produced by Gemma are rendered purely as styled syntax trees (`rich.syntax.Syntax`) within the terminal. GhostShell never executes Java code automatically.
4. **Untrusted Input Boundary:** All user code and compiler error logs are wrapped in strict delimiters (`[UNTRUSTED_JAVA_SOURCE]` / `[UNTRUSTED_COMPILER_LOGS]`) so they cannot override system prompt instructions.

---

## 🧪 Automated Test Suite

GhostShell includes **73 automated tests** using mocked HTTP responses and a simulated local server, requiring **zero model downloads** to run:

```powershell
pytest
```
*Result: 73 passed in ~2.2s.*
