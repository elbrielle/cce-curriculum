#!/usr/bin/env python3
"""Check external source links used by all 36 Canvas week builders.

The checker fails only on confirmed 404/410 responses. Sites that reject
automated requests, time out, or return another unusual response are reported
for manual browser review rather than mislabeled as broken.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import re
import ssl
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[2]
CANVAS_DIR = Path(__file__).resolve().parent
BUILDERS = [
    *(CANVAS_DIR / f"build_wk{week}.py" for week in range(0, 6)),
    *(CANVAS_DIR / f"build_2sw_wk{week}.py" for week in range(1, 7)),
    *(CANVAS_DIR / f"build_3sw_wk{week}.py" for week in range(1, 7)),
    *(CANVAS_DIR / f"build_4sw_wk{week}.py" for week in range(1, 7)),
    *(CANVAS_DIR / f"build_5sw_wk{week}.py" for week in range(1, 7)),
    *(CANVAS_DIR / f"build_6sw_wk{week}.py" for week in range(1, 7)),
]
URL_PATTERN = re.compile(r"https://[^\s\"'<>]+")
USER_AGENT = "Mozilla/5.0 CCR-Canvas-Link-Check/1.0"


def source_urls() -> list[str]:
    return sorted(
        {
            match.rstrip(').,;"\'')
            for builder in BUILDERS
            for match in URL_PATTERN.findall(builder.read_text())
        }
    )


def check(url: str, timeout: float) -> tuple[str, int | str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(
            request, timeout=timeout, context=ssl.create_default_context()
        ) as response:
            return url, response.status, response.geturl()
    except urllib.error.HTTPError as exc:
        return url, exc.code, exc.geturl()
    except Exception as exc:  # network and TLS failures need manual review
        return url, "ERR", f"{type(exc).__name__}: {str(exc)[:160]}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    urls = source_urls()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(check, url, args.timeout) for url in urls]
        results = [future.result() for future in as_completed(futures)]

    stale: list[tuple[str, int | str, str]] = []
    review: list[tuple[str, int | str, str]] = []
    passed = 0
    for result in sorted(results):
        _, status, _ = result
        if isinstance(status, int) and 200 <= status < 400:
            passed += 1
        elif status in (404, 410):
            stale.append(result)
        else:
            review.append(result)

    for url, status, final in stale:
        print(f"STALE\t{status}\t{url}\t{final}")
    for url, status, final in review:
        print(f"REVIEW\t{status}\t{url}\t{final}")
    print(
        f"Checked {len(results)} links: {passed} reachable, "
        f"{len(stale)} stale, {len(review)} require manual review."
    )
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
