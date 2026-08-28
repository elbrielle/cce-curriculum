import assert from "node:assert/strict";
import test from "node:test";

import {
  detectLayoutIssues,
  detectOoxmlIssues,
  parseSlideXml,
} from "./deck_quality_gate.mjs";

test("layout gate catches collisions, small instructional images, and wrapped titles", () => {
  const layout = {
    slide: { slide: 7, frame: { width: 960, height: 540 } },
    elements: [
      {
        kind: "shape",
        id: "10",
        name: "Title",
        bbox: [40, 20, 880, 80],
        text: "A title that wrapped",
        resolvedFontSize: 40,
        textLayout: { lineCount: 2 },
      },
      { kind: "shape", id: "11", bbox: [40, 120, 700, 260], text: "Directions" },
      { kind: "image", id: "12", bbox: [600, 160, 220, 120], alt: "Xello screenshot" },
    ],
  };
  const issues = detectLayoutIssues(layout, {}, new Set(["10"]));
  const codes = new Set(issues.map((issue) => issue.code));
  assert.ok(codes.has("TEXT_IMAGE_COLLISION_CANDIDATE"));
  assert.ok(codes.has("INSTRUCTIONAL_IMAGE_TOO_SMALL"));
  assert.ok(codes.has("TITLE_WRAPS"));
});

test("declared collision zones suppress only the declared overlap", () => {
  const layout = {
    slide: { slide: 2 },
    elements: [
      { kind: "shape", id: "1", bbox: [0, 0, 400, 300], text: "Text" },
      { kind: "image", id: "2", bbox: [300, 200, 200, 200], alt: "photo" },
    ],
  };
  const issues = detectLayoutIssues(layout, {
    allowedCollisionZones: [{ slide: 2, x: 300, y: 200, width: 100, height: 100 }],
  });
  assert.equal(issues.filter((issue) => issue.code === "TEXT_IMAGE_COLLISION_CANDIDATE").length, 0);
});

test("OOXML gate catches double markers, suspicious bullet chars, style drift, and missing alt", () => {
  const xml = `
  <p:sld xmlns:p="p" xmlns:a="a"><p:cSld><p:spTree>
    <p:sp><p:nvSpPr><p:cNvPr id="7" name="Steps"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:txBody><a:bodyPr/><a:lstStyle/>
        <a:p><a:pPr><a:buChar char="1"/></a:pPr><a:r><a:rPr sz="2400"/><a:t>• Open ClassLink</a:t></a:r></a:p>
        <a:p><a:pPr><a:buChar char="2"/></a:pPr><a:r><a:rPr sz="2000" b="1"/><a:t>Open Xello</a:t></a:r></a:p>
      </p:txBody>
    </p:sp>
    <p:pic><p:nvPicPr><p:cNvPr id="8" name="Screenshot"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr></p:pic>
  </p:spTree></p:cSld></p:sld>`;
  const parsed = parseSlideXml(xml, 5);
  const issues = detectOoxmlIssues(parsed);
  const codes = new Set(issues.map((issue) => issue.code));
  assert.ok(codes.has("LITERAL_AND_NATIVE_LIST_MARKER"));
  assert.ok(codes.has("DIGIT_OR_CHECKMARK_BULLET_METADATA"));
  assert.ok(codes.has("PROCEDURE_FONT_SIZE_INCONSISTENT"));
  assert.ok(codes.has("PROCEDURE_BOLD_INCONSISTENT"));
  assert.ok(codes.has("IMAGE_ALT_TEXT_MISSING"));
});

test("OOXML alternative text satisfies the image check", () => {
  const xml = `<p:sld><p:cSld><p:spTree><p:pic><p:nvPicPr><p:cNvPr id="8" name="Screenshot" descr="Xello result screen"/></p:nvPicPr></p:pic></p:spTree></p:cSld></p:sld>`;
  const issues = detectOoxmlIssues(parseSlideXml(xml, 1));
  assert.equal(issues.filter((issue) => issue.code === "IMAGE_ALT_TEXT_MISSING").length, 0);
});
