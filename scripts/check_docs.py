"""Check repository-local file targets in ordinary Markdown inline links."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK = re.compile(r'!?\[[^\]\n]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+"[^"]*")?\)')
TICK = chr(96)
INLINE_CODE = re.compile(TICK + r"+[^" + TICK + r"]*" + TICK + r"+")
IGNORED = {".git", ".venv", "node_modules", "__pycache__"}


def iter_links(content: str):
    fence = None
    for number, line in enumerate(content.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith((TICK * 3, "~~~")):
            marker = stripped[0]
            length = len(stripped) - len(stripped.lstrip(marker))
            if fence is None:
                fence = (marker, length)
            elif marker == fence[0] and length >= fence[1]:
                fence = None
            continue
        if fence is not None:
            continue
        line = INLINE_CODE.sub("", line)
        for match in LINK.finditer(line):
            yield number, match.group(1) or match.group(2)


def check(root: Path) -> tuple[list[str], int, int]:
    root = root.resolve()
    errors = []
    files = 0
    local_links = 0
    for document in sorted(root.rglob("*.md")):
        if any(part in IGNORED for part in document.relative_to(root).parts):
            continue
        files += 1
        for number, destination in iter_links(document.read_text(encoding="utf-8")):
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            local_links += 1
            target = unquote(parsed.path)
            resolved = (root / target.lstrip("/") if target.startswith("/")
                        else document.parent / target).resolve()
            label = f"{document.relative_to(root).as_posix()}:{number}"
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"{label}: target leaves repository: {destination}")
                continue
            if not resolved.exists():
                errors.append(f"{label}: missing local target: {destination}")
    return errors, files, local_links


def main() -> int:
    errors, files, links = check(Path(__file__).resolve().parents[1])
    for error in errors:
        print(error)
    print(f"Checked {files} Markdown files and {links} local file links; "
          f"{len(errors)} errors. External URLs and anchors are not checked.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
