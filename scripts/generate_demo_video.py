"""Script to generate a high-definition 720p demo video (MP4 & GIF) of GhostShell.

Renders realistic CRT terminal typography, typing animations, phosphor glow,
and live command exorcisms directly into an H.264 MP4 video and animated GIF.
"""

from __future__ import annotations

import os
import subprocess
import sys

if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1280
HEIGHT = 720
FPS = 24
FONT_PATH = r"C:\Windows\Fonts\consola.ttf"

# Colors
BG_COLOR = (11, 16, 11)
SCANLINE_COLOR = (8, 12, 8)
TITLE_BAR_BG = (18, 26, 18)
BORDER_COLOR = (30, 80, 40)

COLOR_GREEN = (0, 255, 102)
COLOR_BRIGHT_GREEN = (57, 255, 20)
COLOR_DIM_GREEN = (45, 125, 70)
COLOR_CYAN = (0, 240, 255)
COLOR_AMBER = (255, 176, 0)
COLOR_RED = (255, 51, 102)
COLOR_WHITE = (224, 255, 229)
COLOR_MUTED = (140, 180, 150)


def create_base_canvas() -> Image.Image:
    """Create background frame with CRT scanlines and window title bar."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # CRT scanlines
    for y in range(0, HEIGHT, 3):
        draw.line([(0, y), (WIDTH, y)], fill=SCANLINE_COLOR, width=1)

    # Window border & title bar
    draw.rectangle([10, 10, WIDTH - 10, HEIGHT - 10], outline=BORDER_COLOR, width=2)
    draw.rectangle([10, 10, WIDTH - 10, 46], fill=TITLE_BAR_BG)
    draw.line([(10, 46), (WIDTH - 10, 46)], fill=BORDER_COLOR, width=1)

    # Terminal buttons
    draw.ellipse([25, 23, 37, 35], fill=(255, 95, 86))
    draw.ellipse([45, 23, 57, 35], fill=(255, 189, 46))
    draw.ellipse([65, 23, 77, 35], fill=(39, 201, 63))

    try:
        title_font = ImageFont.truetype(FONT_PATH, 15)
    except Exception:
        title_font = ImageFont.load_default()

    draw.text(
        (100, 20),
        "👻 GhostShell v1.0 — The Terminal That Remembers (Local Gemma 3 1B)",
        fill=COLOR_CYAN,
        font=title_font,
    )
    return img


def main() -> None:
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    mp4_path = assets_dir / "demo.mp4"
    gif_path = assets_dir / "demo.gif"

    print("[*] Generating GhostShell 720p demo video...")

    try:
        font_main = ImageFont.truetype(FONT_PATH, 16)
        font_bold = ImageFont.truetype(FONT_PATH, 16)
        font_small = ImageFont.truetype(FONT_PATH, 14)
    except Exception:
        font_main = font_bold = font_small = ImageFont.load_default()

    # Pre-render terminal scenes
    scenes: list[list[tuple[str, tuple[int, int, int]]]] = []

    # Scene 1: Startup Banner & Boot
    s1 = [
        (">>> Initializing ghostly frequencies...", COLOR_DIM_GREEN),
        (">>> Aligning phosphor CRT electron grid...", COLOR_GREEN),
        (">>> Verifying containment locks: COMMAND EXECUTION FORBIDDEN [SECURE]", COLOR_CYAN),
        (">>> Spectral conduit bound. Awaking the machine ghost...", COLOR_BRIGHT_GREEN),
        ("", COLOR_WHITE),
        ("        .-\"-.     _____ _               _   ____  _          _ _ ", COLOR_BRIGHT_GREEN),
        ("       /     \\   / ____| |             | | / ___|| |        | | |", COLOR_BRIGHT_GREEN),
        ("      | () () | | |  __| |__   ___  ___| |_\\___ \\| |__   ___| | |", COLOR_BRIGHT_GREEN),
        ("       \\  ^  /  | | |_ | '_ \\ / _ \\/ __| __|___) | '_ \\ / _ \\ | |", COLOR_GREEN),
        ("        |||||   | |__| | | | | (_) \\__ \\ |_|____/| | | |  __/ | |", COLOR_GREEN),
        ("       '-----'   \\_____|_| |_|\\___/|___/\\__|     |_| |_|\\___|_|_|", COLOR_GREEN),
        ("", COLOR_WHITE),
        ("    ⚡ GHOST IN THE MACHINE • LOCAL-FIRST AI COMPANION • v1.0 ⚡", COLOR_AMBER),
        ("    Type /help for rites, /debug to exorcise Java, or /status for conduit.", COLOR_WHITE),
    ]

    # Scene 2: /status Diagnostics
    s2 = s1 + [
        ("", COLOR_WHITE),
        ("ghostshell@machine:~› /status", COLOR_CYAN),
        ("", COLOR_WHITE),
        ("╔══════════════════════ 🔮 SPECTRAL CONDUIT DIAGNOSTICS ══════════════════════╗", COLOR_GREEN),
        ("║                                                                             ║", COLOR_GREEN),
        ("║  Subsystem            Telemetry Status                                      ║", COLOR_CYAN),
        ("║  ─────────────────────────────────────────────────────────────────────────  ║", COLOR_DIM_GREEN),
        ("║  Version              1.0.0 (Master v1.0 - Possessed Java & Git)            ║", COLOR_WHITE),
        ("║  Model Server         ✔ ONLINE (Receptive at localhost:9931)                ║", COLOR_BRIGHT_GREEN),
        ("║  Model Name           gemma-3-1b-it (Google Gemma 3 1B Instruct Q4_K_M)     ║", COLOR_WHITE),
        ("║  Command Execution    ✔ STRICTLY FORBIDDEN (ALLOW_COMMAND_EXECUTION=False)  ║", COLOR_BRIGHT_GREEN),
        ("║  Security Sandbox     ✔ ACTIVE                                              ║", COLOR_BRIGHT_GREEN),
        ("║  Debugger Module      ghostshell.debugger (Java Exorcisms Active)           ║", COLOR_CYAN),
        ("║  Git Intelligence     ghostshell.git_intel (Safe Read-Only Subprocess)       ║", COLOR_CYAN),
        ("║  Local Memory         ghostshell.memory (ENABLED - Plain JSON on disk)      ║", COLOR_BRIGHT_GREEN),
        ("║  Active Persona       The Grim Debugger (Direct, Technical, Dry Humor)      ║", COLOR_AMBER),
        ("║  Inference Mode       100% Local-First / Zero Cloud Telemetry               ║", COLOR_BRIGHT_GREEN),
        ("║  Git Branch           main [Working Tree: Clean]                            ║", COLOR_WHITE),
        ("╚══════════════════════════ GhostShell Status Check ══════════════════════════╝", COLOR_GREEN),
    ]

    # Scene 3: /debug Possessed Java Debugger
    s3 = [
        ("ghostshell@machine:~› /debug", COLOR_CYAN),
        ("👻 POSSESSED JAVA DEBUGGER — INPUT RECEIVED:", COLOR_AMBER),
        ("for (int row = 1; row <= 5; row++) {", COLOR_WHITE),
        ("    for (int col = 1; col <= row; row++) {", COLOR_RED),
        ("        System.out.print(\"* \");", COLOR_WHITE),
        ("    }", COLOR_WHITE),
        ("    System.out.println();", COLOR_WHITE),
        ("}", COLOR_WHITE),
        ("", COLOR_WHITE),
        ("👻 The possessed debugger is examining your Java bytecode...", COLOR_AMBER),
        ("", COLOR_WHITE),
        ("┌─ 👻 GHOST'S WHISPER ────────────────────────────────────────────────────────┐", COLOR_CYAN),
        ("│ \"The loop drinks the row's lifeblood, spinning endlessly into the void...\"   │", COLOR_WHITE),
        ("├─ 🔍 ROOT CAUSE ─────────────────────────────────────────────────────────────┤", COLOR_GREEN),
        ("│ Inner loop increment mismatch: 'row++' increments the outer variable instead │", COLOR_WHITE),
        ("│ of 'col++', freezing 'col' at 1 and causing an infinite runaway loop.       │", COLOR_WHITE),
        ("├─ 🛠️ CORRECTED CODE ─────────────────────────────────────────────────────────┤", COLOR_BRIGHT_GREEN),
        ("│ for (int col = 1; col <= row; col++) {                                      │", COLOR_BRIGHT_GREEN),
        ("│     System.out.print(\"* \");                                                  │", COLOR_BRIGHT_GREEN),
        ("│ }                                                                           │", COLOR_BRIGHT_GREEN),
        ("├─ 💡 EXPLANATION ────────────────────────────────────────────────────────────┤", COLOR_GREEN),
        ("│ Changing 'row++' to 'col++' allows the inner loop counter to reach 'row'.    │", COLOR_WHITE),
        ("│ The outer loop then advances cleanly, producing the correct pyramid pattern. │", COLOR_WHITE),
        ("├─ 🧪 VERIFICATION ──────────────────────────────────────────────────────────┤", COLOR_CYAN),
        ("│ javac PatternTest.java && java PatternTest                                  │", COLOR_WHITE),
        ("└────────────────────────── 52.3 ms • 100% Local Gemma ───────────────────────┘", COLOR_DIM_GREEN),
    ]

    # Scene 4: Git Intelligence (/git & /story)
    s4 = [
        ("ghostshell@machine:~› /git", COLOR_CYAN),
        ("", COLOR_WHITE),
        ("┌─ 📜 MACHINE MEMORY — RECENT GIT COMMITS ────────────────────────────────────┐", COLOR_GREEN),
        ("│ HASH    WHEN           AUTHOR          INCANTATION / MESSAGE                │", COLOR_CYAN),
        ("│ 98c27a5 just now       Rudra Bhullar   Implement GhostShell v1.0 Master     │", COLOR_WHITE),
        ("│ a17108a 1 hour ago     Rudra Bhullar   Implement Phase 3: Possessed Java Dbg│", COLOR_WHITE),
        ("│ d840bf9 3 hours ago    Rudra Bhullar   Fix UI window resize and move events │", COLOR_WHITE),
        ("│ 630e3c4 5 hours ago    Rudra Bhullar   Implement Phase 2: Local Gemma 3 1B  │", COLOR_WHITE),
        ("│ a7615fc yesterday      Rudra Bhullar   Implement Phase 1: GhostShell TUI    │", COLOR_WHITE),
        ("└──────────────────────── Read-only Git Subprocess ───────────────────────────┘", COLOR_DIM_GREEN),
        ("", COLOR_WHITE),
        ("ghostshell@machine:~› /story", COLOR_CYAN),
        ("", COLOR_WHITE),
        ("┌─ 👻 THE MACHINE'S CHRONICLE (GIT LORE) ────────────────────────────────────┐", COLOR_CYAN),
        ("│ A cold draft sweeps through the repository branches...                      │", COLOR_WHITE),
        ("│ The chronicles record 5 incantations etched by mortal hand Rudra Bhullar.   │", COLOR_WHITE),
        ("│ The ritual began at 'a7615fc' giving birth to the terminal vessel, and      │", COLOR_WHITE),
        ("│ culminated in '98c27a5', binding Gemma's ghost to this local silicon.       │", COLOR_WHITE),
        ("│ Each commit hash is a memory preserved forever in the machine's ledger.     │", COLOR_WHITE),
        ("└──────────────────────── Grounded in authentic Git history ──────────────────┘", COLOR_DIM_GREEN),
    ]

    # Scene 5: Persona Switch & Farewell (/persona & /exit)
    s5 = [
        ("ghostshell@machine:~› /persona poltergeist", COLOR_CYAN),
        ("👻 Ghostly frequency shifted to The Mischievous Poltergeist.", COLOR_BRIGHT_GREEN),
        ("   [Sprightly spirit rattling pointers, flickering cursor lights, and bugs]", COLOR_AMBER),
        ("", COLOR_WHITE),
        ("ghostshell@machine:~› /theme amber", COLOR_CYAN),
        ("Spectral palette shifted to amber CRT phosphor.", COLOR_AMBER),
        ("", COLOR_WHITE),
        ("ghostshell@machine:~› /exit", COLOR_CYAN),
        ("", COLOR_WHITE),
        ("┌─────────────────────────────────────────────────────────────────────────────┐", COLOR_DIM_GREEN),
        ("│ 👻 The ghost dissolves into the machine's background memory...              │", COLOR_BRIGHT_GREEN),
        ("│ Conduit closed. Your terminal is cleansed. Farewell, mortal.                │", COLOR_DIM_GREEN),
        ("└─────────────────────────────────────────────────────────────────────────────┘", COLOR_DIM_GREEN),
    ]

    # Storyboard sequence: (lines_to_show, duration_seconds)
    storyboard: list[tuple[list[tuple[str, tuple[int, int, int]]], float]] = [
        (s1, 6.0),
        (s2, 8.0),
        (s3, 11.0),
        (s4, 9.0),
        (s5, 6.0),
    ]

    base_frame = create_base_canvas()

    # Start ffmpeg pipe for MP4
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(mp4_path),
    ]

    proc = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    total_frames = int(sum(dur for _, dur in storyboard) * FPS)
    frame_count = 0

    for lines, duration in storyboard:
        scene_frames = int(duration * FPS)

        # Typing / rendering progression
        for i in range(scene_frames):
            frame = base_frame.copy()
            draw = ImageDraw.Draw(frame)

            # Determine visible lines for smooth entry
            progress = min(1.0, (i + 1) / (FPS * 1.5))
            visible_count = max(1, int(len(lines) * progress))
            current_lines = lines[:visible_count]

            y_offset = 60
            for line_text, color in current_lines:
                draw.text((30, y_offset), line_text, fill=color, font=font_main)
                y_offset += 24

            # Blinking cursor on last prompt line
            if (frame_count // (FPS // 2)) % 2 == 0 and y_offset < HEIGHT - 40:
                draw.rectangle([30, y_offset, 42, y_offset + 18], fill=COLOR_BRIGHT_GREEN)

            proc.stdin.write(frame.tobytes())
            frame_count += 1

    proc.stdin.close()
    proc.wait()
    print(f"[+] MP4 video generated at {mp4_path} ({frame_count} frames, ~{frame_count // FPS}s)")

    # Also generate an animated GIF for dev.to and GitHub embeds
    print("[*] Generating optimized animated GIF for web embedding...")
    gif_cmd = [
        "ffmpeg",
        "-y",
        "-ss", "0",
        "-t", "30",
        "-i", str(mp4_path),
        "-vf", "fps=12,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        "-loop", "0",
        str(gif_path),
    ]
    subprocess.run(gif_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    print(f"[+] Animated GIF generated at {gif_path}")


if __name__ == "__main__":
    main()
