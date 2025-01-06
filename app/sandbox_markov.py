import json
import os
import random

SANDBOX_LINES_FILE = "sandbox_lines.json"

def load_sandbox_lines() -> list[str]:
    if not os.path.exists(SANDBOX_LINES_FILE):
        return []
    with open(SANDBOX_LINES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sandbox_lines(lines: list[str]) -> None:
    with open(SANDBOX_LINES_FILE, "w", encoding="utf-8") as f:
        json.dump(lines, f, indent=2)

def add_sandbox_line(line: str) -> None:
    lines = load_sandbox_lines()
    lines.append(line)
    save_sandbox_lines(lines)

def generate_markov_line() -> str:
    """
    Very basic approach: random words from existing lines.
    The more data user inputs, the more variety we have.
    """
    lines = load_sandbox_lines()
    if not lines:
        return ""

    # Gather all words
    words = []
    for ln in lines:
        words.extend(ln.split())

    if len(words) < 3:
        return random.choice(lines)

    out = []
    for _ in range(random.randint(5, 12)):  # random length
        out.append(random.choice(words))
    return " ".join(out)