# CCE Agentic Slide Production Research

**Status:** Proposed architecture for pilot. Not yet an approved production pipeline.

**Owner finding:** The 1SW Week 1 Day 1 deck was visually rejected on 2026-08-23. A structural scan then found the same failure classes across all five Week 1 decks. Preserve those files as evidence, but do not treat their Canvas/Drive parity as instructional-quality approval.

## The actual goal

The system must give a teacher a strong, nearly teach-ready baseline without requiring the teacher to design slides by hand. Teachers must still be able to change pacing, shorten directions, swap examples, move a checkpoint, or replace an image. Therefore the production artifact must remain natively editable.

The system is not a prompt-to-deck toy. It is a constrained curriculum slide agent that:

- reads the approved Teacher/Student Guide pair, HQIM pages, platform task, and licensed asset ledger;
- teaches the lesson from entry through closure;
- uses the Stanley Standard automatically;
- selects from approved layouts instead of inventing geometry;
- places authentic images and approved video at readable sizes;
- writes teacher moves and sources in speaker notes;
- produces editable PowerPoint and Google Slides derivatives; and
- refuses deployment when visual or accessibility QA fails.

## Why the current Week 1 builder failed

The current builder imports a starter PowerPoint, locates text boxes by slide order, and calls `textbox.text.set(...)`. It then places images at absolute coordinates. That created four systemic defects:

1. **Inherited paragraph corruption:** New text inherited old paragraph and run formatting. In Day 1 slide 5, step 2 has no explicit font-size run while step 3 inherited bold. In slide 7, inherited bullet characters `1`, `2`, and `3` were combined with literal bullet text. In slide 8, inherited checkmark bullets were combined with literal `•` characters.
2. **No semantic content model:** The JSON stores an ordered list of strings, not a title, numbered procedure, bullet list, model, question, completion check, or media frame. The builder cannot enforce consistent formatting because it does not know what the text means.
3. **Coordinate overlays without collision rules:** Images were added over full-width inherited text boxes. Day 1 slides 7 and 8 have near-total text-image intersections. The same shared builder produced collision candidates in every Week 1 deck.
4. **Insufficient QA:** Wording lint, notes fields, slide count, editability, off-canvas overflow, and contact sheets passed. None of those checks list semantics, mixed run styling, text-image collision, minimum instructional image size, dead-space balance, or PowerPoint's final rendering. The native Drive renders contained the defects, but montage-scale review concealed them.

Cross-deck scan on 2026-08-23:

| Deck | Text-image collision candidates | Double list markers |
|---|---:|---:|
| Day 1 | 4 | 7 |
| Day 2 | 1 | 9 |
| Day 3 | 11 | 0 |
| Day 4 | 2 | 3 |
| Day 5 | 4 | 6 |

These counts are diagnostic candidates, not a final per-slide design audit. They are sufficient to reject the shared builder as a production baseline.

## Current agentic options

| Option | Native editability | Template control | Image/video fit | Automation fit | CCE judgment |
|---|---|---|---|---|---|
| **Plus AI Presentation Agent API/MCP** | Returns native editable PPTX | Accepts custom templates and existing decks | Images are supported; embedded-video behavior must be proven in the pilot | Strongest direct agent/API fit; supports iterative sessions | Leading external pilot candidate, pending district/privacy approval and a real output test |
| **Microsoft Copilot in PowerPoint** | Native PowerPoint | Brand kits and organizational templates | PowerPoint supports embedded H.264/AAC MP4 and online video; Copilot can add/edit images | Strong in-app agent, but less suitable for unattended bulk API generation | Leading tenant-native authoring candidate if IISD has the required commercial license |
| **Gemini in Google Slides** | Generates fully editable native Slides | Can match the style of an existing Drive presentation | Native Slides supports YouTube, URL, and Drive video | Strong collaborative authoring; the generation feature is plan-gated, desktop/English-limited, and not a general bulk API | Leading Google-native candidate; still needs a separate PowerPoint/video parity plan |
| **Beautiful.ai** | Editable PowerPoint export on paid plans | Themes/templates and Smart Slides | Strong automatic alignment and native video support inside Beautiful.ai | API can create from structured outlines | Good visual-layout challenger, but transitions/animations do not export and Google Slides export drops embedded video/audio |
| **Plus AI add-in** | Native PowerPoint and Slides | Custom template support is limited/beta outside enterprise workflows | Good images; video support is not documented as a core generation feature | Useful for teacher-side refinement | Secondary to its API/MCP for agentic bulk work |
| **Gamma / Canva / Pitch** | Exportable, with varying editability | Good visual templates | Strong web media experiences | Fast drafts | Not canonical for CCE because PPTX/Google export can change fonts, layout, animation, or media behavior |
| **Internal native compiler** | Full control over editable text, images, notes, and layout objects | Complete | Images are straightforward; video requires a supported native media layer | Highest engineering effort, no third-party curriculum upload | Long-term control option and QA reference implementation |

## Recommended CCE architecture

### 1. Design in HTML, approve in native layouts

Keep HTML/CSS as the fast visual exploration environment because it produces the polished baseline the owner prefers. Do not ship the full-slide PNG as the only slide object. Once a slide family is approved, recreate it once as a native PowerPoint/Google Slides layout with real placeholders.

The first Stanley template should contain a small, deliberate layout library:

- title/day divider;
- As You Enter;
- Do Now with visual;
- Today You Will;
- concept plus large photo;
- workbook/source page with callouts;
- platform path with authentic screenshot;
- numbered procedure;
- model/non-model;
- partner roles and timer;
- work checkpoint;
- video with a visible text route;
- You Are Done When; and
- exit/closure.

The background texture or decorative frame may be a locked SVG/PNG. Titles, directions, timers, screenshots, callouts, captions, and teacher-changeable content remain native editable objects.

### 2. Replace positional string arrays with a semantic slide specification

The agent should produce a typed slide plan, for example:

```json
{
  "layout": "platform-path",
  "title": "Open Xello",
  "steps": ["Open ClassLink", "Select Xello", "Open What Is CTE?"],
  "visual": {"asset": "classlink-xello-tile.png", "role": "platform-screenshot"},
  "doneWhen": "The response is submitted.",
  "notes": {"teacherMove": "...", "lookFor": "...", "sources": ["..."]}
}
```

Lists must be native lists generated from structured items. The source text must never contain literal bullet characters when bullet metadata is applied. Every text style is set explicitly after insertion; no paragraph inherits unexplained formatting from a source slide.

### 3. Use an agent to plan and populate, not invent geometry

The agent receives:

- the approved lesson contract and 50-minute flow;
- the Stanley template/layout library;
- the asset inventory with rights, alt text, and allowed delivery boundary;
- exact platform routes and workbook pages;
- the three language tiers; and
- teacher-editable versus locked elements.

It selects layouts, writes concise slide copy, assigns one instructional job per slide, and fills bounded placeholders. It may request a missing image or video asset. It may not add an unbounded text box or image overlay.

### 4. Produce two native media-aware derivatives from one specification

- **PowerPoint:** Native text, images, notes, alt text, and—when permitted—embedded H.264/AAC MP4 or supported online video.
- **Google Slides:** Native text, images, notes, alt text, and a `CreateVideoRequest` for approved YouTube or Drive media.

Do not assume video survives a PowerPoint-to-Google or Google-to-PowerPoint conversion. The canonical slide specification names the video source and poster, and each renderer inserts the correct native media object. When a licensed vendor stream may not be rehosted, use the official player/link plus a readable poster and text route.

### 5. Make QA fail closed

Automated checks must reject:

- any text/image/media intersection outside a layout's explicitly allowed zones;
- literal bullet/number characters combined with native list metadata;
- mixed font size, weight, or color within a procedure unless the semantic spec requests emphasis;
- title wrapping, font below the Stanley minimum, or text auto-shrink;
- instructional screenshots below a tested display-size threshold;
- low-resolution, stretched, or unreadable images;
- unexplained dead space or an unbalanced primary composition;
- empty or duplicate placeholders;
- missing alt text, unique title, reading order, captions/text video route, or source notes;
- missing Do Now, exact path/page, partner role, timer/checkpoint, or Done When where the lesson requires it; and
- visual drift between the PowerPoint render and the native Google Slides render.

The review sequence is binding:

1. Render every slide at 1920×1080 or higher from the final PowerPoint.
2. Inspect every slide individually at full size. A contact sheet is only for pacing and consistency.
3. Run PowerPoint's Accessibility Checker and verify reading order.
4. Import/update the native Google Slides derivative, export it, and compare the native render slide by slide.
5. Give the owner a four-slide review sample before generating the complete week.
6. Synchronize Canvas and Drive only after owner acceptance.

## Recommended pilot

Do not rebuild all 75 Week 1 slides first. Build the same four difficult Day 1 slides through two candidate pipelines:

1. Xello three-step launch with authentic icon and Done When;
2. FYF p. 199 with a readable workbook visual and discussion question;
3. six pathways with a large authentic app screen and clean list; and
4. tour/video launch with timer, response cue, and text alternative.

Pilot A should use **Plus AI Presentation Agent API/MCP with a Stanley native template** if district/privacy review permits a sanitized trial. Pilot B should use the **internal semantic-spec/native-layout compiler**. If Microsoft 365 Copilot is already licensed in the district tenant, use it as a third in-app comparison.

Score each result on visual baseline, editability, list/style integrity, image legibility, native video, speaker notes, accessibility, Google/PowerPoint parity, reproducibility, privacy, and minutes of human repair. Adopt the winning architecture only after the owner reviews the actual four-slide files in PowerPoint.

## Pilot outcome: selected local hybrid compiler

The four-slide bake-off compared a fully native composition with a hybrid composition that uses a rendered decorative background plus native editable content. The hybrid won because it reached the visual finish of the HTML prototype without flattening titles, directions, screenshots, timers, completion cues, or notes into a single image.

The selected implementation is `build/decks/1sw-wk1-agentic/build.mjs`. It rebuilt all 75 Week 1 slides from the lesson-grounded JSON sources with an explicit layout map, named objects, explicit text styles, and structured speaker notes. The five final PowerPoints passed the fail-closed geometry/style/notes gate with zero issues, the PowerPoint overflow test, and full-size render inspection. No external paid slide-generation service or licensed-content upload was required.

The test also exposed two limits that remain part of the production contract:

- The current PowerPoint exporter retains semantic alt labels in its authoring model but does not reliably emit those descriptions into OOXML. Run PowerPoint Accessibility Checker and repair image descriptions before publication until the exporter closes that gap.
- The Drive connector can preserve raw PowerPoint IDs but cannot import a PPTX into an existing native Google Slides ID. Native Google parity therefore requires the backed-up, import-first browser workflow and an independent native render/notes check.

## Data and licensing boundary

Do not send FYF pages, Xello/H&L licensed files, authenticated screenshots, student data, or district-only materials to a third-party slide service until district/vendor terms and data processing are approved. The first external-service pilot uses public-safe substitute assets. A tenant-native or internal compiler remains the default when approval is unclear.

## Research sources

- [Plus AI Presentation MCP](https://plusai.com/features/mcp) and [Presentation Agent API](https://plusai.com/features/presentation-agent-api)
- [Microsoft: Edit with Copilot in PowerPoint](https://support.microsoft.com/en-US/PowerPoint/edit-with-copilot-in-powerpoint)
- [Microsoft: Create a branded presentation from a file](https://support.microsoft.com/en-US/PowerPoint/copilot-tutorial-create-a-branded-presentation-from-a-file)
- [Microsoft: Insert and play a video file](https://support.microsoft.com/en-US/PowerPoint/insert-and-play-a-video-file-from-your-computer)
- [Microsoft: Make PowerPoint presentations accessible](https://support.microsoft.com/en-US/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities)
- [Google: Generate presentations with Gemini in Slides](https://support.google.com/docs/answer/17111393)
- [Google: Insert images and videos in Slides](https://support.google.com/docs/answer/97447)
- [Google Slides API: CreateVideoRequest](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request#CreateVideoRequest)
- [Beautiful.ai: Smart Slide templates](https://www.beautiful.ai/slide-templates), [video support](https://support.beautiful.ai/hc/en-us/articles/40186723882125-Video), and [export limitations](https://support.beautiful.ai/hc/en-us/articles/30629528652685-Exporting-your-slides-and-presentations)
- [Gamma: PowerPoint/PDF export differences](https://help.gamma.app/en/articles/15939201-why-doesn-t-my-exported-pdf-or-powerpoint-match-what-i-see-in-gamma)
