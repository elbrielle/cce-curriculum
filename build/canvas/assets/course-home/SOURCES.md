# CCE course-home asset sources

Accessed August 16, 2026.

| Asset | Source | Use |
|---|---|---|
| `modules.png` | Original CCE navigation mark created for this course | Identifies the Canvas Modules launch. It does not represent an external product. |
| `onenote.png` | Microsoft, [Branding guidelines and logos for OneNote API developers](https://www.microsoft.com/en-us/download/details.aspx?id=42977), `OneNote Logos_Final.zip`, `AppLockup_rgb_OneNote_Large_OneNote_88.png` | Official purple OneNote icon-and-name lockup on a light background. Microsoft identifies the lockup as the preferred representation and prohibits custom replacement icons, recoloring, and shadows. |
| `hats-ladders.png` | Hats & Ladders, [official site header](https://hatsandladders.com/), `logo-purple-registered@4x.png` | Official purple Hats & Ladders registered wordmark. |
| `xello.png` | Xello, [Brand Center](https://xello.world/en/brand-center/), `Xello-Brand-Center-Wordmark.jpg` | Official preferred Xello wordmark. It is shown on white without an outline, shadow, recoloring, or enclosing shape. The source JPEG was converted to PNG without changing its proportions or content. |

The three product marks are used only to identify the linked services for enrolled students. They are kept in locked authenticated Canvas files. Do not redraw them, put them inside decorative shapes, recolor them, or add effects.

## Interface basis

The launch surface follows the current Material 3 distinction between a prominent action and a short navigational list:

- [Buttons](https://m3.material.io/components/buttons/overview) for the single primary Modules action;
- [Lists](https://m3.material.io/components/lists/overview) for the three recurring tool destinations;
- [Interaction states](https://m3.material.io/foundations/interaction/states/overview) for clear enabled/focus/hover treatment rather than decorative shadows.

Canvas page HTML cannot supply the full application state-layer system. The implementation therefore keeps the hierarchy explicit in the saved markup: one high-contrast filled Modules link, full-width linked rows, literal link text, official product marks, and divider lines. It does not imitate an app dashboard with colored edge treatments, stacked cards, or elevation effects.
