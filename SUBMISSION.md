# 👻 GhostShell — The Terminal That Remembers
### Hacktoberfest Open-Source AI Challenge (Week 3: Ghost in the Machine)

---

## 1. What GhostShell Does

**GhostShell** is a haunted, local-first AI developer companion engineered for the terminal. Dwelling directly inside the developer's machine, GhostShell observes coding activity, Git history, and Java compiler errors, translating them into eerie, witty, and razor-sharp commentary from a fictional ghost trapped within the silicon.

Unlike generic chatbot wrappers, GhostShell is deeply integrated into local developer workflows:
- **Possessed Java Debugger (`/debug`):** Accepts multiline source code and compiler logs, diagnosing classic traps like loop variable increment mismatches (`for (int col = 1; col <= row; row++)`), `NullPointerException`, array bounds defects, and missing syntax across 5 structured Rich panels.
- **Machine Memory & Git Intelligence (`/git`, `/story`, `/review`):** Inspects local repository records using strictly read-only subprocess calls, weaving gothic narratives grounded in authentic commit hashes and delivering cautious development hygiene reviews.
- **Private Local Memory (`/history`, `/forget`, `/storage`):** Keeps conversation context entirely on the developer's local machine using human-inspectable plain JSON with atomic replacement, easily purged with `/forget`.
- **Configurable Ghost Personalities (`/persona`):** Switches between three distinct archetypes—the reflective **Archivist**, the playful **Poltergeist**, and the dry, cynical **Grim Debugger**—altering commentary tone without compromising technical accuracy.
- **Phosphor CRT Aesthetics:** Built with Python and Rich, rendering green phosphor CRT text, dynamic spinners, adaptive ASCII art, and terminal resize/move protection on Windows PowerShell.

---

## 2. Why Open-Weight AI Matters

Proprietary cloud models lock developer workflows behind paywalls, network latency, arbitrary rate limits, and restrictive corporate terms. **Open-weight AI models**—such as Google's Gemma 3 family—fundamentally democratize software intelligence:

1. **True Developer Ownership:** When an open-weight model runs on your machine, it cannot be depreciated, altered, or retroactively restricted by a remote provider.
2. **Deterministic & Inspectable:** Developers can inspect model weights, quantizations, and system prompts down to the token level.
3. **Hardware Accessibility:** Small quantized open models (such as `gemma-3-1b-it-Q4_K_M.gguf`, ~1.0 GB disk footprint) run efficiently on standard consumer hardware—even an 8 GB RAM laptop with zero dedicated GPU.

---

## 3. How Local Inference Protects Developer Context

Developers routinely work with sensitive intellectual property: proprietary source code, private Git commit messages, internal server architecture, and unreleased security patches. Sending these artifacts to remote cloud APIs exposes organizations to data leakage, vendor logging, and potential training ingestion.

GhostShell enforces **strict on-device isolation**:
- **Zero Cloud Dependencies:** All inferences route to a locally hosted `llama.cpp` endpoint (`http://127.0.0.1:9931/v1/chat/completions`).
- **Zero Remote Telemetry:** Prompts, source files, and Git histories never leave `localhost`.
- **Non-Local Endpoint Protection:** If an external endpoint is configured, GhostShell proactively renders an unmissable security warning before any data is sent over the network.
- **Zero-Execution Sandbox:** GhostShell operates strictly as an advisory assistant. Neither user inputs nor model responses are ever executed as shell commands (`ALLOW_COMMAND_EXECUTION = False`).

---

## 4. What Works Without Internet After Setup

Once `llama.cpp`, the Gemma 3 1B GGUF model, and Python dependencies are downloaded, **100% of GhostShell functions offline**:

| Capability | Offline Status | Operational Details |
| :--- | :--- | :--- |
| **Terminal REPL & UI** | 🟢 100% Offline | All Rich panels, ASCII art, and animations run locally. |
| **Gemma 3 1B Inference** | 🟢 100% Offline | CPU-only local inference via `llama-server.exe`. |
| **Possessed Java Debugger** | 🟢 100% Offline | Multiline analysis and 5-section exorcisms run locally. |
| **Git Intelligence** | 🟢 100% Offline | Read-only subprocess calls query the local `.git` repository. |
| **Private Memory** | 🟢 100% Offline | Stored in local JSON files in `~/.ghostshell/`. |
| **Personality Switching** | 🟢 100% Offline | Persona prompts are composed entirely within the application. |

Even if `llama-server` is shut down, GhostShell's **grounded offline fallbacks** ensure the application remains completely interactive without crashing.

---

## 5. Why Replaceable Models and Prompts Are Valuable

GhostShell decouples the user experience from any single backend:
- **OpenAI-Compatible Standard:** Because GhostShell communicates via the standard OpenAI-compatible completions API, developers can swap models effortlessly—from Gemma 3 1B to Gemma 2 9B, Mistral, or Qwen—simply by passing `--model` or `--endpoint`.
- **System Prompt Composition:** Personality styles (`archivist`, `poltergeist`, `grim-debugger`) are cleanly separated from core safety invariants and technical instructions. Developers can modify the voice of the machine ghost without degrading technical diagnostic accuracy.

---

## 6. What Was Actually Implemented and Tested

Every single capability documented in GhostShell has been implemented in production code and verified through an automated test suite of **115 passing tests** (zero model download required for testing):

1. **Phase 1: Haunted Terminal UI**
   - Phosphor CRT themes, adaptive ASCII art banners, window resize/move protection, and `/help`, `/clear`, `/exit`.
2. **Phase 2: Local Gemma 3 1B Integration**
   - Lightweight `urllib` HTTP client (no bulky third-party SDKs), timeout resilience, and non-crashing offline fallbacks.
3. **Phase 3: Possessed Java Debugger**
   - `/debug` with interactive multiline input (`:done` / `:cancel`) and inline quick mode.
   - Five structured sections: 👻 Ghost's Whisper, Root Cause, Corrected Code, Explanation (with special runaway loop increment diagnosis), and Verification.
   - Ambiguity detection that requests missing context rather than hallucinating.
4. **Phase 4: Git Intelligence**
   - `/git`, `/status`, `/story`, `/review`, and `/githelp`. Safe read-only subprocess argument arrays (`shell=False`).
5. **Phase 5: Private Local Memory**
   - `/history`, `/storage`, and `/forget`. Atomic replacement JSON writes, FIFO truncation, and corruption recovery.
6. **Phase 6: Ghost Personality Engine**
   - `/persona` (`archivist`, `poltergeist`, `grim-debugger`) and `/theme` (`green`, `amber`, `cyan`, `monochrome`).
7. **Phase 7: Security & Offline Hardening**
   - Immutable `allow_command_execution = False`, untrusted input bounding, non-local endpoint detection, and signal handling (Ctrl+C, EOF).

---

## 7. How to Link a DevRelay Session

If you record an interactive coding or debugging session using the DevRelay tools, you can embed the transcript directly in this submission using the standard DevRelay Liquid tag:

```liquid
{% devrelay <session-id> %}
```

Or reference the local transcript log generated in:
```text
C:\Users\<user>\.gemini\antigravity\brain\<conversation-id>\.system_generated\logs\transcript.jsonl
```

---

## 8. License

GhostShell is released under the permissive [MIT License](LICENSE).  
The underlying Gemma model is subject to Google's [Gemma Terms of Use](https://ai.google.dev/gemma/terms).
