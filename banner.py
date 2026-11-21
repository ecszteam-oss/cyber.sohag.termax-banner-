#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Termux Custom Banner Maker — CYBER SOHAG
=========================================
Run:  python banner.py

যা যা করবে:
  1. নাম চাইবে (যেমন: SOHAG)
  2. ট্যাগলাইন চাইবে (যেমন: EXPERT CYBER SECURITY ZONE) — খালি রাখলে বাদ যাবে
  3. ডিজাইন বাছতে দেবে — 3D, Isometric, Big, Slant, Bubble, Digital, Simple Box
  4. কালার বাছতে দেবে — লাল, সবুজ, হলুদ, নীল, বেগুনি, সায়ান, সাদা, কমলা, রেইনবো, র‍্যান্ডম
  5. স্টাইল বাছতে দেবে — Bold / Normal
  6. প্রিভিউ দেখাবে, OK করলে সেভ করবে
  7. Termux খুললেই ব্যানার দেখাবে — ~/.bashrc-তে অটো বসিয়ে দেবে

প্রথমবার চালালে pyfiglet না থাকলে নিজেই pip দিয়ে ইনস্টল করে নেবে।
ইনস্টল না হলে Simple Box ডিজাইন দিয়ে কাজ চালাবে।
"""

import os
import random
import subprocess
import sys

# ---------- রং (ANSI) ----------
RESET = "\033[0m"
BOLD = "\033[1m"

COLORS = {
    "1": ("লাল (Red)", "\033[91m"),
    "2": ("সবুজ (Green)", "\033[92m"),
    "3": ("হলুদ (Yellow)", "\033[93m"),
    "4": ("নীল (Blue)", "\033[94m"),
    "5": ("বেগুনি (Magenta/Purple)", "\033[95m"),
    "6": ("সায়ান (Cyan)", "\033[96m"),
    "7": ("সাদা (White)", "\033[97m"),
    "8": ("কমলা (Orange)", "\033[38;5;208m"),
}

RAINBOW_CODES = [
    "\033[91m", "\033[93m", "\033[92m",
    "\033[96m", "\033[94m", "\033[95m",
]

# ---------- ডিজাইন (pyfiglet font) ----------
DESIGNS = {
    "1": ("3D ডিজাইন", "3-d"),
    "2": ("3D Isometric ডিজাইন", "isometric1"),
    "3": ("Big বোল্ড ডিজাইন", "big"),
    "4": ("Slant স্টাইলিশ ডিজাইন", "slant"),
    "5": ("Bubble ডিজাইন", "bubble"),
    "6": ("Digital ডিজাইন", "digital"),
    "7": ("Simple Box ডিজাইন (বর্ডার সহ)", "box"),
}

BANNER_FILE = os.path.expanduser("~/.custom_banner.txt")
BASHRC = os.path.expanduser("~/.bashrc")
MARK_START = "# === CUSTOM TERMUX BANNER (by banner.py) ==="
MARK_END = "# === END CUSTOM TERMUX BANNER ==="


def ask(prompt, default=""):
    """ইনপুট নেওয়া — খালি দিলে default ফেরত দেবে।"""
    try:
        value = input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nবন্ধ করা হলো।")
        sys.exit(0)
    return value if value else default


def choose(prompt, options, default="1"):
    """নম্বর দিয়ে অপশন বাছা — ভুল নম্বর দিলে আবার চাইবে।"""
    while True:
        value = ask(prompt, default)
        if value in options:
            return value
        print("❌ ভুল নম্বর! আবার দাও।\n")


def ensure_pyfiglet():
    """pyfiglet আছে কি না দেখবে, না থাকলে ইনস্টল করার চেষ্টা করবে।"""
    try:
        import pyfiglet  # noqa: F401
        return True
    except ImportError:
        print("[*] pyfiglet পাওয়া যায়নি, ইনস্টল করা হচ্ছে... (একটু সময় লাগবে)")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", "pyfiglet"]
            )
            import pyfiglet  # noqa: F401
            print("[✓] pyfiglet ইনস্টল হয়ে গেছে!\n")
            return True
        except Exception:
            print("[!] pyfiglet ইনস্টল করা গেল না — Simple Box ডিজাইন দিয়ে চলবে।\n")
            return False


def make_box_text(name, tagline):
    """pyfiglet ছাড়া চলার Simple Box ডিজাইন।"""
    width = max(len(name), len(tagline)) + 8
    border = "+" + "-" * width + "+"
    lines = [border]
    lines.append("|" + name.center(width) + "|")
    if tagline:
        lines.append("|" + tagline.center(width) + "|")
    lines.append(border)
    return "\n".join(lines)


def render_banner(name, tagline, design_key, has_figlet):
    """নাম + ট্যাগলাইন থেকে ব্যানার টেক্সট বানাবে (রং ছাড়া)।"""
    design_name, font = DESIGNS[design_key]
    if font == "box" or not has_figlet:
        art = make_box_text(name, tagline)
    else:
        from pyfiglet import Figlet
        try:
            art = Figlet(font=font).renderText(name)
        except Exception:
            # ফন্ট না পেলে standard দিয়ে চালাবে
            art = Figlet(font="standard").renderText(name)
        if tagline:
            art = art.rstrip("\n") + "\n" + tagline.center(50) + "\n"
    return art.rstrip("\n")


def apply_color(art, color_key, bold):
    """ব্যানারে রং + Bold লাগাবে।"""
    prefix = BOLD if bold else ""
    if color_key == "9":  # রেইনবো — প্রতি অক্ষরে আলাদা রং
        out_lines = []
        for line in art.split("\n"):
            coloured = ""
            ci = 0
            for ch in line:
                if ch == " ":
                    coloured += " "
                else:
                    coloured += RAINBOW_CODES[ci % len(RAINBOW_CODES)] + ch
                    ci += 1
            out_lines.append(coloured)
        return prefix + ("\n".join(out_lines)) + RESET
    if color_key == "10":  # র‍্যান্ডম
        code = random.choice(list(COLORS.values()))[1]
        return prefix + code + art + RESET
    code = COLORS[color_key][1]
    return prefix + code + art + RESET


def install_to_bashrc():
    """~/.bashrc-তে ব্যানার চালানোর লাইন বসাবে (একবারই বসবে)।"""
    block = (
        MARK_START + "\n"
        "if [ -f ~/.custom_banner.txt ]; then\n"
        "  clear\n"
        "  cat ~/.custom_banner.txt\n"
        "fi\n" + MARK_END + "\n"
    )
    existing = ""
    if os.path.exists(BASHRC):
        with open(BASHRC, "r", encoding="utf-8", errors="ignore") as f:
            existing = f.read()
    if MARK_START in existing:
        return False  # আগেই বসানো আছে
    with open(BASHRC, "a", encoding="utf-8") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write(block)
    return True


def remove_banner():
    """ব্যানার ফাইল + bashrc-র লাইন মুছে ফেলবে।"""
    removed = False
    if os.path.exists(BANNER_FILE):
        os.remove(BANNER_FILE)
        removed = True
    if os.path.exists(BASHRC):
        with open(BASHRC, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines(keepends=True)
        kept, skipping = [], False
        for line in lines:
            if MARK_START in line:
                skipping = True
                continue
            if MARK_END in line:
                skipping = False
                continue
            if not skipping:
                kept.append(line)
        with open(BASHRC, "w", encoding="utf-8") as f:
            f.writelines(kept)
    print("✓ ব্যানার মুছে ফেলা হয়েছে। Termux আবার খুললে আর ব্যানার আসবে না।"
          if removed else "কোনো ব্যানার বসানো ছিল না।")


def create_banner():
    """নতুন ব্যানার বানানোর পুরো ফ্লো।"""
    print("\n========== নতুন কাস্টম ব্যানার ==========\n")
    has_figlet = ensure_pyfiglet()

    name = ask("👤 তোমার নাম / ব্যানারের লেখা দাও (যেমন: SOHAG): ", "SOHAG")
    tagline = ask("✍️ ট্যাগলাইন দাও (যেমন: EXPERT CYBER SECURITY ZONE) — খালি রাখলে বাদ যাবে: ")

    print("\n🎨 ডিজাইন বাছো:")
    for key, (label, _font) in DESIGNS.items():
        print(f"   [{key}] {label}")
    design_key = choose("\nডিজাইনের নম্বর দাও (1-7): ", DESIGNS, "1")

    print("\n🌈 কালার বাছো:")
    for key, (label, _code) in COLORS.items():
        print(f"   [{key}] {label}")
    print("   [9] রেইনবো (সব রং মেশানো)")
    print("   [10] র‍্যান্ডম")
    color_key = choose("\nকালারের নম্বর দাও (1-10): ",
                       {**COLORS, "9": None, "10": None}, "1")

    print("\n✨ স্টাইল বাছো:")
    print("   [1] Bold (মোটা)")
    print("   [2] Normal (সাধারণ)")
    style_key = choose("স্টাইলের নম্বর দাও (1-2): ", {"1": None, "2": None}, "1")

    art = render_banner(name, tagline, design_key, has_figlet)
    banner = apply_color(art, color_key, style_key == "1")

    print("\n========== প্রিভিউ ==========")
    print(banner)
    print("=============================\n")

    confirm = ask("এই ব্যানারটা সেভ করবো? (y/n): ", "y").lower()
    if confirm not in ("y", "yes", "হ্যাঁ"):
        print("❌ সেভ করা হয়নি। আবার চালিয়ে নতুন করে বানাও।")
        return

    with open(BANNER_FILE, "w", encoding="utf-8") as f:
        f.write(banner + "\n")

    if install_to_bashrc():
        print("✓ ~/.bashrc-তে ব্যানার বসিয়ে দেওয়া হয়েছে।")
    else:
        print("✓ ~/.bashrc-তে ব্যানার আগেই বসানো ছিল।")

    print("\n🎉 হয়ে গেছে! এখন Termux exit করে আবার খুললেই")
    print("   তোমার কাস্টম ব্যানারটা দেখাবে।")
    print(f"\n(ব্যানার ফাইল: {BANNER_FILE})")


def main():
    print("=" * 44)
    print("   TERMUX CUSTOM BANNER MAKER")
    print("   by CYBER SOHAG")
    print("=" * 44)
    print("\n[1] নতুন ব্যানার বানাও")
    print("[2] ব্যানার মুছে ফেলো")
    print("[3] বের হও")
    choice = choose("\nকী করবে? নম্বর দাও (1-3): ",
                    {"1": None, "2": None, "3": None}, "1")
    if choice == "1":
        create_banner()
    elif choice == "2":
        remove_banner()
    else:
        print("বাই! 👋")


if __name__ == "__main__":
    main()
