#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Termux Banner Maker PRO — CYBER SOHAG
=======================================
Run:  python banner.py

PRO features (all menus in English):
  1. Name / banner text — each word on its own line (like CYBER / SOHAG)
  2. Welcome box on top (e.g. < Welcome To Termux! >)
  3. ASCII art logo — Skull / Phoenix / Crown / None
  4. 10 stylish pyfiglet fonts (3D, Isometric, Doom, Ghost, Slant...)
  5. 7 professional themes with TRUE GRADIENT colours
     (FIRE like the screenshot, Ocean, Matrix, Neon, Gold, Blood, Rainbow)
  6. Loading system — animated loading bar every time Termux opens,
     then the banner appears
  7. Optional stylish prompt (e.g. CYBER SOHAG@localhost ~ >>>)
  8. Live preview before saving, one-command remove

How it works:
  banner.py saves ~/.custom_banner.txt (the art) and ~/.show_banner.py
  (the loader) and adds one block to ~/.bashrc. Every time Termux opens,
  the loader plays the loading bar and then shows your banner.
  Re-running banner.py replaces the old banner automatically.
  pyfiglet is auto-installed on first run if missing.
"""

import os
import subprocess
import sys
import time

# ---------------------------------------------------------------- colours
RESET = "\033[0m"
BOLD = "\033[1m"

# ------------------------------------------------------------------ paths
HOME = os.path.expanduser("~")
BANNER_FILE = os.path.join(HOME, ".custom_banner.txt")
LOADER_FILE = os.path.join(HOME, ".show_banner.py")
BASHRC = os.path.join(HOME, ".bashrc")

OLD_START = "# === CUSTOM TERMUX BANNER (by banner.py) ==="
OLD_END = "# === END CUSTOM TERMUX BANNER ==="
MARK_START = "# === CYBER SOHAG BANNER v2 ==="
MARK_END = "# === END CYBER SOHAG BANNER v2 ==="
PROMPT_START = "# === CYBER SOHAG BANNER PROMPT ==="
PROMPT_END = "# === END CYBER SOHAG BANNER PROMPT ==="

# ------------------------------------------------------------------ fonts
FONTS = {
    "1": ("3D", "3-d"),
    "2": ("3D Isometric", "isometric1"),
    "3": ("Big Bold", "big"),
    "4": ("Slant Stylish", "slant"),
    "5": ("Doom", "doom"),
    "6": ("Ghost", "ghost"),
    "7": ("Classic", "standard"),
    "8": ("Lean", "lean"),
    "9": ("Digital", "digital"),
    "10": ("Bubble", "bubble"),
}

# ------------------------------------------------------- themes (RGB stops)
# gradient: list of RGB stops (left -> right), accent: welcome/tagline colour
THEMES = {
    "1": ("FIRE (like the screenshot)", [(57, 255, 20), (255, 235, 0),
                                          (255, 140, 0), (255, 45, 85)],
         (0, 229, 255)),
    "2": ("OCEAN", [(0, 229, 255), (0, 140, 255), (120, 80, 255)],
         (0, 255, 170)),
    "3": ("MATRIX", [(0, 255, 65), (0, 200, 60), (180, 255, 0)],
         (120, 255, 120)),
    "4": ("NEON", [(255, 0, 200), (150, 0, 255), (0, 220, 255)],
         (0, 255, 200)),
    "5": ("GOLD", [(255, 240, 150), (255, 200, 0), (255, 140, 0)],
         (255, 220, 120)),
    "6": ("BLOOD", [(255, 90, 90), (200, 0, 0), (120, 0, 20)],
         (255, 120, 120)),
    "7": ("RAINBOW", [(255, 0, 0), (255, 150, 0), (255, 240, 0),
                      (0, 220, 0), (0, 150, 255), (160, 0, 255)],
         (255, 255, 255)),
}

# -------------------------------------------------------------- ascii art
SKULL = r"""
        ______
     .-"      "-.
    /            \
   |              |
   |,  .-.  .-.  ,|
   | )(__/  \__)( |
   |/     /\     \|
   (_     ^^     _)
    \__|IIII|__/
     | \IIII/ |
     \        /
      `--------`
""".strip("\n")

PHOENIX = r"""
          _
         / \
        |   |
     _  |   |  _
    / \ |   | / \
   |   \|   |/   |
    \   |   |   /
     \  |   |  /
      \ |   | /
       \|   |/
        |   |
       /|   |\
      / |   | \
     /  |   |  \
    /   |   |   \
""".strip("\n")

CROWN = r"""
   *     *     *
   |     |     |
  \|/   \|/   \|/
   |     |     |
   |   __|__   |
   |  /  |  \  |
    \/   |   \/
    |    |    |
    |____|____|
""".strip("\n")

ARTS = {
    "1": ("Skull", SKULL),
    "2": ("Phoenix", PHOENIX),
    "3": ("Crown", CROWN),
    "4": ("None", ""),
}

# ---------------------------------------------------------------- helpers
def ask(prompt, default=""):
    try:
        value = input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        sys.exit(0)
    return value if value else default


def choose(prompt, options, default="1"):
    while True:
        value = ask(prompt, default)
        if value in options:
            return value
        print("Invalid number! Try again.\n")


def rgb(code):
    return "\033[38;2;{};{};{}m".format(*code)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient_at(stops, t):
    """Colour at position t (0.0 - 1.0) along the gradient stops."""
    if len(stops) == 1:
        return stops[0]
    t = max(0.0, min(1.0, t))
    seg = t * (len(stops) - 1)
    i = min(int(seg), len(stops) - 2)
    return lerp(stops[i], stops[i + 1], seg - i)


def apply_gradient_horizontal(text, stops, bold=True):
    """Left-to-right gradient, per line (like the screenshot)."""
    prefix = BOLD if bold else ""
    out_lines = []
    for line in text.split("\n"):
        width = max(1, len(line) - 1)
        coloured = ""
        for x, ch in enumerate(line):
            if ch == " ":
                coloured += " "
            else:
                coloured += rgb(gradient_at(stops, x / width)) + ch
        out_lines.append(coloured)
    return prefix + "\n".join(out_lines) + RESET


def apply_gradient_vertical(text, stops, bold=True):
    """Top-to-bottom gradient (for the ASCII art logo)."""
    prefix = BOLD if bold else ""
    lines = text.split("\n")
    total = max(1, len(lines) - 1)
    out_lines = []
    for y, line in enumerate(lines):
        colour = rgb(gradient_at(stops, y / total))
        out_lines.append("".join(colour + ch if ch != " " else " "
                                 for ch in line))
    return prefix + "\n".join(out_lines) + RESET


def loading_bar(message, duration=1.0, steps=20):
    """Animated loading bar used while generating the banner."""
    for i in range(steps + 1):
        pct = int(i * 100 / steps)
        filled = int(30 * i / steps)
        bar = "█" * filled + "░" * (30 - filled)
        sys.stdout.write("\r{} [{}] {}%".format(message, bar, pct))
        sys.stdout.flush()
        time.sleep(duration / steps)
    print()


def ensure_pyfiglet():
    try:
        import pyfiglet  # noqa: F401
        return True
    except ImportError:
        print("[*] pyfiglet not found, installing... (takes a moment)")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", "pyfiglet"])
            import pyfiglet  # noqa: F401
            print("[OK] pyfiglet installed!\n")
            return True
        except Exception:
            print("[!] Could not install pyfiglet — using simple text mode.\n")
            return False


def render_name(name, font, has_figlet):
    """Render each word of the name on its own line (CYBER / SOHAG)."""
    words = name.split() or ["SOHAG"]
    if not has_figlet:
        width = max(len(w) for w in words) + 6
        border = "+" + "-" * width + "+"
        lines = [border]
        for w in words:
            lines.append("|" + w.center(width) + "|")
        lines.append(border)
        return "\n".join(lines)
    from pyfiglet import Figlet
    blocks = []
    for word in words:
        try:
            blocks.append(Figlet(font=font).renderText(word).rstrip("\n"))
        except Exception:
            blocks.append(Figlet(font="standard").renderText(word).rstrip("\n"))
    return "\n".join(blocks)


def make_welcome_box(text, accent):
    """< Welcome To Termux! > box, like the screenshot."""
    inner = "< {} >".format(text)
    width = len(inner) + 2
    line = "-" * width
    return "{}{}{}\n  {}\n{}".format(rgb(accent), line, RESET, inner, line)


def make_loader(name, accent):
    """The startup loader script — loading bar, then the banner."""
    return '''#!/usr/bin/env python3
"""Termux banner loader — generated by banner.py (do not edit by hand)."""
import os
import sys
import time

BANNER = os.path.expanduser("~/.custom_banner.txt")
NAME = {name!r}
ACCENT = {accent!r}


def _rgb(c):
    return "\\033[38;2;{{}};{{}};{{}}m".format(*c)


def main():
    try:
        with open(BANNER, encoding="utf-8") as f:
            art = f.read()
    except OSError:
        return
    for p in range(0, 101, 4):
        filled = int(30 * p / 100)
        bar = "\\u2588" * filled + "-" * (30 - filled)
        sys.stdout.write(
            "\\r\\033[1m" + _rgb(ACCENT) +
            "Loading " + NAME + "... [" + bar + "] " +
            str(p) + "%\\033[0m")
        sys.stdout.flush()
        time.sleep(0.03)
    print()
    os.system("clear")
    sys.stdout.write(art)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
'''.format(name=name, accent=accent)


def strip_block(lines, start, end):
    """Remove a marked block (start..end lines) from bashrc lines."""
    kept, skipping = [], False
    for line in lines:
        if start in line:
            skipping = True
            continue
        if end in line:
            skipping = False
            continue
        if not skipping:
            kept.append(line)
    return kept


def install_to_bashrc(prompt_name):
    """Install the v2 loader block (+ optional stylish prompt), once only."""
    existing = ""
    if os.path.exists(BASHRC):
        with open(BASHRC, "r", encoding="utf-8", errors="ignore") as f:
            existing = f.read()
    lines = existing.splitlines(keepends=True)
    # remove any old v1 block, old v2 block and old prompt block first
    lines = strip_block(lines, OLD_START, OLD_END)
    lines = strip_block(lines, MARK_START, MARK_END)
    lines = strip_block(lines, PROMPT_START, PROMPT_END)

    block = (
        MARK_START + "\n"
        "if [ -f ~/.show_banner.py ]; then\n"
        "  python ~/.show_banner.py\n"
        "elif [ -f ~/.custom_banner.txt ]; then\n"
        "  clear\n"
        "  cat ~/.custom_banner.txt\n"
        "fi\n" + MARK_END + "\n"
    )
    if prompt_name:
        ps1 = (
            "PS1='\\[\\033[1;95m\\]{}"
            "\\[\\033[0m\\]@\\[\\033[1;91mlocalhost\\[\\033[0m\\] "
            "\\w \\[\\033[1;91m\\]>>>\\[\\033[0m\\] '\n"
        ).format(prompt_name)
        block += PROMPT_START + "\n" + ps1 + PROMPT_END + "\n"

    text = "".join(lines)
    with open(BASHRC, "w", encoding="utf-8") as f:
        f.write(text)
        if text and not text.endswith("\n"):
            f.write("\n")
        f.write(block)
    return True


def remove_banner():
    removed = False
    for path in (BANNER_FILE, LOADER_FILE):
        if os.path.exists(path):
            os.remove(path)
            removed = True
    if os.path.exists(BASHRC):
        with open(BASHRC, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines(keepends=True)
        lines = strip_block(lines, OLD_START, OLD_END)
        lines = strip_block(lines, MARK_START, MARK_END)
        lines = strip_block(lines, PROMPT_START, PROMPT_END)
        with open(BASHRC, "w", encoding="utf-8") as f:
            f.writelines(lines)
    print("Banner removed. It will not show when Termux opens again."
          if removed else "No banner was installed.")


def create_banner():
    print("\n========== CREATE NEW BANNER ==========\n")
    has_figlet = ensure_pyfiglet()

    name = ask("Enter your name / banner text (e.g. CYBER SOHAG): ",
               "CYBER SOHAG")
    welcome = ask("Welcome message (e.g. Welcome To Termux!) "
                  "- leave empty to skip: ", "Welcome To Termux!")
    tagline = ask("Tagline (e.g. EXPERT CYBER SECURITY ZONE) "
                  "- leave empty to skip: ", "")

    print("\n--- ASCII ART LOGO ---")
    for key, (label, _art) in ARTS.items():
        print("   [{}] {}".format(key, label))
    art_key = choose("\nChoose art (1-4): ", ARTS, "1")

    print("\n--- FONT (stylish) ---")
    for key, (label, _font) in FONTS.items():
        print("   [{}] {}".format(key, label))
    font_key = choose("\nChoose font (1-10): ", FONTS, "1")

    print("\n--- THEME (gradient colours) ---")
    for key, (label, _stops, _accent) in THEMES.items():
        print("   [{}] {}".format(key, label))
    theme_key = choose("\nChoose theme (1-7): ", THEMES, "1")

    print("\n--- STYLE ---")
    print("   [1] Bold")
    print("   [2] Normal")
    style_key = choose("Choose style (1-2): ", {"1": None, "2": None}, "1")
    bold = style_key == "1"

    use_prompt = ask("\nSet stylish prompt like "
                     "{}@localhost ~ >>> ? (y/n): ".format(name),
                     "y").lower() in ("y", "yes")

    _label, stops, accent = THEMES[theme_key]
    _flabel, font = FONTS[font_key]
    _alabel, art = ARTS[art_key]

    loading_bar("Generating your banner", duration=0.8)

    parts = []
    if welcome:
        parts.append(make_welcome_box(welcome, accent))
    if art:
        parts.append(apply_gradient_vertical(art, stops, bold))
    parts.append(apply_gradient_horizontal(render_name(name, font, has_figlet),
                                           stops, bold))
    if tagline:
        parts.append(BOLD + rgb(accent) + tagline.center(50) + RESET)
    banner = "\n".join(parts)

    print("\n========== PREVIEW ==========")
    print(banner)
    print("=============================\n")

    confirm = ask("Save this banner? (y/n): ", "y").lower()
    if confirm not in ("y", "yes"):
        print("Not saved. Run again to make a new one.")
        return

    with open(BANNER_FILE, "w", encoding="utf-8") as f:
        f.write(banner + "\n")
    with open(LOADER_FILE, "w", encoding="utf-8") as f:
        f.write(make_loader(name, accent))

    install_to_bashrc(name if use_prompt else "")

    print("\nDone! Exit Termux and open it again —")
    print("the loading bar will play, then your banner appears.")
    print("\n(Banner file: {})".format(BANNER_FILE))


def main():
    print("=" * 44)
    print("   TERMUX BANNER MAKER  PRO")
    print("   by CYBER SOHAG")
    print("=" * 44)
    print("\n[1] Create New Banner")
    print("[2] Remove Banner")
    print("[3] Exit")
    choice = choose("\nWhat do you want to do? (1-3): ",
                    {"1": None, "2": None, "3": None}, "1")
    if choice == "1":
        create_banner()
    elif choice == "2":
        remove_banner()
    else:
        print("Bye!")


if __name__ == "__main__":
    main()
