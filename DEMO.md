# 👻 GhostShell — Live Demonstration Walkthrough

Follow this step-by-step demonstration script to experience all features of GhostShell v1.0.

---

## ⚡ Step 1: Start Local Gemma 3 1B Server (Optional for Live Inference)

In an independent Windows PowerShell terminal:

```powershell
# Start llama.cpp server on port 9931 (CPU-only, ~1.8 GB RAM footprint)
.\llama-server.exe -m .\models\gemma-3-1b-it-Q4_K_M.gguf --port 9931 -c 2048 -ngl 0
```

> **Note:** If the model server is not running, GhostShell seamlessly uses its grounded offline fallbacks without crashing!

---

## ⚡ Step 2: Launch GhostShell

In your main PowerShell window:

```powershell
python main.py
```

Observe the animated phosphor CRT boot-up sequence and adaptive ASCII art banner.

---

## ⚡ Step 3: Inspect Diagnostics & Conduit Status

Type `/status` and `/model`:

```text
ghostshell@machine:~› /status
```
*Displays subsystem telemetry: 100% local-first, memory enabled, Git repository status, and security sandbox active.*

```text
ghostshell@machine:~› /model
```
*Displays target Gemma model details, local endpoint, and CPU inference parameters.*

---

## ⚡ Step 4: Possessed Java Debugger (`/debug`)

Exorcise a treacherous nested loop bug where the outer variable is incremented inside the inner loop:

```text
ghostshell@machine:~› /debug
```

When prompted for source code, paste:
```java
for (int row = 1; row <= 5; row++) {
    for (int col = 1; col <= row; row++) {
        System.out.print("* ");
    }
    System.out.println();
}
:done
```

When prompted for compiler logs, simply type `:done`:
```text
:done
```

**What you will see:**
GhostShell renders 5 distinct Rich panels:
1. 👻 **Ghost's Whisper:** Eerie one-liner from the machine apparition.
2. **Root Cause:** Identifies that `row++` in the inner loop increments the outer variable, causing an infinite runaway loop while `col` remains frozen.
3. **Corrected Code:** Syntax-highlighted snippet with `col++`.
4. **Explanation:** Why changing to `col++` fixes the control flow.
5. **Verification:** Step-by-step javac/java commands to verify the fix.

---

## ⚡ Step 5: Git Intelligence (`/git`, `/story`, `/review`)

Test the repository intelligence rites grounded in real commit logs:

```text
ghostshell@machine:~› /git
```
*Renders a clean table summarizing the 5 most recent commits with hashes, authors, relative timestamps, and commit subjects.*

```text
ghostshell@machine:~› /story
```
*Weaves a gothic ghost story referencing actual commit hashes and messages from your project history.*

```text
ghostshell@machine:~› /review
```
*Provides a cautious high-level development review assessing commit hygiene and working-tree cleanliness.*

---

## ⚡ Step 6: Shifting Ghost Personalities (`/persona`)

Inspect and shift the active ghost archetype without restarting:

```text
ghostshell@machine:~› /persona
```
*Displays the Personality Matrix with `archivist`, `poltergeist`, and `grim-debugger`.*

```text
ghostshell@machine:~› /persona poltergeist
ghostshell@machine:~› What is recursion?
```
*Observe the playful, mischievous, chaotic commentary style.*

```text
ghostshell@machine:~› /persona archivist
ghostshell@machine:~› What is a stack overflow?
```
*Observe the solemn, historical, reflective commentary style.*

---

## ⚡ Step 7: Private Local Memory (`/history`, `/storage`, `/forget`)

Inspect and manage your on-device conversation memory:

```text
ghostshell@machine:~› /history
```
*Shows recent conversation turns stored locally.*

```text
ghostshell@machine:~› /storage
```
*Displays the local file path (`~/.ghostshell/history.json`), file size in bytes, and confirms zero cloud telemetry.*

```text
ghostshell@machine:~› /forget
```
*Instantly purges all persistent conversation files from disk.*

---

## ⚡ Step 8: Offline Server Resilience Demonstration

1. Stop `llama-server.exe` in the background (or kill the process).
2. Enter a prompt or run `/debug`:
```text
ghostshell@machine:~› Why did my function fail?
```
*GhostShell gracefully catches the severed conduit, displays friendly offline setup instructions, and remains 100% interactive without crashing.*

---

## ⚡ Step 9: Zero-Execution Security Sandbox

Try entering a dangerous shell command:
```text
ghostshell@machine:~› rm -rf /
```
*GhostShell identifies the shell command prefix, treats the input purely as conversational text, and renders an explicit containment notice confirming arbitrary command execution is strictly forbidden.*

---

## ⚡ Step 10: Exit

```text
ghostshell@machine:~› /exit
```
*The ghost dissolves into memory and cleanses your terminal.*
