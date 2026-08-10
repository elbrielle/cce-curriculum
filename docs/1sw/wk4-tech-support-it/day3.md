# Day 3: Build a Help Desk Sequence
<!-- CCE DAILY CONTRACT START -->
## Daily Learning Contract

- **Topic:** Troubleshooting Logic
- **Objective:** Students will identify problem-solving and communication skills that transfer among careers by building, testing, and explaining a three-step help desk sequence.
- **TEKS:** d(4)(B)
- **Demonstration of Learning:** Students complete the first section of the Help Desk Program Evidence: an ordered three-step sequence, Button A and Button B logic, a recorded test, and a transferable-skill connection.
<!-- CCE DAILY CONTRACT END -->

## Lesson Overview

| | |
|---|---|
| **Time** | 50 minutes |
| **Core artifact** | Help Desk Program Evidence, Day 1 of 2 |
| **Equal routes** | micro:bit + MakeCode, MakeCode simulator, or paper logic trace |
| **Materials** | Scenario Cards, Block-Order Guide, Step-Sort Cards, Program Evidence, Day 3 exit ticket |

## Before Students Arrive

1. Test `makecode.microbit.org` on a student-filtered Chromebook and leave one completed example open.
2. Assign one Chromebook per team for Days 3-5.
3. Choose and state the durable backup method.
4. If using boards, test one complete connect/download cycle. Do not update every board preemptively. Official micro:bit guidance treats firmware update as a troubleshooting step when a compatible device is not found or the installed firmware is too old.
5. Print duplicate [Scenario Cards](../../resources/worksheets/wk4-help-desk-scenario-cards.pdf), the [Block-Order Guide](../../resources/worksheets/wk4-makecode-starter-blocks.pdf), [Step-Sort Cards](../../resources/worksheets/wk4-troubleshooting-step-sort-cards.pdf), and [Program Evidence](../../resources/worksheets/wk4-help-desk-program-evidence.pdf).

## Bellringer — Put the Checks in Order (5 min)

**Prompt:** A Chromebook will not turn on. Which check belongs first: replace the device, check the charger/cable, or open a repair ticket? Explain.

Expected reasoning: start with a fast, low-risk check before a more disruptive or expensive action.

## Activity 1 — Scenario, Roles, and Project Name (10 min)

Give each team one scenario. Assign flexible roles: driver, navigator, tester, and evidence recorder. Students write the exact project name: **Period - Team - Help Desk**.

Teams use the Step-Sort Cards and say their reasoning aloud:

> “We put ___ first because it is a fast, low-risk check. We put ___ last because ___.”

Check the Wi-Fi card specifically: the scenario says everyone else is online, so students troubleshoot the user's device and do not restart shared network equipment.

## Activity 2 — Build or Trace the Logic (25 min)

Chunk the process. Students test after each chunk.

1. Create the `step` variable and set it to 1 on start.
2. Show “Help Desk Ready.”
3. Add Button A and the three branches.
4. Show the current step before increasing the variable.
5. After Step 3, return to Step 1.
6. Add Button B to display “FIXED.”

The paper route uses the same Block-Order Guide. Students trace Button A four times and Button B once.

**Active-monitoring look-fors**

- A shows Step 1, Step 2, Step 3, then Step 1.
- B independently displays FIXED.
- The sequence uses the assigned low-risk steps.
- The evidence recorder explains why Step 1 belongs first.

## Activity 3 — Test, Save, and Exit (10 min)

Students record their first test, one bug or confusion, and the durable backup location. They complete the Day 3 branching exit ticket.

Before leaving, every student names one skill used today and another career or setting that uses the same skill. Examples include nursing, teaching, automotive repair, customer service, and engineering.

## Supports

- Project the completed logic while students build; do not compress all steps into one verbal direction.
- Use bilingual Step-Sort Cards and allow Spanish step text.
- Let students use screen magnification or dictate step text to the evidence recorder.
- Rotate roles at the halfway checkpoint so tool speed does not become the assessment.

## If Hardware, MakeCode, or Attendance Fails

- No board: use the simulator.
- Site blocked: arrange the cards, trace A/A/A/A/B, and have another team initial the results.
- Saved project missing: use the screenshot, share link, downloaded `.hex`, or signed paper trace instead of rebuilding from memory.
- Absent: complete the paper route or join the assigned team's durable evidence on return.
