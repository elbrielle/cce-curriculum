# Day 4: Sphero Factory Floor + Robots for Crayons (Part 1)

## Lesson Overview

| | |
|---|---|
| **Time** | 50 minutes |
| **Objectives** | Set up Sphero RVR+ teams; learn basic SpheroEDU block-based programming; begin the "Robots for Crayons" team activity at Kaleido-Crayons Factory |
| **TEKS** | d(1)(C) |
| **5E Phases** | Engage: Warm-Up · Explain: SpheroEDU block walkthrough · Explore: Factory floor runs and Robots for Crayons case files · Evaluate: Exit Ticket |
| **Deliverable** | Sphero teams driving basic patterns + team role assignments + Steps 1-3 (problems, machine reference, shift notes) complete |
| **Materials** | Sphero RVR+ robots (1 per team of 3-4), SpheroEDU app, painter's tape factory floor course, cardboard obstacles, *Find Your Future* workbook pp. 200-202, Chromebooks, projector |

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

**Chunking:** Students follow along on their Chromebooks. Say what each block is for before you demonstrate it (Roll drives, Heading aims, Wait buys time, Stop protects the robot), and close each chunk with a quick visual check: "Hold up a thumb if your block is on screen." Do not release the next block until the thumbs are up. Note which block draws the most thumbs down; that block is the 3 minute re-teach at the start of Day 5.

**Mini-challenge:** Have each team write a 3-block program that drives the Sphero forward 3 seconds, turns 90 degrees, and drives forward 2 seconds. Run it on the factory floor course and observe.

!!! tip "Facilitation Tip"
    The first run will fail for most teams. Sphero overshoots, undershoots, or turns the wrong way. This is GOOD. Tell students: "This is debugging. Real software developers spend more time debugging than writing code." Encourage iteration, not perfection.

---

## Activity 3: Begin "Robots for Crayons" — Read the Brief (15 min)

**Source:** (FYF pp. 200-202: "Robots for Crayons", Steps 1-3), a Career Climb activity

**Step 1: Learn about Kaleido-Crayons (p. 200).** Students get into small groups of 3-4 and take turns reading the brief aloud. They are called in to a 24/7 factory where the robotic sorting machine is malfunctioning and production is falling behind. Two specific problems:

- **Problem #1: Color Confusion**: Boxes have repeated colors or missing colors. The robot struggles to tell similar colors apart, especially Sky Blue and Violet. Customers expect complete, accurate boxes.
- **Problem #2: Slowpoke Robot**: The robotic arm moves too slowly or misses crayons, so crayons fall, pile up, or jam the system. The line has already stopped twice. Delays slow the whole factory and waste materials.

**Step 2: How the Machines Work (p. 201).** This page is the team's technical reference, and it is where the answers hide. Read it as a group and have each team circle the causes that could match their two problems: color sensors read color by light reflection and are thrown off by uneven lighting, dust on the sensor, calibration errors, or low-quality replacement parts; robotic arms run on motors and belts and fail when a belt is too tight or too loose, when arm and conveyor speeds do not match, or when parts wear out; production lines need every part moving at the same speed, so slowing one part affects the whole system.

**Step 3: Read the Shift Notes (pp. 201-202).** Students read the Supervisor Shift Notes from J. Vega's 2nd shift and circle key details. The notes contain the critical clues:

- The color sensor was REPLACED last week, and the new one might not work as well under factory lights.
- A software update happened at 4:00 PM.
- Three new people are being trained this week.
- The robotic arm's rubber belt was recently changed and might be the wrong size.
- New packaging might be a factor.

**Waste + Impact Report (p. 202):** 68 boxes hand-fixed, 20 boxes pulled from shipping, 430 crayons damaged, two stops of 12 and 14 minutes for a total of 26 minutes that caused over 1.5 hours of downstream delay, 1 full pallet of 120 boxes pushed to the next day. The customer is unhappy, and this is the second wait this month.

**Assign team roles.** The workbook puts students in groups of 3-4 without naming jobs inside the group. Assign these four production roles anyway so every student has something to own when the plan gets written on Day 5:

- **Shift Supervisor**: Leads team discussions and keeps everyone on track.
- **Quality Control Specialist**: Makes sure product quality meets standards.
- **Maintenance Tech**: Considers mechanical issues with equipment.
- **Packaging Supervisor**: Oversees all packaging of the product.

Teams write down who is playing which role. Then each role rereads the shift notes through its own lens and marks the clues that belong to its job. Push teams with these questions:

- Why might these problems be happening?
- How can the robotic sorter be improved without shutting down the factory?
- How can the problem be fixed without buying a brand-new robotic sorter?
- Which clue belongs to your role, and which one is somebody else's problem?

**DOK 3:** What conclusions can you draw about the connection between Problem #1 (Color Confusion) and the shift notes about the new color sensor and the software update?

---

## Exit Ticket (2 min)

**EXIT TICKET** (Decision Tree / Branching Prompt) · [Printable PDF](../../resources/exit-tickets/1sw-wk1-day4-sphero-factory-floor-robots-for-crayons-part-1.pdf):

My production team role today: _______________________ (Shift Supervisor, Quality Control Specialist, Maintenance Tech, or Packaging Supervisor)

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

- **Support:** Provide pre-built SpheroEDU starter code (drive forward + stop) that students modify rather than build from scratch. For Robots for Crayons, assign roles to students rather than letting them choose (extroverts get Shift Supervisor; detail-focused students get Quality Control).
- **Extension:** Sphero teams who master the basic 3-block program can add a 4th block (drive backward) and create a square pattern.
- **ELL:** Bilingual SpheroEDU command card (Roll = Rodar, Heading = Dirección, Stop = Detener, Wait = Esperar). Pair ELL students with bilingual peers when reading the Kaleido-Crayons shift notes.
