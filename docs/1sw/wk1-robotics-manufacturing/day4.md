# Day 4: Sphero Factory Floor + Task Bot in Action (Part 1)

## Lesson Overview

| | |
|---|---|
| **Time** | 50 minutes |
| **Objectives** | Set up Sphero RVR+ teams; learn basic SpheroEDU block-based programming; begin the H&L "Task Bot in Action" team activity at Kaleido-Crayons Factory |
| **TEKS** | d(1)(C) |
| **Deliverable** | Sphero teams driving basic patterns + Task Bot role assignments + Step 1 (read shift notes) and Step 2 (research) complete |
| **Materials** | Sphero RVR+ robots (1 per team of 3-4), SpheroEDU app, painter's tape factory floor course, cardboard obstacles, H&L Workbook Ch 14 (pp. 240-242), Chromebooks, projector |

---

## Warm-Up (5 min)

**WARM-UP: Have you ever seen a real industrial robot in person (at a factory tour, on a video, or in a YouTube short)? What was it doing?**

Quick share. If you have access, queue up a 60-second YouTube clip of FANUC robots assembling cars. Bridge: "Today you become the team that runs a factory floor, but with a much smaller robot called a Sphero."

---

## Activity 1: Set Up the Factory Floor Course (8 min)

Before class, lay out a "factory floor" course on the classroom floor using painter's tape:

- A **Start zone** at one end (Point A)
- A **Delivery zone** at the other end (Point B), about 6-8 feet away
- 2-3 **obstacles** in the path (cardboard boxes, blocks, books)
- A **straight path** for the first run, then add complexity later

Distribute Sphero RVR+ robots, one per team of 3-4 students. Assign roles within each team:

- **Driver**: Runs the SpheroEDU app
- **Coder**: Builds the block-based program
- **Observer**: Watches the robot's behavior and calls out problems
- **Connector**: Pairs the Sphero to the Chromebook (this is often the trickiest part)

Walk students through Sphero pairing:

1. Power on the Sphero RVR+ (button on the rear).
2. Open SpheroEDU app on the Chromebook.
3. Tap "Connect" → select the Sphero by its name.
4. Confirm the LED indicator goes solid (not blinking).

!!! warning "Common Issue"
    Sphero pairing fails if multiple teams try to connect to the same robot. Color-code the robots and the Chromebooks (sticker matching) so each team always works with the same Sphero.

---

## Activity 2: SpheroEDU Block Programming Basics (15 min)

Project the SpheroEDU app on the screen. Walk students through the **block-based programming interface** one block at a time:

1. **Roll**: Make the Sphero drive forward at a set speed for a set time. Show how to adjust speed (0-255) and duration (seconds).
2. **Heading**: Set the direction the robot drives (0° = forward, 90° = right, 180° = backward, 270° = left).
3. **Stop**: Stop the robot.
4. **Wait**: Pause the program for a set time.

Students follow along on their Chromebooks. After each block, do a quick visual check: "Hold up a thumb if your block is on screen."

**Mini-challenge:** Have each team write a 3-block program that drives the Sphero forward 3 seconds, turns 90 degrees, and drives forward 2 seconds. Run it on the factory floor course and observe.

!!! tip "Facilitation Tip"
    The first run will fail for most teams. Sphero overshoots, undershoots, or turns the wrong way. This is GOOD. Tell students: "This is debugging. Real software developers spend more time debugging than writing code." Encourage iteration, not perfection.

---

## Activity 3: Begin H&L "Task Bot in Action" — Read the Brief (15 min)

**Source:** H&L Workbook Ch 14, pp. 240-242, "Task Bot in Action" (Career Lab activity, Steps 1-2)

Open the workbook to page 240. Read the scenario together: students are the production team at Kaleido-Crayons Factory. The robotic crayon-sorting machine is malfunctioning, and production is falling behind. Two specific problems:

- **Problem #1: Color Confusion**: Boxes are arriving with too many crayons of the same color or missing colors entirely. The robot's color sensors can't distinguish certain crayons under bright lights.
- **Problem #2: Slowpoke Robot**: The robot's arms miss crayons, causing delays. It moves too slowly and backs up the production line.

**Step 1: Read the Shift Notes (workbook p. 241).** Have students read the Supervisor Shift Notes from J. Vega's 2nd shift. The notes contain the critical clues:

- The color sensor was REPLACED last week, and the new one might not work as well under factory lights.
- A software update happened at 4:00 PM.
- Three new people are being trained this week.
- The robotic arm's rubber belt was recently changed and might be the wrong size.
- New packaging might be a factor.

**Waste + Impact Report:** 68 boxes hand-fixed, 20 boxes pulled from shipping, 430 crayons damaged, 26 minutes of stopped production caused 1.5 hours of downstream delays, 1 full pallet of 120 boxes delayed. Customer is upset (this is the second time this month).

**Step 2: Research and Investigate, Assign Roles (workbook p. 242).** Each team member chooses ONE of the four production team roles:

- **Shift Supervisor**: Leads team discussions and keeps everyone on track.
- **Quality Control Specialist**: Makes sure product quality meets standards.
- **Maintenance Tech**: Considers mechanical issues with equipment.
- **Packaging Supervisor**: Oversees all packaging of the product.

Teams write down who is playing which role. Then, as a team, they begin researching factory sorting and packaging equipment online (10 min). The workbook prompts them to consider:

- Why might these problems be happening?
- How can the robotic sorter be improved without shutting down the factory?
- How can the problem be fixed without buying a brand-new robotic sorter?
- How do other factories handle problems like this?

**DOK 3:** What conclusions can you draw about the connection between Problem #1 (Color Confusion) and the shift notes about the new color sensor and the software update?

---

## Exit Ticket (2 min)

**EXIT TICKET** (Decision Tree / Branching Prompt) · [Printable PDF](../../resources/exit-tickets/1sw-wk1-day4-sphero-factory-floor-task-bot-in-action-part-1.pdf):

My Task Bot role today: _______________________ (Shift Supervisor, Quality Control Specialist, Maintenance Tech, or Packaging Supervisor)

Problem: Kaleido-Crayons just reported MORE Color Confusion boxes at 5:00 PM, one hour AFTER the 4:00 PM software update.

Step 1: What does MY ROLE do FIRST in the next 15 minutes? One sentence:

   ___________________________________________________________________

Step 2: Which OTHER role on the team do I need to talk to right now, and why? (Pick ONE: Shift Supervisor / Quality Control Specialist / Maintenance Tech / Packaging Supervisor)

   I need to talk to: _______________________

   Because: ________________________________________________________

Step 3: What is ONE specific clue from the shift notes that points to a possible cause of Color Confusion? *(d(1)(C))*

   ___________________________________________________________________

---

## Differentiation

- **Support:** Provide pre-built SpheroEDU starter code (drive forward + stop) that students modify rather than build from scratch. For Task Bot, assign roles to students rather than letting them choose (extroverts get Shift Supervisor; detail-focused students get Quality Control).
- **Extension:** Sphero teams who master the basic 3-block program can add a 4th block (drive backward) and create a square pattern.
- **ELL:** Bilingual SpheroEDU command card (Roll = Rodar, Heading = Dirección, Stop = Detener, Wait = Esperar). Pair ELL students with bilingual peers when reading the Kaleido-Crayons shift notes.
