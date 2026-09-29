import re
import sys
from collections import defaultdict

FRAME_RE = re.compile(r'^\S+\s+(.*?)\s+\((.*)\)$')


def frame_name(line: str) -> str | None:
    m = FRAME_RE.match(line.strip())
    if not m:
        return None
    symbol, dso = m.groups()
    symbol = re.sub(r'\+0x[0-9a-fA-F]+$', '', symbol)
    if symbol == '[unknown]':
        return f'[{dso.rsplit("/", 1)[-1]}]'
    return symbol


def main() -> None:
    stacks: dict[str, int] = defaultdict(int)
    frames: list[str] = []

    def flush():
        if frames:
            stacks[';'.join(reversed(frames))] += 1
            frames.clear()

    for line in sys.stdin:
        if not line.strip():
            flush()
            continue
        if line[0] not in (' ', '\t'):
            continue  # sample header line (comm/pid/time/event)
        name = frame_name(line)
        if name:
            frames.append(name)
    flush()

    for stack, count in sorted(stacks.items()):
        print(f'{stack} {count}')


if __name__ == '__main__':
    main()
