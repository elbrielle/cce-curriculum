# Day 4: Vital Signs Monitor — Test + Present

## Lesson Overview

| | |
|---|---|
| **Time** | 50 minutes |
| **Objectives** | Refine the micro:bit vital signs monitor with an alarm feature; take and record a partner's vital signs after activity and after rest as a travel nurse; write a five-part nursing report and present it with the working device |
| **TEKS** | d(1)(C) |
| **5E Phases** | Engage: Warm-Up · Explore: Alarm feature build · Extend: Vitals in Motion partner readings · Explain: Nursing report and team presentations · Evaluate: Exit Ticket |
| **Deliverable** | Refined MakeCode program (Button A + B + alarm feature) + completed Vital Signs Chart (FYF p. 61) + five-part nursing report + 1-minute team demo |
| **Materials** | Chromebooks, micro:bit devices (continue from Day 3), MakeCode, *Find Your Future* workbook p. 61, stopwatches or phone timers, shared digital thermometer and pulse oximeter if available, chart paper or poster board, projector |

---

## Warm-Up (5 min)

**WARM-UP: If your vital signs monitor showed an abnormal reading, what would a nurse do next?**

Take 2-3 responses and ask which reading would make the nurse act first. The monitor reports the number; the nurse decides what it means. Today students add an alarm for readings outside the programmed range.

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

## Activity 2: "Vitals in Motion" — Take and Record Vital Signs (10 min)

**Source:** (FYF p. 61: "Vitals in Motion", Steps 2-3)

Students return to the fun run scenario from Day 3 and now run it for real. Partners take turns as the **Travel Nurse** and the **Fun Run Participant (Patient)**, filling in the Vital Signs Chart on page 61. The chart has four rows (Blood Pressure, Temperature, Pulse Rate, Oxygen Level) and two columns (After Activity, After Rest).

Sequence for each pair:

1. The Participant does 60 seconds of activity in place (marching, jumping jacks, or a fast step). The Nurse runs a visible countdown.
2. The Nurse takes the readings immediately and records them in the **After Activity** column.
3. The Participant sits for 2 minutes. The Nurse takes the readings again and records them in the **After Rest** column.
4. **Step 3: Compare and Switch Roles.** Partners compare the two columns, talk about what changed and why they think it changed, then switch roles and repeat.

**Time, Voice, Body:** Post the three blocks before anyone stands up. Voice 1 for nurse and patient talk, Voice 0 during the counting so pulses can be counted accurately, a visible countdown for the 60 seconds of activity and again for the 2 minutes of rest, and shared tools go back in the station tray between teams.

!!! tip "Facilitation Tip"
    Missing equipment does not stop the activity. Every pair can fill the Pulse Rate row by counting the radial pulse at the wrist for 15 seconds and multiplying by four. If the campus health office can lend a digital thermometer and pulse oximeter, run one shared station and rotate pairs through it. Without a blood pressure cuff, leave that row blank and use the Climber Notes chart to discuss what the missing reading would have shown. Score the before-and-after comparison rather than the number of devices available.

---

## Activity 3: Nursing Report + Team Presentations (15 min)

**Source:** (FYF p. 61: "Vitals in Motion", Step 4)

**Step 4: Record Patient Information (5 min).** Travel nurses write up what happened so other medical staff can understand the situation quickly. Each team builds its report on chart paper or poster board with the workbook's five fields:

- **Scene Description:** Where are you? What is happening around you?
- **Patient Condition:** What symptoms did the patient describe? What were their vital signs?
- **Care Provided:** What steps did you take to assess the patient?
- **Reasoning:** How did activity affect the vital signs? What changed after resting?
- **Next Steps:** Does the patient need rest, water, cooling down, or further attention?

**Team presentations (10 min).** Each team gets 1 minute. They demo Button A, Button B, and the alarm if they built it, then read their nursing report as the script and close by naming a specific nursing career (CNA, LVN, RN, Patient Care Technician) and how the monitor connects to what that person does every shift.

The class evaluates each presentation using a quick rubric (visible on the projector):

- Does the monitor work?
- Does the nursing report answer all five fields?
- Did the team explain HOW the monitor connects to nursing work?

!!! tip "Facilitation Tip"
    If the class has more than ten teams, split into two circles so every team presents inside the ten minutes. Use the workbook's own class discussion prompts (FYF p. 61) to close if time allows: vital signs can look normal while a person still feels unwell, so how should a nurse balance the numbers against what the patient says?

**DOK 4:** If you were designing a training program for new nursing students, how would you use technology like the micro:bit monitors you built today? What would students learn from BUILDING a monitor before they use a real one with patients?

---

## Exit Ticket (5 min)

**EXIT TICKET** (Mini-Case / Scenario Application) · [Printable PDF](../../resources/exit-tickets/2sw-wk3-day4-vital-signs-monitor-test-present.pdf):

Scenario: Ms. Alvarez is an older patient in a DFW nursing home. Each morning at 7:00 AM, someone needs to check her vital signs (heart rate + temperature) and write them in her chart. The chart is reviewed by a nurse at 8:00 AM.

1. Which nursing career from the ladder fits THIS morning task BEST? Circle ONE: **CNA** / **LVN** / **RN** / **NP**

   One sentence why: ________________________________________________________

2. Name ONE feature of YOUR micro:bit monitor that would help this person do Ms. Alvarez's check accurately.

   My feature: _______________________. How it helps: ___________________________________________________________________

3. At 8:00 AM, a different Health Science role reviews the chart. Which role is that, and WHY is it different from the morning check role?

   Reviewer role: _______________________. Why different: ___________________________________________________________________

*(d(1)(C))*

---

## Differentiation

- **Support:** Provide an alarm code template. Students drag in pre-built blocks instead of writing the if/then logic from scratch. Provide a pre-labeled nursing report poster with the five field headings already written so the team only fills in content.
- **Extension:** Add a third vital sign (respiration rate) using the accelerometer. Or program a "patient profile" with the team's names that displays on startup. If LEGO bricks are available, teams build a physical housing that holds the micro:bit securely, leaves both buttons reachable, and looks like a wearable medical device, which ties the build back to the 1st Six Weeks Manufacturing cluster.
- **ELL:** Visual presentation template with Spanish key terms. Pre-teach: Alarm = Alarma, Reset = Reiniciar, Demo = Demostración. Pair ESL students with bilingual peers as a co-presenter.
