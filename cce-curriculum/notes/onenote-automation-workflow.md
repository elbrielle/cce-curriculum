# OneNote Automation Workflow

This document codifies the requirements for agents (Antigravity, Claude, Codex) generating worksheets and exit tickets for the CCE curriculum.

## The Dual-Track Strategy
To support varying teacher preferences, all student-facing worksheets and exit tickets must be available in two formats:
1. **Printable PDF:** Maintained in `docs/resources/worksheets/` and `docs/resources/exit-tickets/` for colleagues who prefer physical handouts.
2. **Native OneNote HTML:** A semantic HTML structure designed specifically to be injected into Microsoft OneNote via the Graph API.

The OneNote artifact is a parallel teacher-selectable derivative. It does not replace or deprecate the printable artifact, and it does not remove an existing private Canvas response when that is an approved route. Before class, the teacher selects one response home for the class or individual student. Students complete the work once in that selected location; they are never required to copy the same response between OneNote, paper, Canvas, FYF, H&L, or Xello.

## OneNote Graph API Constraints
Microsoft OneNote does not have an MCP server. Instead, we use the Microsoft Graph API (`https://graph.microsoft.com/v1.0/me/onenote/pages`).

When an agent is tasked with creating or updating a worksheet for OneNote, it must adhere to the following HTML standards expected by the Graph API:
- **No external CSS:** OneNote ignores external stylesheets and most complex inline styling. Rely on semantic HTML structure.
- **Native Elements:** Use `<h1>`, `<h2>`, `<p>`, `<ul>`, `<ol>` for text structuring.
- **Tables for Layout:** Because OneNote lacks CSS grid/flexbox and frequently ignores CSS percentage widths, use standard `<table>`, `<tr>`, `<td>` tags. You **must** specify absolute pixel widths (e.g., `<table width="850">` and `<td width="300">`) to prevent tables from collapsing into narrow columns. Avoid 1x1 tables that grow awkwardly; give students distinct rows or clearly defined sections.
- **ESL/Emergent Bilingual Scaffolds:** Apply the strategic support decision below. Do not translate every line by default.
- **Images:** Images can be embedded using `<img src="URL" alt="..." />`. Ensure the URL is publicly accessible, or the script will need to upload the image as multipart form data.
- **Document Structure:** The HTML payload *must* include a `<head><title>Page Title</title></head>` block. The `<title>` tag dictates the name of the page in OneNote.

## Deployment Pipeline
The deployment tool is located at `build/onenote/deploy_worksheet.py`.

**Usage:**
```bash
python build/onenote/deploy_worksheet.py --section-id REVIEWED_SECTION_ID --title "Day 1: Exit Ticket" --html-file path/to/worksheet.html
```

**Agent Instructions:**
1. When the user requests a new worksheet, draft the HTML version first.
2. If the user wants to deploy it, run the `deploy_worksheet.py` script with the reviewed teacher-only section ID. The tool creates a new page and fails closed when that exact title already exists; it does not perform partial in-place updates.
3. The script uses MSAL Device Code Flow. It will output a URL and a code to `stderr`. You MUST relay this URL and code to the user in the chat so they can authenticate. The script will block until the user completes the login in their browser.
4. Once authenticated, the page is pushed to the teacher's OneNote.

## Strategic EB Support Decision

The goal is access to the same grade-level thinking, plus growth in academic English. A longer bilingual page is not automatically a better scaffold. For each response block, identify the language function students need: name, describe, sequence, explain, compare, justify, or reflect. Then add the smallest useful combination of supports:

1. **Focused vocabulary:** Preteach a small set of high-utility academic and technical terms. Pair each with a student-friendly definition, meaningful icon/photo, example, cognate, or home-language equivalent when useful. Do not turn the page into a translated dictionary.
2. **Comprehensible model:** Show one completed example or nonexample and explicitly connect the evidence to the expected response. Authentic interface icons and screenshots should clarify click paths; decorative images do not count as language support.
3. **Oral rehearsal before writing:** Build in partner talk, teacher think-aloud, read-aloud, or speech-to-text so students can form the idea before producing a written answer.
4. **Purpose-built frames:** Offer a stem that matches the thinking move, such as evidence-to-reason (`The clue ___ matters because ___`) or sequence (`First ___; next ___; finally ___`). A frame is optional support, not the only acceptable syntax. More proficient students may write without it or expand it.
5. **Strategic home-language access:** Translate essential directions, safety statements, prerequisite information, and high-value terms when needed. Encourage cognates, personal glossaries, bilingual dictionaries, and multilingual planning. Do not assume every EB student speaks Spanish, and do not automatically mirror every prompt or response line in Spanish.
6. **Responsive fading:** Keep the content target constant. Adjust word/phrase, sentence, and discourse support from observed speaking/writing samples and proficiency information; remove or extend supports as students become more independent.

Before deployment, the author should be able to answer: What language demand could mask the student's content knowledge? Which scaffold addresses that exact demand? Can the student still see and practice the English needed for the task? Can a teacher easily fade or extend the support?

### Research basis

- The U.S. Department of Education's What Works Clearinghouse recommends intensive work with a focused set of academic vocabulary, integration of oral and written English into content instruction, and regular structured writing opportunities: [Teaching Academic Content and Literacy to English Learners in Elementary and Middle School](https://ies.ed.gov/ncee/wwc/PracticeGuide/19).
- WIDA recommends maintaining common grade-level content and language goals while differentiating multimodal scaffolds from actual language evidence and proficiency descriptors: [WIDA Proficiency Level Descriptors: Informing Expectations and Scaffolding](https://wida.wisc.edu/resources/resource-snapshot/wida-proficiency-level-descriptors-informing-expectations-and) and the [WIDA ELD Standards Framework Implementation Guide](https://wida.wisc.edu/sites/default/files/resource/Implementation-Guide-WIDA-ELD-Standards-Framework.pdf).
- CAST recommends clarifying vocabulary and language structures through multiple representations and making key information available across languages when needed: [CAST UDL Guidelines - Language and Symbols](https://udlguidelines.cast.org/representation/language-symbols/).
- WIDA frames home-language use as an asset through cognates, multilingual resources, and personal glossaries rather than a requirement to duplicate every line: [A Guide to Translanguaging in the Classroom](https://wida.wisc.edu/news/guide-translanguaging-classroom).
