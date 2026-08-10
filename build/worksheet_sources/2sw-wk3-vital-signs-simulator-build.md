---
title: Vital Signs Simulator Build and Test
slug: 2sw-wk3-vital-signs-simulator-build
kind: scaffold
weeks: 2sw/wk3-nursing-health-science
audience: student
variant_of:
language: en
pages: 2
orientation: portrait
---

## The boundary

This program is a **training simulation**. It does not measure a person, diagnose a condition, or replace medical equipment. Use only fictional values supplied by the lesson.

## Build in Microsoft MakeCode

1. Open **makecode.microbit.org** and create a project named `Vital Signs Simulator`.
2. In `on button A pressed`, set `heartRate` to `pick random 60 to 110`.
3. Add `show number heartRate`.
4. Add a heart LED image, `pause 200 ms`, and a smaller or blank heart image.
5. In `on button B pressed`, set `temperature` to `pick random 970 to 1005`.
6. Add `show number temperature` and explain that 986 represents 98.6°F because the micro:bit display does not show decimals in this build.
7. Test both buttons in the on-screen simulator.
8. Save a screenshot or share link. Download to a physical micro:bit only if one is available.

## Test record

| Test | Expected result | What happened | Revision made |
|---|---|---|---|
| Button A | Shows a fictional heart-rate value | | |
| Button A visual | Shows a pulse animation | | |
| Button B | Shows a fictional temperature code | | |
| Repeat test | Values can change within the assigned range | | |

[[pagebreak]]

## Add a handoff alert

Add this **simulation rule** after Button A displays the value:

- If `heartRate > 100`, show the letter `R` for **report**.
- Otherwise, show a check mark.

The `R` does not diagnose anything. It reminds the learner to document the value, listen to the fictional patient, and report through the scenario's chain of supervision.

| Alert test | Fictional input | Expected output | Pass? |
|---|---:|---|---|
| Within assigned range | 84 | Check mark | |
| Report branch | 108 | R | |

## Explain your design

Which block stores a value? __________________________________________________

Which block makes a decision? ________________________________________________

Why is this program a simulator rather than a medical device?

[[lines: 3]]

Name one nursing-related role that uses monitored data. What does that worker do with the information?

[[lines: 3]]

## Equal evidence routes

- [ ] Physical micro:bit
- [ ] MakeCode browser simulator
- [ ] Paper block trace supplied by the teacher

The route does not change the score. Evidence is the tested logic and explanation.
