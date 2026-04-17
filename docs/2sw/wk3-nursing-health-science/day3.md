# Day 3: Vital Signs Monitor — Build Phase

## Lesson Overview

| | |
|---|---|
| **Time** | 50 minutes |
| **Objectives** | Build a working vital signs monitor in MakeCode using the micro:bit; program Button A to display heart rate and Button B to display temperature with an LED animation |
| **TEKS** | d(1)(C) |
| **Deliverable** | Working MakeCode program with both buttons functional (saved as student.hex file or screenshot of finished code blocks) |
| **Materials** | Chromebooks, micro:bit devices (1 per team of 2-3), MakeCode website ([makecode.microbit.org](https://makecode.microbit.org)), USB cables, projector |

---

## Warm-Up (5 min)

**WARM-UP: What are vital signs? Name as many as you can. Hint: think about what a nurse checks at the start of every doctor's visit.**

Take responses. Students should name: heart rate (pulse), temperature, blood pressure, respiration rate (breathing). If they miss respiration rate, name it for them.

---

## Activity 1: The Challenge + Real-World Connection (8 min)

Introduce today's challenge:

> "Nurses monitor vital signs constantly, heart rate, temperature, blood pressure, oxygen levels. Modern hospitals use electronic monitoring systems to do this. Today you are going to BUILD a simplified vital signs monitor using your micro:bit. When you press Button A, it displays a simulated heart rate. When you press Button B, it displays a simulated temperature. This is how real medical technology works at a basic level."

Connect the project to the Singley Academy Nursing Science pathway. Patient Care Technicians use vital signs monitors every shift. Connect to the Day 1 Making Connections activity: most students named "thermometer" or "blood pressure monitor". Those are programmable devices.

**Project specifications** (project on the board):

- Press Button A → display a simulated heart rate (number between 60-100) + LED animation showing "pulse"
- Press Button B → display a simulated temperature (number between 97.0-99.5) + LED animation showing "thermometer"
- Bonus (Day 4): Add an alarm if the heart rate is above 100 or below 60

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

The teacher circulates with a 3-checkpoint rubric:

- Button A displays a heart rate number ✓
- Button A shows an LED animation ✓
- Button B displays a temperature number ✓

Teams that finish early add a third button (touch logo) for a bonus vital sign or build the Day 4 alarm feature.

**DOK 2:** How would you describe the connection between the programming you are doing today and the technology that real nurses use in hospitals?

!!! tip "Facilitation Tip"
    The most common error is forgetting to set the variable. Tell students: "If your number doesn't show up, your variable is empty. Initialize it to a number first." Project the variable initialization as the troubleshooting reference.

---

## Exit Ticket (5 min)

**EXIT TICKET** (Decision Tree / Branching Prompt):

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
- **Extension:** Add a third button (logo touch) for blood pressure (display two numbers, systolic and diastolic). Or add a randomization so the heart rate changes each press.
- **ELL:** Visual MakeCode cheat sheet with screenshots of each block. Pair ESL students with bilingual peers as the "code reader" while they build. Pre-teach: Heart Rate = Frecuencia Cardíaca, Temperature = Temperatura, Button = Botón, Display = Mostrar.
