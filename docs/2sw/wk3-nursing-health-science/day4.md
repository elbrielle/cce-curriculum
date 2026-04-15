# Day 4: Vital Signs Monitor — Test + Present

## Lesson Overview

| | |
|---|---|
| **Time** | 50 minutes |
| **Objectives** | Refine the micro:bit vital signs monitor with an alarm feature; test with another team; present the device with a 1-minute connection to a real nursing career |
| **TEKS** | d(1)(C), d(2)(A) |
| **Deliverable** | Refined MakeCode program (Button A + B + alarm feature) + 1-minute team demo + connection to specific nursing career |
| **Materials** | Chromebooks, micro:bit devices (continue from Day 3), MakeCode, optional LEGO bricks for housing prototype, projector |

---

## Warm-Up (5 min)

**WARM-UP: If your vital signs monitor showed an abnormal reading, what would a nurse do next?**

Take 2-3 responses. Bridge: nurses act on data. The monitor is just the messenger. Today students add an ALARM feature so their monitor can flag abnormal readings, just like a real hospital monitor.

---

## Activity 1: Add the Alarm Feature (15 min)

**Source:** MakeCode + Day 3 student program

Students return to their Day 3 MakeCode programs. Today's add-on: an alarm that triggers when the heart rate is too high or too low.

Walk through the logic on the projector:

1. After `show number heartRate`, add an **`if`** block from Logic
2. Inside the if condition: `heartRate > 100 OR heartRate < 60`
3. If true: **`play tone middle C for 1 beat`** + **`show icon`** (sad face or skull)
4. Add `clear screen` after 2 seconds to reset

Students implement the alarm. Then they extend the program by:

- **Randomizing the heart rate** with `pick random 50 to 110` so the alarm sometimes triggers
- **Adding a "shake to reset"** block from Input → on shake → set heartRate to 75

Teams test the alarm by shaking the micro:bit until they get an abnormal reading.

!!! tip "Facilitation Tip"
    The alarm is the "wow" feature. Students who add the alarm AND get it to trigger feel like real engineers. Encourage teams to make the alarm DRAMATIC, flashing LEDs, loud tones, scary icons.

---

## Activity 2: Optional LEGO Housing (10 min)

**For teams with extra time:** if LEGO bricks are available, teams build a physical housing for their micro:bit. The housing should:

- Hold the micro:bit securely
- Allow access to both buttons
- Look like a real medical device (the team can pretend it's worn on a wrist or attached to a patient)

This adds an Engineering Design Process layer and connects to the manufacturing of medical devices (a nice tie-back to the 1st Six Weeks Manufacturing cluster).

If LEGOs are not available, teams sketch their housing on paper and label the design choices.

---

## Activity 3: Team Presentations (15 min)

Each team presents their vital signs monitor to the class in 1 minute. The presentation must cover:

1. **Demo:** Show Button A and Button B working. Show the alarm if you built it.
2. **Vital signs monitored:** Name the two vital signs your monitor tracks
3. **Connection to a real nurse:** Name a specific nursing career (CNA, LVN, RN, Patient Care Technician) and explain how this monitor connects to what they do every day
4. **Singley Academy connection:** Connect the project to the Patient Care Technician certification offered at Singley

The class evaluates each presentation using a quick rubric (visible on the projector):

- Does the monitor work?
- Did the team name a real nursing career?
- Did the team explain HOW the monitor connects to nursing work?

**DOK 4:** If you were designing a training program for new nursing students, how would you use technology like the micro:bit monitors you built today? What would students learn from BUILDING a monitor before they use a real one with patients?

---

## Exit Ticket (5 min)

**EXIT TICKET:** Explain one way your micro:bit project simulates real medical technology and connect it to a specific nursing career (e.g., "My alarm feature simulates the alert system that an RN uses in the ICU"). *(d(1)(C), d(2)(A))*

---

## Differentiation

- **Support:** Provide an alarm code template. Students drag in pre-built blocks instead of writing the if/then logic from scratch.
- **Extension:** Add a third vital sign (respiration rate) using the accelerometer. Or program a "patient profile" with the team's names that displays on startup.
- **ELL:** Visual presentation template with Spanish key terms. Pre-teach: Alarm = Alarma, Reset = Reiniciar, Demo = Demostración. Pair ESL students with bilingual peers as a co-presenter.
