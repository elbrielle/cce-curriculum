---
title: MakeCode Help Desk Starter Blocks
slug: wk4-makecode-starter-blocks
kind: scaffold
weeks: 1sw/wk4-tech-support-it
audience: student
variant_of:
language: en
pages: 2
orientation: portrait
---
**This is the starter program, block by block, in the order you drag them in.** Build it at [makecode.microbit.org](https://makecode.microbit.org), then change only the words inside the quote marks to your team's three troubleshooting steps. There is no link to click and no file to download. You build it from this card.

**Before you start:** from the **Variables** drawer, click **Make a Variable** and name it `step`.

| # | Drawer | Block to drag | Where it goes | What to type in it |
|---|---|---|---|---|
| 1 | Variables | `set step to 0` | inside `on start` | change the 0 to **1** |
| 2 | Basic | `show string " "` | inside `on start`, under block 1 | `Help Desk Ready` |
| 3 | Input | `on button A pressed` | empty workspace | nothing |
| 4 | Logic | `if / then / else` | inside `on button A pressed` | nothing yet |
| 5 | Logic | `0 = 0` comparison | into the `if` slot of block 4 | drag `step` into the left side, type **1** on the right |
| 6 | Basic | `show string " "` | inside the first `then` | `Step 1:` plus your first step |
| 7 | Logic | click the **+** on the if block | adds an `else if` | nothing |
| 8 | Logic | `0 = 0` comparison | into the `else if` slot | drag `step` into the left side, type **2** on the right |
| 9 | Basic | `show string " "` | inside the `else if` then | `Step 2:` plus your second step |
| 10 | Basic | `show string " "` | inside the final `else` | `Step 3:` plus your third step |
| 11 | Variables | `change step by 1` | inside `on button A pressed`, **under** the whole if block | nothing |
| 12 | Logic | `if / then` | under block 11 | nothing |
| 13 | Logic | `0 > 0` comparison | into the `if` slot of block 12 | drag `step` into the left side, type **3** on the right |
| 14 | Variables | `set step to 0` | inside that `then` | change the 0 to **1** |
| 15 | Input | `on button B pressed` | empty workspace | nothing |
| 16 | Basic | `show string " "` | inside `on button B pressed` | `FIXED!` |

**Read the order carefully.** Block 11 comes AFTER the whole if block, not before it. The micro:bit shows the step first, then counts up to the next one. If you put `change step by 1` above the if block, the first press of Button A skips straight to Step 2.

**Test it.** Press A four times. You should see Step 1, Step 2, Step 3, and then Step 1 again. Press B. You should see FIXED!

## Before you leave

Record your project name and backup location on the Help Desk Program Evidence sheet. If the site is unavailable, trace Button A four times and Button B once on this guide and ask another team to initial the result.
