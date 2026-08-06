# Day 3: Help Desk Simulator (MakeCode Day 1)

## Lesson Overview

| | |
|---|---|
| **Time** | 50 minutes |
| **Objectives** | Set up micro:bit + MakeCode; build a basic 3-step troubleshooting program; load the program onto the micro:bit and test it |
| **TEKS** | d(4)(B) |
| **5E Phases** | Engage: Warm-Up · Explain: MakeCode setup and starter program · Explore: 3-step troubleshooting build · Evaluate: Exit Ticket |
| **Deliverable** | MakeCode program with at least 3 troubleshooting steps that displays text on the micro:bit when Button A is pressed |
| **Materials** | micro:bit devices (1 per team of 2-3, so 10-15 for a class of 30; with none, the whole day runs in the MakeCode simulator), data-capable USB cables (1 per board), Chromebooks, MakeCode for micro:bit, printed Help Desk scenario cards ([Printable PDF](../../resources/worksheets/wk4-help-desk-scenario-cards.pdf)), projector |

---

## Warm-Up (5 min)

**WARM-UP: If someone brought you a computer that would not turn on, what are the FIRST 3 things you would check, in order?**

Quick share. Listen for: "Is it plugged in?" "Is the power button working?" "Is the screen on?" Bridge: "What you just did is troubleshooting, and it has a specific ORDER. Today you build a tool that displays troubleshooting steps in order, just like real help desk software."

---

## Activity 1: micro:bit + MakeCode Setup (10 min)

Distribute micro:bit devices to teams of 2-3 students. Each team gets:

- 1 micro:bit
- 1 USB cable
- A Help Desk scenario card ([Printable PDF](../../resources/worksheets/wk4-help-desk-scenario-cards.pdf)): printer not working, Wi-Fi disconnected, software crashing, computer won't turn on, or password reset

Walk students through MakeCode setup on the projector:

1. Open [makecode.microbit.org](https://makecode.microbit.org) in Chrome.
2. Click **"New Project"** and name it (e.g., "Help Desk Tool").
3. Look at the workspace: **left side** = micro:bit simulator, **middle** = block category drawer, **right** = workspace.
4. Connect the micro:bit USB cable to the Chromebook.
5. Click the three dots next to the **Download** button and choose **"Connect device"**. Pick the micro:bit from the browser's device list and click Connect. This WebUSB pairing flow is the normal path on a district-managed Chromebook, not a workaround, and each Chromebook only needs it once for the week.
6. Click **"Download"** in the bottom-left. The code now flashes straight to the paired board.

!!! warning "Before Monday: Device Prep"
    Count your micro:bits and USB cables two weeks out. A class of 30 needs 10 to 15 boards at teams of 2-3, plus one data-capable cable per board. Decide power now: boards run fine tethered to the Chromebook over USB for the whole period, and battery packs (2 AAA cells per board) are only needed if Day 4 pairs carry devices away from their desks. Then update the firmware across the fleet in one sitting. Download the current DAPLink firmware once from [microbit.org/get-started/user-guide/firmware](https://microbit.org/get-started/user-guide/firmware/), then hold the RESET button while plugging each board in so it mounts as MAINTENANCE instead of MICROBIT, drag that firmware file onto the MAINTENANCE drive, and unplug when it remounts as MICROBIT. Fifteen boards take about twenty minutes and this clears the most common pairing failure before it costs you class time. Finish by running one full Connect device and Download on an actual student Chromebook, signed in as a student, not on the teacher machine.

!!! tip "No micro:bits? Run the Simulator"
    The simulator on the left side of the MakeCode workspace runs the identical program, buttons and LED display included. Students click Button A and Button B on screen. Activities 2 and 3 both work with no hardware at all. With fewer boards than teams, run teams of 4 and rotate who holds the device, or put half the teams in the simulator today and swap them onto boards on Day 4.

---

## Activity 2: Build Your First Program — Display a Welcome Message (10 min)

Project the MakeCode workspace and walk students through building this exact starter program:

1. From the **Basic** category, drag a `show string` block into the `on start` area. Type a welcome message: "Help Desk Ready"
2. From the **Input** category, drag an `on button A pressed` block into the workspace.
3. From **Basic**, drag a `show string` block into the `on button A pressed` area. Type the first troubleshooting step: "Step 1: Restart"
4. Click **Download** and load it to the micro:bit.
5. Press Button A on the micro:bit. Students should see "Step 1: Restart" scroll across the LED display.

**Chunking:** One block at a time on the projector, each with its purpose named before it is demonstrated: `show string` puts words on the screen, `on button A pressed` waits for the user.

**Visual checkpoint:** Hold up your micro:bit when "Step 1: Restart" is showing. Verify every team got it before moving on. Teams that needed help clearing the checkpoint start Activity 3 from the printed starter blocks ([Printable PDF](../../resources/worksheets/wk4-makecode-starter-blocks.pdf)), which lists all sixteen blocks in drag order so those teams only have to type their own step text.

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
- **Scenario: Software crashing**
  - Step 1: "Close and reopen app"
  - Step 2: "Restart computer"
  - Step 3: "Check for updates"
- **Scenario: Computer won't turn on**
  - Step 1: "Check power cable"
  - Step 2: "Check power button"
  - Step 3: "Hold power 10 sec"
- **Scenario: Password reset**
  - Step 1: "Check caps lock"
  - Step 2: "Use forgot password link"
  - Step 3: "Call IT to reset"

To build the cycling logic, students use a **variable** called `step` that increments each time Button A is pressed:

1. From **Variables**, create a variable `step` and set it to 1 in `on start`.
2. Use `if/then/else` blocks (from **Logic**) inside `on button A pressed` to display a different message for each value of `step`.
3. Put a `change step by 1` block **below** the whole if block, not above it, so the board shows the current step and then counts up to the next one.

Walk between teams. The trickiest part is the `if/then` logic, sit with teams that get stuck. The predictable bug is a `change step by 1` sitting above the if block, which makes the first press of Button A skip straight to Step 2. The printed starter blocks ([Printable PDF](../../resources/worksheets/wk4-makecode-starter-blocks.pdf)) put the sixteen blocks in the order that avoids it.

!!! tip "Facilitation Tip"
    Some teams will get frustrated with the if/else nesting. Tell them: "If you can get just TWO steps working today (Step 1 and Step 2), you have done well. We refine tomorrow." Don't push perfection on day 1.

**DOK 2:** How would you describe the logical order of your troubleshooting steps and why that order matters?

---

## Exit Ticket (5 min)

**EXIT TICKET** (Decision Tree / Branching Prompt) · [Printable PDF](../../resources/exit-tickets/1sw-wk4-day3-help-desk-simulator-makecode-day-1.pdf):

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

- **Support:** Hand out the printed starter blocks ([Printable PDF](../../resources/worksheets/wk4-makecode-starter-blocks.pdf)), which list every block in drag order with the variable and Button A logic already worked out, so students modify only the text strings. Before programming, give these students the troubleshooting step sort cards ([Printable PDF](../../resources/worksheets/wk4-troubleshooting-step-sort-cards.pdf)) and have them physically arrange their scenario's three steps in order first.
- **Extension:** Add a sound effect (use the **Music** blocks) for "FIXED!" or for advancing to the next step. Add an LED animation that shows progress (1 LED for step 1, 2 LEDs for step 2, etc.).
- **ELL:** Allow ELL students to write troubleshooting step text in Spanish. Pre-teach: Reiniciar = Restart, Verificar = Check, Cable de poder = Power cable. Use the bilingual step sort cards ([Printable PDF](../../resources/worksheets/wk4-troubleshooting-step-sort-cards-bilingual.pdf)), which print each step in English and Spanish on the same card.
