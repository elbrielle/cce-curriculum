import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 2 });
await page.goto(`file://${path.join(here, "backgrounds.html")}`);
for (const id of ["left-media", "right-media", "split", "video"]) {
  for (const other of ["left-media", "right-media", "split", "video"]) {
    await page.locator(`#${other}`).evaluate((node, visible) => { node.style.display = visible ? "block" : "none"; }, other === id);
  }
  await page.locator(`#${id}`).screenshot({ path: path.join(here, `bg-${id}.png`) });
}
await browser.close();
await fs.writeFile(path.join(here, "background-rendered.txt"), "1280x720 at 2x device scale\n");
