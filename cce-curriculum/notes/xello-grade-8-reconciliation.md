# Xello Grade 8 Reconciliation

**Status:** AUTHENTICATED INVENTORY COMPLETE. Findings use the live Bowie Middle School Completion Standards configuration viewed on 2026-08-06, the current S&S, the current daily plans, and Xello's official educator resources.

## The governing decision

Xello is not an interchangeable Friday supplement. District-configured Grade 8 completion standards form a required yearlong profile and planning sequence. The FYF realignment should have preserved that sequence while changing the workbook grounding.

The educator Completion Standards page is authoritative for:

- whether a task is assigned to Grade 8
- instructional time
- task prerequisites
- attached facilitator guides, worksheets, slide decks, and videos
- completion reporting

## Bowie Grade 8 completion inventory

The live district configuration assigns 24 tasks to Grade 8. These are the required Xello spine. A Xello activity that is useful but absent from this table may remain in a lesson as a supplement, but it must not be labeled as a Grade 8 completion standard.

| # | Configured task | Time | Grade 8 completion detail or prerequisite |
|---:|---|---:|---|
| 1 | Log in to Xello | 10 min | Account access; Xello supplies a first-day checklist, introduction deck, and student video |
| 2 | Matchmaker quiz | 30 min | Complete **After high school goal** first |
| 3 | Personality Style quiz | 20 min | Complete **Matchmaker quiz** first |
| 4 | Learning Style quiz | 20 min | No prerequisite shown |
| 5 | Add interests | 15 min | Add at least 1 interest |
| 6 | Add skills | 20 min | Add at least 1 skill |
| 7 | Favorite clusters | 40 min | Save at least 1 cluster |
| 8 | Life experiences | 10 min | Add at least 1 experience |
| 9 | Education experiences | 10 min | Add at least 1 experience |
| 10 | Volunteer hours | 15 min | Add at least 1 hour |
| 11 | Work experiences | 10 min | Add at least 1 experience |
| 12 | After high school goal | 15 min | Select 1 goal; this unlocks the intended Matchmaker sequence |
| 13 | Save careers | 30 min | Save at least 3 careers |
| 14 | Set goals | 20 min | Add at least 2 goals |
| 15 | 4-year course plan | 30 min | Course Planner task |
| 16 | Make plans | 30 min | Add at least 1 plan |
| 17 | Submit course requests | 20 min | Grade 8 only; coordinate timing with counseling |
| 18 | Parent 4-year course plan approval | 15 min | Grade 8 only; district due date shown as May 1, 2027 |
| 19 | Scholarship profile | 20 min | Complete the profile used to match scholarships |
| 20 | What is CTE? | Not shown | District custom lesson; requires a file attachment or text response |
| 21 | Biases and career choices lesson | 30 min | Grade 8 Xello lesson |
| 22 | Skills lesson | 35 min | Save at least 3 careers first |
| 23 | Explore career matches lesson | 35 min | Complete Matchmaker and save at least 3 careers first |
| 24 | Transition to high school lesson | 30 min | Save at least 5 interests first, even though the completion minimum for **Add interests** is 1 |

The course-planning tasks require counselor coordination rather than arbitrary placement on a career-cluster Friday. The parent approval deadline also makes this a calendar-dependent requirement.

### Items confirmed as not assigned to Grade 8

The live configuration does not assign these currently used items to Grade 8: **Mission Complete quiz, Skills Lab quiz, Learning styles lesson, Interests lesson, Decision making lesson, Exploring career factors lesson, Save quick sims, Careers and lifestyle costs lesson, Jobs and employers lesson, Time management lesson, Discover learning pathways lesson, School subjects at work lesson, Resume,** and **Job interviews lesson**. They may still be used as supplemental instruction when they fit the weekly objective.

## Current-repo audit

The current S&S has 36 week rows. Twenty-eight rows name at least one Xello standard or task. The year therefore still contains many Xello references, but the completion pathway is not coherent yet.

### Confirmed regressions

1. `CLAUDE.md` called the source the **Xello 7th-Grade Task List**. The district requirement for this implementation is the Grade 8 Completion Standards configuration.
2. 1SW Wk0 Day 5 offers five onboarding quizzes in one flex block: Matchmaker, Personality Style, Skills Lab, Learning Style, and Mission Complete. Those five tasks total 135 instructional minutes in the educator view, and two of them are not assigned to Grade 8. The block cannot run as written. Matchmaker also appears before its configured prerequisite, **After high school goal**.
3. Xello tasks are usually parked on a Day 5 beside H&L wrap-up and eDynamic work. That pattern treats Xello as leftover time instead of protecting completion time and prerequisites.
4. Task names drift across files: `Life Experience` / `Life Experiences`, `Education Experience` / `Education Experiences`, `Interests Lesson`, `Save Careers`, and similar labels must be reconciled against the exact configured names.
5. Several lesson plans say “7th-grade task list.” Those claims must be corrected only after the Grade 8 inventory confirms the exact task and resource.
6. The S&S and lesson plans use H&L localized salary as a dependency in several blocks. Xello is now the default district source for localized salary information; BLS or CareerOneStop remains the independent check.

## Official educator resources already located

Xello's public educator library exposes downloadable prerequisite and lesson-resource PDFs. These links are reference inputs for the reconciliation; licensed classroom copies ultimately belong in Canvas.

### Prerequisite guides

- [Matchmaker Assessment](https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/Matchmaker.pdf)
- [My Personality Styles](https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/Personality-Styles.pdf)
- [My Learning Styles](https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/Learning-Styles.pdf)
- [My Interests](https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/Interests.pdf)
- [Introduction to About Me](https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/About-Me.pdf)
- [My Career Clusters](https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/My-Career-Clusters.pdf)
- [My Experiences](https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/Experiences.pdf)
- [My Careers](https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/Careers.pdf)
- [My Goals](https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/Goals.pdf)
- [My Plans](https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/Plans.pdf)
- [My College Fair Preparation](https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/College-Fair-Prep.pdf)

### Lesson resources

- [Learning Styles](https://help.xello.world/en-us/Content/Resources/PDFs/Lesson-Resources-6-12/Explore-Learning-Styles.pdf)
- [Study Skills and Habits](https://help.xello.world/en-us/Content/Resources/PDFs/Lesson-Resources-6-12/Study-Skills-Habits.pdf)
- [Plans](https://help.xello.world/en-us/Content/Resources/PDFs/Lesson-Resources-6-12/Plans.pdf)
- [Biases and Career Choices](https://help.xello.world/en-us/Content/Resources/PDFs/Lesson-Resources-6-12/Biases-Career-Choices.pdf)
- [Skills](https://help.xello.world/en-us/Content/Resources/PDFs/Lesson-Resources-6-12/Skills.pdf)
- [Explore Career Matches](https://help.xello.world/en-us/Content/Resources/PDFs/Lesson-Resources-6-12/Explore-Career-Matches.pdf)
- [Transition to High School](https://help.xello.world/en-us/Content/Resources/PDFs/Lesson-Resources-6-12/Transition-to-High-School.pdf)

Xello also publishes [Teaching Resources for Xello 6-12](https://help.xello.world/en-us/content/Get-Started/Educator/Teaching-Resources/GS_Teaching-Resources.htm) and an official [Video Resources Overview](https://help.xello.world/en-us/Content/Get-Started/Xello-Administrator/Video-Resources-Overview.htm). Use the provided downloads and official shareable video links instead of capturing hosted streams.

## Reconciliation result

The current S&S names 14 of the 24 Grade 8 requirements at least once, allowing singular/plural label drift. It omits **Log in to Xello, After high school goal, Set goals, Submit course requests, Parent 4-year course plan approval, Scholarship profile, Biases and career choices lesson, Skills lesson, Explore career matches lesson,** and **Transition to high school lesson**.

The repair must happen in this order:

1. Replace the Wk0 quiz pileup with a short access/setup block and the prerequisite **After high school goal**.
2. Place Matchmaker before Personality Style and before Explore Career Matches.
3. Place Save Careers early enough to unlock Skills and Explore Career Matches.
4. Put course planning, course requests, and parent approval on the counseling calendar.
5. Spiral profile updates across the year instead of treating them as leftover Friday work.
6. Label non-Grade 8 items **Xello supplemental**, just as eDynamic, Canva, and Code.org are labeled supplemental.
7. Add completion evidence to the six-weeks grading map without turning every Xello click into a separate grade.
8. Run a cold-start teacher test with the Canvas module, workbook, and student demo account.

## Do not do yet

- Do not publish licensed Xello downloads on the public MkDocs site.
- Do not assume every public Xello lesson is part of Irving's Grade 8 completion configuration.
- Do not capture hosted video streams. Use Xello's official shareable links or add the resource through Xello/Canvas.
- Do not remove the existing Xello work during the reconciliation. The task is to repair the sequence, not replace it again.
