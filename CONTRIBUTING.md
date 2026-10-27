# Contributing to GhostShell 👻

Thank you for your interest in contributing to **GhostShell — The Terminal That Remembers**! 

GhostShell is an open-source AI developer companion created for the **Hacktoberfest "Ghost in the Machine" AI Challenge**. We welcome improvements, bug reports, and contributions that uphold our core design principles.

---

## 🔒 Core Invariants & Non-Negotiables

When submitting contributions, the following architectural and security invariants **must strictly be respected**:

1. **Zero-Execution Sandbox (`ALLOW_COMMAND_EXECUTION = False`):**
   - GhostShell is an advisory coding companion, **never an autonomous command execution agent**.
   - Neither user inputs nor model responses are ever evaluated with `os.system`, `subprocess(shell=True)`, `eval()`, or `exec()`.
   - The security containment flag `GhostConfig.allow_command_execution` is immutable and must remain `False`.

2. **100% Local-First Inference (Zero Required Cloud Telemetry):**
   - GhostShell communicates with a local OpenAI-compatible endpoint (e.g. `llama.cpp` hosting Gemma 3 1B Instruct GGUF).
   - No paid cloud APIs (e.g., OpenAI, Gemini Cloud API, Anthropic) or mandatory cloud subscriptions may be added as hard runtime requirements.
   - Non-local endpoints must trigger a prominent user-facing security alert before data leaves the device.

3. **Safe Subprocess Usage for Git Intelligence:**
   - All Git inspections are strictly read-only (`git log`, `git status --porcelain`, `git branch`).
   - Never use `shell=True`. Always pass argument arrays (e.g. `["git", "log", "-n5"]`).
   - GhostShell will never stage, commit, push, reset, or alter local repositories.

4. **Private Local Memory:**
   - Conversation history is stored in plain, human-readable JSON files in `~/.ghostshell/`.
   - Memory must remain optional (`--no-memory` flag or `GHOSTSHELL_MEMORY_ENABLED=false`).
   - Atomic replacement (`os.replace`) must be used for file writes to prevent corruption.

---

## 🛠️ Local Development Setup

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/RudraBhullar/GhostShell.git
   cd GhostShell
   ```

2. **Set up a Python 3.10+ virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Run the automated test suite:**
   ```powershell
   pytest -v
   ```
   *All 115 tests should pass with 100% mock isolation, requiring zero model downloads.*

---

## 📝 Code Style Guidelines

- **Type Annotations:** All functions and methods must include explicit type hints.
- **Docstrings:** Follow Google-style or PEP 257 docstrings explaining arguments and return values.
- **Terminal Aesthetics:** Use the `GhostUI` methods and the Rich library. Respect the phosphor CRT theme (`#00FF66`, `#39FF14`, `#00F0FF`, `#FFB000`, `#FF3366`).
- **Cross-Platform & Windows Terminal:** Ensure UTF-8 standard streams and virtual terminal processing (`enable_windows_virtual_terminal()`) are maintained.

---

## 🚀 Submitting a Pull Request

1. Create a feature branch:
   ```powershell
   git checkout -b feature/your-spooky-feature
   ```
2. Write unit tests for your changes in `tests/`.
3. Verify the entire test suite passes:
   ```powershell
   pytest
   ```
4. Submit a clear Pull Request explaining your changes and confirming that no security invariants were modified.
