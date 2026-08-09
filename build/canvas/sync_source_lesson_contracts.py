#!/usr/bin/env python3
"""Synchronize the explicit daily contract into all 180 Markdown backups."""

from __future__ import annotations

import re

from lesson_contracts import load_contracts


START = "<!-- CCE DAILY CONTRACT START -->"
END = "<!-- CCE DAILY CONTRACT END -->"
BLOCK_RE = re.compile(rf"\n?{re.escape(START)}.*?{re.escape(END)}\n?", re.S)


def block(topic: str, objective: str, teks: str, dol: str) -> str:
    return (
        f"\n{START}\n"
        "## Daily Learning Contract\n\n"
        f"- **Topic:** {topic}\n"
        f"- **Objective:** {objective}\n"
        f"- **TEKS:** {teks}\n"
        f"- **Demonstration of Learning:** {dol}\n"
        f"{END}\n"
    )


def main() -> None:
    changed = 0
    for contract in load_contracts():
        text = contract.source.read_text(encoding="utf-8")
        text = BLOCK_RE.sub("\n", text, count=1)
        heading = re.search(r"^#\s+.+?$", text, re.MULTILINE)
        if not heading:
            raise ValueError(contract.source)
        new = (
            text[: heading.end()]
            + block(contract.topic, contract.objective, contract.teks, contract.dol)
            + text[heading.end() :].lstrip("\n")
        )
        if new != contract.source.read_text(encoding="utf-8"):
            contract.source.write_text(new, encoding="utf-8")
            changed += 1
    print(f"contracts=180 files_changed={changed}")


if __name__ == "__main__":
    main()
