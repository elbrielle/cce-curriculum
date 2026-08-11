# Day 3: Build a Vital-Signs Training Simulator
<!-- CCE DAILY CONTRACT START -->
## Daily Learning Contract

- **Topic:** Training Simulation
- **Objective:** Students will identify how nursing workers use monitored data by building and testing a fictional simulator and explaining the career connection.
- **TEKS:** d(1)(C)
- **Demonstration of Learning:** Vital Signs Simulator Build and Test record, nursing-work connection, and screenshot, share link, or paper trace.
<!-- CCE DAILY CONTRACT END -->
## Lesson Overview

| | |
|---|---|
| **Time** | 50 minutes |
| **Objectives** | Identify four vital-sign tools from the workbook source; build and test a MakeCode program that displays fictional heart-rate and temperature values; explain the simulator boundary |
| **TEKS** | d(1)(C) |
| **5E Phases** | Engage: Warm-Up, Explore: tool research, Explain: MakeCode model, Elaborate: build and test, Evaluate: boundary check |
| **Deliverable** | Vital Signs Simulator Build and Test record plus screenshot, share link, or paper trace |
| **Materials** | FYF p. 60, Climber Notes slide 2, MakeCode, Vital Signs Simulator Build and Test, micro:bits optional |

## Warm-Up (5 min)

**WARM-UP:** What is the difference between a device that displays a number and a device that measures a person?

Establish the boundary before students code: the micro:bit program displays assigned fictional numbers. It is not medical equipment and does not measure, diagnose, or recommend care.

## Activity 1: Tools and Data (8 min)

**Source:** (FYF p. 60: "Vitals in Motion," Step 1) and (Climber Notes: "Vitals in Motion," slide 2)

Students match the blood pressure cuff, pulse oximeter, digital thermometer, and stopwatch to what each tool is used to measure. The source chart prepares students to interpret the fictional cards on Day 4. No student health data are collected.

## Activity 2: MakeCode Model (10 min)

Use the [Vital Signs Simulator Build and Test](../../resources/worksheets/2sw-wk3-vital-signs-simulator-build.pdf). Demonstrate only Button A:

The matching Canvas Student Guide includes the completed Button A visual. This is the required model; the teacher does not need to create a screenshot.

1. `on button A pressed`
2. set `heartRate` to `pick random 60 to 110`
3. `show number heartRate`
4. heart LED image, `pause 200 ms`, then a smaller or blank heart

Test in the on-screen simulator. Students then transfer the pattern to Button B with a temperature code from 970 to 1005. In this build, 986 represents 98.6°F.

## Activity 3: Build, Test, and Explain (22 min)

Students use one equal route:

- physical micro:bit,
- MakeCode browser simulator, or
- paper block trace.

Default setup is pairs with one connected device per pair. Assign Driver and Code Reader, then switch roles after Button A passes. Each student completes a test explanation; each pair may submit one screenshot or share link. If paper is the response route, provide one two-page build-and-test guide per student.

Active-monitoring laps:

1. Button A displays a fictional heart-rate value.
2. Button B displays a fictional temperature code.
3. The student can explain where the values came from and why the program is not a medical device.

Students who finish add a simulation alert: if heart rate is greater than 100, display `R` for report; otherwise display a check mark. The alert is a classroom handoff rule, not a diagnosis.

**Safe trim:** Cut the optional alert and pulse-animation refinement first. Protect both button tests, the simulator boundary, and the nursing-role connection. Reserve the final four minutes to save the artifact, return optional hardware, close MakeCode, and collect records.

**DOK 2:** Why does testing the program with more than one value matter to a worker who depends on accurate information?

## Exit Ticket (5 min)

**EXIT TICKET** (Decision Tree / Branching Prompt) · [Printable PDF](../../resources/exit-tickets/2sw-wk3-day3-build-a-vital-signs-training-simulator.pdf):

The simulator displays `108` and then `R`.

1. Does the program prove a real person has a medical condition? **Yes / No**
2. What should the learner document from the simulation?
3. If the fictional patient also reports a concerning symptom, which branch comes next: ignore, diagnose, or make a supervised handoff? Explain. *(d(1)(C))*

## Differentiation

- **Support:** Provide the Button A blocks as a screenshot and ask students to complete Button B.
- **Extension:** Add an A+B button that displays `SIM` before any value, or test a deliberate out-of-range input and revise the branch.
- **ELL:** Pre-teach simulator = simulador, value = valor, measure = medir, variable = variable, report = reportar. Students may explain the block sequence orally before writing.
