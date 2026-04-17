# Day 3: Help Desk Simulator (MakeCode Day 1)

## Lesson Overview

| | |
|---|---|
| **Time** | 50 minutes |
| **Objectives** | Set up micro:bit + MakeCode; build a basic 3-step troubleshooting program; load the program onto the micro:bit and test it |
| **TEKS** | d(4)(B) |
| **Deliverable** | MakeCode program with at least 3 troubleshooting steps that displays text on the micro:bit when Button A is pressed |
| **Materials** | micro:bit devices (1 per team of 2-3), USB cables, Chromebooks, MakeCode for micro:bit, Help Desk scenario cards, projector |

---

## Warm-Up (5 min)

**WARM-UP: If someone brought you a computer that would not turn on, what are the FIRST 3 things you would check, in order?**

Quick share. Listen for: "Is it plugged in?" "Is the power button working?" "Is the screen on?" Bridge: "What you just did is troubleshooting, and it has a specific ORDER. Today you build a tool that displays troubleshooting steps in order, just like real help desk software."

---

## Activity 1: micro:bit + MakeCode Setup (10 min)

Distribute micro:bit devices to teams of 2-3 students. Each team gets:

- 1 micro:bit
- 1 USB cable
- A Help Desk scenario card (printer not working, Wi-Fi disconnected, software crashing, computer won't turn on, password reset)

Walk students through MakeCode setup on the projector:

1. Open [makecode.microbit.org](https://makecode.microbit.org) in Chrome.
2. Click **"New Project"** and name it (e.g., "Help Desk Tool").
3. Look at the workspace: **left side** = micro:bit simulator, **middle** = block category drawer, **right** = workspace.
4. Connect the micro:bit USB cable to the Chromebook.
5. Click **"Download"** in the bottom-left to push code to the device.

!!! warning "Common Issue"
    Some Chromebooks block USB device access. If a student cannot download to the micro:bit, use the Web USB pairing flow (click "Connect device" in MakeCode). Some devices may need the firmware update, check the micro:bit support page if pairing fails.

---

## Activity 2: Build Your First Program — Display a Welcome Message (10 min)

Project the MakeCode workspace and walk students through building this exact starter program:

1. From the **Basic** category, drag a `show string` block into the `on start` area. Type a welcome message: "Help Desk Ready"
2. From the **Input** category, drag an `on button A pressed` block into the workspace.
3. From **Basic**, drag a `show string` block into the `on button A pressed` area. Type the first troubleshooting step: "Step 1: Restart"
4. Click **Download** and load it to the micro:bit.
5. Press Button A on the micro:bit. Students should see "Step 1: Restart" scroll across the LED display.

**Visual checkpoint:** Hold up your micro:bit when "Step 1: Restart" is showing. Verify every team got it before moving on.

---

## Activity 3: Build a 3-Step Troubleshooting Program (20 min)

Teams build a program that cycles through 3 troubleshooting steps for their assigned scenario. The program logic:

- When **Button A** is pressed, advance to the next troubleshooting step.
- When **Button B** is pressed, mark the problem "solved" (display "FIXED!").
- The display should show the current step number AND the step text.

**Scenario examples:**

- **Scenario: Printer not working**
  - Step 1: "Check power cable"
  - Step 2: "Check paper tray"
  - Step 3: "Restart printer"
- **Scenario: Wi-Fi disconnected**
  - Step 1: "Check Wi-Fi switch"
  - Step 2: "Restart router"
  - Step 3: "Forget and reconnect network"
- **Scenario: Computer won't turn on**
  - Step 1: "Check power cable"
  - Step 2: "Check power button"
  - Step 3: "Hold power 10 sec"

To build the cycling logic, students use a **variable** called `step` that increments each time Button A is pressed:

1. From **Variables**, create a variable `step` and set it to 1 in `on start`.
2. In `on button A pressed`, use a `change step by 1` block.
3. Use `if/then/else` blocks (from **Logic**) to display different messages based on the value of `step`.

Walk between teams. The trickiest part is the `if/then` logic, sit with teams that get stuck.

!!! tip "Facilitation Tip"
    Some teams will get frustrated with the if/else nesting. Tell them: "If you can get just TWO steps working today (Step 1 and Step 2), you have done well. We refine tomorrow." Don't push perfection on day 1.

**DOK 2:** How would you describe the logical order of your troubleshooting steps and why that order matters?

---

## Exit Ticket (5 min)

**EXIT TICKET** (Decision Tree / Branching Prompt):

My role today: **Help Desk Technician**. My Day 3 scenario card: _______________________

Step 1: When the user calls, what is the VERY FIRST troubleshooting step you tell them to try? (Use your micro:bit program.)

   ___________________________________________________________________

Step 2: Why is that step FIRST and not a later step? One sentence:

   ___________________________________________________________________

Step 3: Branch the next move based on the result:

   IF the user says the first step FIXED the problem, what do I do next? ___________________________________________________________________

   IF the user says the first step did NOT fix it, what do I do next? ___________________________________________________________________

*(d(4)(B))*

---

## Differentiation

- **Support:** Provide pre-built MakeCode starter code with the variable + button A logic already in place. Students just modify the text strings.
- **Extension:** Add a sound effect (use the **Music** blocks) for "FIXED!" or for advancing to the next step. Add an LED animation that shows progress (1 LED for step 1, 2 LEDs for step 2, etc.).
- **ELL:** Allow ELL students to write troubleshooting step text in Spanish. Pre-teach: Reiniciar = Restart, Verificar = Check, Cable de poder = Power cable.
