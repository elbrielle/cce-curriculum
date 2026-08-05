# Day 3: Vital Signs Monitor — Build Phase

## Lesson Overview

| | |
|---|---|
| **Time** | 50 minutes |
| **Objectives** | Complete "Vitals in Motion" Step 1 team research on the four vital signs tools; build a working vital signs monitor in MakeCode using the micro:bit; program Button A to display heart rate and Button B to display temperature with an LED animation |
| **TEKS** | d(1)(C) |
| **5E Phases** | Engage: Warm-Up · Explore: Vitals in Motion Step 1 tool research · Explain: MakeCode demo · Explore: Student build time · Evaluate: Exit Ticket |
| **Deliverable** | Completed "Vitals in Motion" Step 1 answers (FYF p. 60) + working MakeCode program with both buttons functional (saved as student.hex file or screenshot of finished code blocks) |
| **Materials** | Chromebooks, micro:bit devices (1 per team of 2-3), MakeCode website ([makecode.microbit.org](https://makecode.microbit.org)), USB cables, *Find Your Future* workbook p. 60, Climber Notes deck "Vitals in Motion" (slides 2-4), projector |

---

## Warm-Up (5 min)

**WARM-UP: What are vital signs? Name as many as you can. Hint: think about what a nurse checks at the start of every doctor's visit.**

Take responses. Students should name: heart rate (pulse), temperature, blood pressure, respiration rate (breathing). If they miss respiration rate, name it for them.

---

## Activity 1: "Vitals in Motion" Team Research (8 min)

**Source:** (FYF p. 60: "Vitals in Motion", Step 1), a Career Climb activity

Open the workbook to page 60. Read the scenario together: not all nurses work in the same place every day. Travel nurses move from city to city and step in wherever care is needed most, including community events. It is a bright Saturday morning at a community summer fun run, families and neighbors are walking and jogging, a medical tent is set up near the finish line, and the student is the travel nurse on duty. The job listed on the page is to collect and record vital signs, use medical tools correctly, communicate clearly and calmly, and rotate roles and document findings.

**Step 1: Team Research and Share.** Students pair up or join a small group and answer the page's five questions in the workbook. Project the Climber Notes deck while they work (Climber Notes: "Vitals in Motion", slides 2-4), which carries the tool reference table and the fever, blood pressure, and pulse oximeter charts:

- What is blood pressure, and what can it indicate?
- What is the correct way to use a blood pressure cuff?
- What does a pulse oximeter measure? Why is it important?
- What is the correct way to use a pulse oximeter?
- What does body temperature tell you about a person's condition?

Students take these readings on each other on Day 4. Today the research is the preparation for that, and it is also the specification for the device they are about to build.

**Project specifications** (project on the board):

- Press Button A → display a simulated heart rate (number between 60-100) + LED animation showing "pulse"
- Press Button B → display a simulated temperature (number between 97.0-99.5) + LED animation showing "thermometer"
- Bonus (Day 4): Add an alarm if the heart rate is above 100 or below 60

Name the local tie before students open MakeCode. Patient Care Technicians monitor vital signs every shift, and the Singley Academy labs run programmable patient simulators whose manikins display changing vital signs to replicate critical emergencies. The micro:bit build is the classroom-scale version of that machine.

---

## Activity 2: MakeCode Demo (10 min)

Open [makecode.microbit.org](https://makecode.microbit.org) on the projector. Walk students through:

1. **Create a new project** named "Vital Signs Monitor"
2. **Drag in `on button A pressed`** from the Input drawer
3. **Inside the button block, drag in `show number`** from Basic
4. **Set the number to a variable** called `heartRate` initialized to 75
5. **Test on the simulator:** click Button A and watch the LED grid display "75"

Then add the LED animation:

6. **Show LEDs** block from Basic, draw a simple heart pattern
7. **Pause 200ms**
8. **Show LEDs** with empty heart
9. **Loop 3 times** for the pulse effect

Walk students through saving the project and downloading it to the micro:bit (drag the .hex file to the MICROBIT drive).

!!! tip "Facilitation Tip"
    Don't spend more than 10 minutes on the demo, the goal is to get students building, not watching. Demonstrate the heart rate (Button A) only, then let students build Button B independently using the same pattern. They learn faster by doing.

---

## Activity 3: Student Build Time (22 min)

Students work in teams of 2-3 with one micro:bit per team. They:

1. **Recreate the Button A heart rate display** using the demo as reference
2. **Add Button B for temperature:** `on button B pressed` → `show number` (temperature variable initialized to 98.6) → LED thermometer animation
3. **Test both buttons** on the simulator first, then download to the physical micro:bit
4. **Show the teacher** when both buttons work. This is the Day 3 checkpoint

**Active Monitoring:** Walk a fixed pathway with one target per lap rather than drifting toward raised hands, marking the 3-checkpoint rubric as you go:

- Lap 1 target: Button A displays a heart rate number ✓
- Lap 2 target: Button A shows an LED animation ✓
- Lap 3 target: Button B displays a temperature number ✓

Pivot condition: if more than a handful of teams miss the lap 2 target, stop and reproject the pause block to the whole room instead of fixing it team by team.

Teams that finish early add a third button (touch logo) for a bonus vital sign or build the Day 4 alarm feature.

**DOK 2:** How would you describe the connection between the programming you are doing today and the technology that real nurses use in hospitals?

!!! tip "Facilitation Tip"
    The most common error is forgetting to set the variable. Tell students: "If your number doesn't show up, your variable is empty. Initialize it to a number first." Project the variable initialization as the troubleshooting reference.

---

## Exit Ticket (5 min)

**EXIT TICKET** (Decision Tree / Branching Prompt) · [Printable PDF](../../resources/exit-tickets/2sw-wk3-day3-vital-signs-monitor-build-phase.pdf):

My role today: **Patient Care Technician** (a nursing career in Health Science)

Scenario: During my shift, I press Button A on my vital signs monitor and see a heart rate of **130** (way above normal).

Step 1: What does my role do FIRST in the next 30 seconds?

   ___________________________________________________________________

Step 2: Which OTHER Health Science role do I need to tell, and why? (Pick one: CNA / LVN / RN / NP / doctor)

   I need to tell: _______________________

   Because: ________________________________________________________

Step 3: Branch on the patient response —

   IF the patient is AWAKE and talking, what do I do next? ___________________________________________________________________

   IF the patient is NOT responding, what do I do next? ___________________________________________________________________

*(d(1)(C))*

Show the teacher your working program before leaving.

---

## Differentiation

- **Support:** Provide a MakeCode starter file with the variable already initialized and the Button A block already in place. Students just complete Button B.
- **Extension:** Add a third button (logo touch) for blood pressure (display two numbers, systolic and diastolic). Or add a randomization so the heart rate changes each press. Teams that finish both buttons well ahead of the checkpoint start the "Ultrasound Detectives" enrichment (FYF pp. 64-68) with a partner, working Step 1 (match the three ultrasound types to their purposes) and Step 2 (read a practice scan and say what clues led to the guess) while the teacher projects the scan images (Climber Notes: "Ultrasound Detectives", slides 2-4).
- **ELL:** Visual MakeCode cheat sheet with screenshots of each block. Pair ESL students with bilingual peers as the "code reader" while they build. Pre-teach: Heart Rate = Frecuencia Cardíaca, Temperature = Temperatura, Button = Botón, Display = Mostrar.
