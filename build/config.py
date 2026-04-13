"""Shared styles, colors, fonts, and page setup for the CCE build scripts."""

from docx.shared import Pt, Inches, Emu, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ── Page setup ──
PAGE_MARGIN = Inches(0.75)  # 1080 DXA

# ── Font ──
FONT_NAME = "Arial"

# ── Colors ──
NAVY       = RGBColor(0x1B, 0x2A, 0x4A)
BLUE       = RGBColor(0x2E, 0x75, 0xB6)
GRAY_TITLE = RGBColor(0x66, 0x66, 0x66)
GRAY_SUB   = RGBColor(0x55, 0x55, 0x55)
GREEN_TEXT  = RGBColor(0x2E, 0x7D, 0x32)
RED_TEXT    = RGBColor(0xD8, 0x43, 0x15)
ORANGE_TEXT = RGBColor(0xE6, 0x51, 0x00)
PURPLE_TEXT = RGBColor(0x70, 0x30, 0xA0)
PURPLE_EDP  = RGBColor(0x7B, 0x1F, 0xA2)
PURPLE_EDYN = RGBColor(0x6A, 0x1B, 0x9A)

# ── Background fill hex strings (for paragraph shading) ──
BG_LIGHT_BLUE   = "E8F0FE"   # H&L platform callouts
BG_YELLOW       = "FFF8E1"   # warm-ups
BG_GREEN        = "E8F5E9"   # exit tickets, "I can" statements
BG_ORANGE       = "FFF3E0"   # [VERIFY IN H&L]
BG_LIGHT_PURPLE = "F3E5F5"   # [VERIFY IN eDynamic]

# ── Font sizes (in Pt) ──
SIZE_HEADER_TOP  = Pt(10)    # "Career and College Explorations" top line
SIZE_HEADER_SUB  = Pt(9)     # "Facilitator Guide" / "1st Six Weeks | Week 0"
SIZE_TITLE       = Pt(16)    # main title
SIZE_SUBTITLE    = Pt(11)    # subtitle
SIZE_SECTION_H2  = Pt(11)    # ## section headings (LESSON OBJECTIVE etc.)
SIZE_DAY_H3      = Pt(12)    # ### Day N headings
SIZE_ACTIVITY_H4 = Pt(11)    # #### Activity headings
SIZE_BODY        = Pt(10)    # normal body text
SIZE_FLAG         = Pt(9)    # flag boxes (H&L PLATFORM, VERIFY, etc.)

# ── XLSX tab colors (hex without #) ──
XLSX_TAB_COLORS = {
    "Master Pacing Guide":     "1B2A4A",
    "TEKS Coverage Matrix":    "2E75B6",
    "Free Resource Directory": "E65100",
    "eDynamic Unit Map":       "6A1B9A",
}
