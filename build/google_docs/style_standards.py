"""Style standards and layout specifications for CCE Google Docs worksheets.

Defines design tokens, typography rules, border treatments, callout styling,
and structured word-bank layouts to ensure Google Docs worksheets achieve
high visual quality and legibility rather than unstyled defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ColorPalette:
    # Primary Ink
    ink_primary: str = "#1f2937"       # Dark slate for body text (high contrast)
    ink_secondary: str = "#4b5563"     # Muted slate for subtext/meta
    ink_muted: str = "#6b7280"         # Captions and secondary notes
    
    # Brand Accents
    navy: str = "#004d7c"              # Primary Irving ISD brand navy
    navy_deep: str = "#002845"
    purple: str = "#5a2d91"            # Secondary student unit purple
    teal: str = "#1f617a"              # Academic / instructional teal
    green: str = "#4a9d2f"             # Success / Done-when green
    gold: str = "#f3c63c"              # Irving ISD accent gold
    
    # Surfaces & Tints
    surface_light: str = "#f8fafc"     # Neutral cool background for callouts
    surface_teal_tint: str = "#f0fdfa" # Soft teal container fill
    surface_purple_tint: str = "#faf8fd"# Soft purple container fill
    surface_green_tint: str = "#f2f8ef" # Soft green container fill
    surface_header: str = "#f1f5f9"    # Table header cell background
    
    # Subtle Borders (Never harsh #000000)
    border_subtle: str = "#cbd5e1"     # Standard table grid border
    border_card: str = "#e2e8f0"       # Callout card perimeter
    border_accent_navy: str = "#004d7c"
    border_accent_teal: str = "#1f617a"
    border_accent_purple: str = "#5a2d91"
    border_accent_green: str = "#4a9d2f"


@dataclass(frozen=True)
class TypographyTokens:
    font_family_primary: str = "Source Sans Pro"  # Clean, accessible sans
    font_family_fallback: str = "Arial"
    
    size_h1: float = 16.0              # Document title
    size_h2: float = 13.0              # Section headings
    size_h3: float = 11.5              # Subheadings
    size_body: float = 10.5            # Main body / instructions
    size_table: float = 10.0           # Inside table cells
    size_meta: float = 9.0             # Name/Date/Period headers
    size_scaffold: float = 9.5         # Word bank terms and sentence stems
    
    line_spacing_body: float = 1.3
    line_spacing_tight: float = 1.15


@dataclass(frozen=True)
class TableSpecs:
    border_width_pt: float = 0.5       # Subtle, crisp grid line
    cell_padding_top_pt: float = 6.0
    cell_padding_bottom_pt: float = 6.0
    cell_padding_left_pt: float = 8.0
    cell_padding_right_pt: float = 8.0
    header_background: str = "#f1f5f9"
    header_text_color: str = "#0f172a"
    response_min_height_lines: int = 2


PALETTE = ColorPalette()
TYPOGRAPHY = TypographyTokens()
TABLES = TableSpecs()


def format_word_bank_categorized(
    items: list[str],
    *,
    columns: int = 2,
    categories: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Structure a word bank into clean columns or categorized groups.
    
    Avoids joining terms into an unreadable inline paragraph with bullets.
    """
    if categories:
        return {
            "type": "categorized_word_bank",
            "categories": [
                {
                    "title": cat_name,
                    "items": [item for item in cat_items],
                }
                for cat_name, cat_items in categories.items()
            ],
        }
    
    # Multi-column grid distribution
    col_lists: list[list[str]] = [[] for _ in range(columns)]
    for i, item in enumerate(items):
        col_lists[i % columns].append(item)
        
    return {
        "type": "columnar_word_bank",
        "columns": col_lists,
    }


def format_sentence_stems(stems: list[str]) -> list[dict[str, str]]:
    """Split and cleanly format bilingual sentence stems."""
    formatted: list[dict[str, str]] = []
    for stem in stems:
        if " / " in stem:
            en, es = stem.split(" / ", 1)
            formatted.append({
                "english": en.strip(),
                "spanish": es.strip(),
            })
        else:
            formatted.append({
                "english": stem.strip(),
                "spanish": "",
            })
    return formatted
