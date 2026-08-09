#!/usr/bin/env python3
"""Report oversized local Canvas-only raster assets without modifying them."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ASSET_ROOT = ROOT / "cce-curriculum/resources/canvas-licensed"
EXTENSIONS = {".jpg", ".jpeg", ".png"}
JPEG_SOF = {
    0xC0,
    0xC1,
    0xC2,
    0xC3,
    0xC5,
    0xC6,
    0xC7,
    0xC9,
    0xCA,
    0xCB,
    0xCD,
    0xCE,
    0xCF,
}


def image_dimensions(path: Path) -> tuple[int, int] | None:
    """Read PNG/JPEG dimensions with the standard library."""
    with path.open("rb") as handle:
        signature = handle.read(24)
        if signature.startswith(b"\x89PNG\r\n\x1a\n") and len(signature) >= 24:
            return struct.unpack(">II", signature[16:24])
        if not signature.startswith(b"\xff\xd8"):
            return None

        handle.seek(2)
        while True:
            byte = handle.read(1)
            if not byte:
                return None
            if byte != b"\xff":
                continue
            while byte == b"\xff":
                byte = handle.read(1)
            if not byte:
                return None
            marker = byte[0]
            if marker in {0xD8, 0xD9}:
                continue
            length_bytes = handle.read(2)
            if len(length_bytes) != 2:
                return None
            segment_length = struct.unpack(">H", length_bytes)[0]
            if segment_length < 2:
                return None
            if marker in JPEG_SOF:
                data = handle.read(5)
                if len(data) != 5:
                    return None
                height, width = struct.unpack(">HH", data[1:5])
                return width, height
            handle.seek(segment_length - 2, 1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inventory large Canvas-only PNG/JPEG assets without changing files."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ASSET_ROOT)
    parser.add_argument("--warn-kb", type=int, default=500)
    parser.add_argument("--top", type=int, default=30)
    args = parser.parse_args()

    asset_root = args.root.resolve()
    if not asset_root.is_dir():
        raise SystemExit(f"Asset root does not exist: {asset_root}")

    records: list[tuple[int, Path, tuple[int, int] | None]] = []
    for path in asset_root.rglob("*"):
        if path.is_file() and path.suffix.lower() in EXTENSIONS:
            records.append((path.stat().st_size, path, image_dimensions(path)))
    records.sort(reverse=True, key=lambda row: row[0])

    threshold = args.warn_kb * 1024
    oversized = [row for row in records if row[0] > threshold]
    total_bytes = sum(row[0] for row in records)
    print(
        f"Canvas-only rasters: {len(records)} files, {total_bytes / 1048576:.1f} MB; "
        f"{len(oversized)} exceed {args.warn_kb} KB."
    )
    print("size_kb\tdimensions\tpath")
    for size, path, dimensions in records[: args.top]:
        dimension_text = f"{dimensions[0]}x{dimensions[1]}" if dimensions else "unknown"
        print(f"{size / 1024:.1f}\t{dimension_text}\t{path.relative_to(ROOT)}")

    if oversized:
        print(
            "Review oversized files individually at desktop and 390px viewport widths; "
            "do not replace the licensed source original or apply blind batch compression."
        )


if __name__ == "__main__":
    main()
