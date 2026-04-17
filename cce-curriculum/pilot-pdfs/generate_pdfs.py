"""Generate 5 exit ticket PDFs for 2SW Wk2 pilot week.

Brute-force script for the pilot. NOT a reusable pipeline for all 180 days.
If we decide to scale later, parameterize content via YAML / JSON and loop.

Design:
- Letter-size, one ticket per page
- Header row (Name / Date / Period)
- Title + format label
- Body content from cce-curriculum/notes/exit-ticket-templates.md examples
- Horizontal-rule "answer blanks" where the student writes
- No TEK codes visible to student
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.colors import black, HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
    Table,
    TableStyle,
)
from reportlab.lib.enums import TA_LEFT
from pathlib import Path

# PDFs ship on the deployed MkDocs site under docs/resources/exit-tickets/
# so coordinators can follow a single site link and browse printable versions
# alongside the daily plan.
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "docs" / "resources" / "exit-tickets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Shared styles ----------

styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "Title",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=16,
    leading=20,
    spaceAfter=4,
    textColor=black,
)

SUBTITLE = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=10,
    leading=12,
    spaceAfter=14,
    textColor=HexColor("#555555"),
)

BODY = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=12,
    leading=16,
    spaceAfter=8,
)

QUESTION = ParagraphStyle(
    "Question",
    parent=BODY,
    fontName="Helvetica-Bold",
    spaceBefore=8,
    spaceAfter=4,
)

CHOICE = ParagraphStyle(
    "Choice",
    parent=BODY,
    leftIndent=24,
    spaceAfter=3,
)

LIST_ITEM = ParagraphStyle(
    "ListItem",
    parent=BODY,
    leftIndent=18,
    bulletIndent=6,
    spaceAfter=2,
)

INSTRUCTION = ParagraphStyle(
    "Instruction",
    parent=BODY,
    fontName="Helvetica-Oblique",
    spaceBefore=4,
    spaceAfter=4,
)


def answer_line():
    """Horizontal rule as a writing blank."""
    return HRFlowable(
        width="100%",
        thickness=0.5,
        color=HexColor("#888888"),
        spaceBefore=4,
        spaceAfter=10,
    )


def answer_block(lines=2):
    """Multi-line answer block."""
    return [answer_line() for _ in range(lines)]


def name_date_period_header():
    """Top-of-page identification row."""
    data = [[
        Paragraph("<b>Name:</b> ______________________________", BODY),
        Paragraph("<b>Date:</b> ______________", BODY),
        Paragraph("<b>Period:</b> ______", BODY),
    ]]
    t = Table(data, colWidths=[3.2 * inch, 2.0 * inch, 1.3 * inch])
    t.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def build_pdf(filename, title, subtitle, story_body):
    """Assemble and write one exit ticket PDF."""
    path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title=title,
    )
    full = [
        name_date_period_header(),
        Spacer(1, 14),
        HRFlowable(width="100%", thickness=1.2, color=black, spaceAfter=10),
        Paragraph(title, TITLE),
        Paragraph(subtitle, SUBTITLE),
    ]
    full.extend(story_body)
    doc.build(full)
    print(f"Built {path.name}")


# ---------- Day 1: Mini-Case ----------

def day1():
    body = [
        Paragraph(
            "Jordan is a high school senior in Irving ISD. Jordan wants to start "
            "working as a first responder in the next year after graduating. "
            "Jordan wants to stay close to family in DFW.",
            BODY,
        ),
        Spacer(1, 10),
        Paragraph(
            "<b>1.</b> Which pathway from your Training Comparison worksheet fits "
            "Jordan's one-year plan best? (Police Officer, EMT, or Firefighter) "
            "Use the training time from your worksheet to explain.",
            QUESTION,
        ),
        *answer_block(3),
        Paragraph(
            "<b>2.</b> To start this pathway fast, what is one hard choice Jordan "
            "will need to make?",
            QUESTION,
        ),
        *answer_block(3),
    ]
    build_pdf(
        "2sw-wk2-day1-first-responder-pathways.pdf",
        "Exit Ticket — Day 1: First Responder Pathways",
        "2SW Week 2 · Law Enforcement & EMT · Mini-Case format",
        body,
    )


# ---------- Day 2: Diagnostic MCQ ----------

def day2():
    body = [
        Paragraph(
            "A detective looks at the evidence and says Alex took the painting. "
            "Later, she finds new clues that point to Kai instead. Now she must "
            "tell her boss she was wrong.",
            BODY,
        ),
        Spacer(1, 6),
        Paragraph(
            "To change her mind and fix her mistake, which quality does the "
            "detective need MOST?",
            QUESTION,
        ),
        Paragraph("<b>A.</b> Speed, because detectives have to solve cases fast.", CHOICE),
        Paragraph(
            "<b>B.</b> Honesty, because telling the truth about being wrong is "
            "hard but important.",
            CHOICE,
        ),
        Paragraph(
            "<b>C.</b> Confidence, because good detectives never doubt themselves.",
            CHOICE,
        ),
        Paragraph("<b>D.</b> Luck, because detective work is mostly guessing.", CHOICE),
        Spacer(1, 10),
        Paragraph(
            "Circle your answer. In one sentence, say why the other three choices "
            "are weaker.",
            INSTRUCTION,
        ),
        *answer_block(3),
    ]
    build_pdf(
        "2sw-wk2-day2-missing-painting.pdf",
        "Exit Ticket — Day 2: Missing Painting",
        "2SW Week 2 · Law Enforcement & EMT · Diagnostic MCQ format",
        body,
    )


# ---------- Day 3: Decision Tree ----------

def day3():
    body = [
        Paragraph(
            "<b>My role today:</b> __________________________________",
            BODY,
        ),
        Paragraph("(a first responder career in Law and Public Service)", INSTRUCTION),
        Spacer(1, 4),
        Paragraph(
            "<b>My team's emergency:</b> __________________________________",
            BODY,
        ),
        Spacer(1, 10),
        Paragraph(
            "<b>Step 1:</b> What does your role do FIRST in the first 15 minutes "
            "of the emergency?",
            QUESTION,
        ),
        *answer_block(3),
        Paragraph(
            "<b>Step 2:</b> Pick ONE quality your role needs MOST right now "
            "(choose one or add your own):",
            QUESTION,
        ),
        Paragraph("• stay calm", LIST_ITEM),
        Paragraph("• work fast", LIST_ITEM),
        Paragraph("• make hard choices", LIST_ITEM),
        Paragraph("• speak clearly", LIST_ITEM),
        Paragraph("• notice small things", LIST_ITEM),
        Paragraph("• help others", LIST_ITEM),
        Spacer(1, 8),
        Paragraph("<b>I picked:</b> __________________________________", BODY),
        Spacer(1, 8),
        Paragraph(
            "<b>Why does this quality matter more than the others RIGHT NOW?</b> "
            "(One sentence)",
            QUESTION,
        ),
        *answer_block(3),
    ]
    build_pdf(
        "2sw-wk2-day3-task-force-setup.pdf",
        "Exit Ticket — Day 3: Task Force Setup",
        "2SW Week 2 · Law Enforcement & EMT · Decision Tree format",
        body,
    )


# ---------- Day 4: Trade-off ----------

def day4():
    body = [
        Paragraph(
            "You are the Emergency Management Director. A wildfire is coming. "
            "You have enough buses to save only ONE place before the fire gets "
            "here:",
            BODY,
        ),
        Paragraph(
            "<b>(A)</b> A senior living home with 80 older adults. Many use "
            "wheelchairs or walkers.",
            LIST_ITEM,
        ),
        Paragraph(
            "<b>(B)</b> A high school with 1,200 students and staff at an "
            "after-school event.",
            LIST_ITEM,
        ),
        Spacer(1, 10),
        Paragraph("<b>Pros of picking A:</b>", QUESTION),
        *answer_block(2),
        Paragraph("<b>Pros of picking B:</b>", QUESTION),
        *answer_block(2),
        Paragraph("<b>My choice (A or B):</b> ______", QUESTION),
        Spacer(1, 6),
        Paragraph(
            "To make a hard choice like this, first responders need a strong "
            "professional quality. Pick ONE from the list (or add your own):",
            BODY,
        ),
        Paragraph("• calm &nbsp;&nbsp; • fair &nbsp;&nbsp; • brave &nbsp;&nbsp; "
                  "• honest &nbsp;&nbsp; • caring &nbsp;&nbsp; • clear-thinking", LIST_ITEM),
        Spacer(1, 6),
        Paragraph(
            "<b>Which quality fits THIS choice best?</b> "
            "______________________________",
            QUESTION,
        ),
        Paragraph(
            "<b>In one sentence, why is THIS quality the right one here "
            "(not the others)?</b>",
            QUESTION,
        ),
        *answer_block(2),
    ]
    build_pdf(
        "2sw-wk2-day4-citywide-emergency-plan.pdf",
        "Exit Ticket — Day 4: Citywide Emergency Plan",
        "2SW Week 2 · Law Enforcement & EMT · Trade-off / Dilemma Analysis format",
        body,
    )


# ---------- Day 5: Concept Map ----------

def day5():
    body = [
        Paragraph(
            "<b>My favorite first responder career from this week:</b>",
            QUESTION,
        ),
        answer_line(),
        Spacer(1, 4),
        Paragraph("<b>Connect this career to THREE things:</b>", QUESTION),
        Spacer(1, 4),
        Paragraph(
            "<b>1. A TRAINING FACT from your worksheet</b> "
            "<i>(example: \"EMT training takes 6 to 12 weeks\")</i>",
            BODY,
        ),
        Paragraph("<b>My training fact:</b>", BODY),
        answer_line(),
        Spacer(1, 4),
        Paragraph(
            "<b>2. Your Wk0 RIASEC type</b> "
            "<i>(Doer, Analyzer, Creator, Helper, Persuader, or Organizer)</i>",
            BODY,
        ),
        Paragraph("<b>My RIASEC type:</b> ______________________________", BODY),
        Paragraph(
            "<b>Why does this career match (or not match) your type?</b> "
            "(one sentence)",
            BODY,
        ),
        answer_line(),
        answer_line(),
        Spacer(1, 4),
        Paragraph(
            "<b>3. A quality this career needs</b> "
            "<i>(example: brave, honest, caring, clear-thinking, strong)</i>",
            BODY,
        ),
        Paragraph("<b>My quality:</b> ______________________________", BODY),
        Paragraph(
            "<b>Why does this career need this quality?</b> (one sentence)",
            BODY,
        ),
        answer_line(),
        answer_line(),
    ]
    build_pdf(
        "2sw-wk2-day5-cluster-wrap-up.pdf",
        "Exit Ticket — Day 5: Cluster Wrap-Up",
        "2SW Week 2 · Law Enforcement & EMT · Concept Map format",
        body,
    )


if __name__ == "__main__":
    day1()
    day2()
    day3()
    day4()
    day5()
    print(f"\nAll 5 PDFs generated in {OUTPUT_DIR.relative_to(Path(__file__).resolve().parents[2])}/")
