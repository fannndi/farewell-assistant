"""Measure instruction files loaded by OpenCode every turn."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

files = [
    ("rules.md", ROOT / "instructions" / "rules.md"),
    ("farewell-assistant.md", ROOT / ".farewell" / "context" / "farewell-assistant.md"),
    ("context.md", ROOT / ".opencode" / "context.md"),
    ("work-mode.json", ROOT / ".opencode" / "work-mode.json"),
]

def count(path):
    if not path.exists(): return 0, 0, 0
    text = path.read_text(encoding="utf-8")
    lines = len(text.splitlines())
    chars = len(text)
    tokens = sum(0.25 if ord(c) < 128 else 1 for c in text)
    return lines, chars, int(tokens)

total_l = total_c = total_t = 0
print(f"{'File':45s} {'Lines':>6s} {'Chars':>7s} {'Tokens':>6s}")
print("=" * 66)
for name, path in files:
    l, c, t = count(path)
    total_l += l; total_c += c; total_t += t
    print(f"{name:45s} {l:6d} {c:7d} {t:6d}")
print("=" * 66)
print(f"{'TOTAL (loaded every turn)':45s} {total_l:6d} {total_c:7d} {total_t:6d}")
print(f"\nPer 50 turns: ~{total_t * 50:,} tokens loaded as instructions")
