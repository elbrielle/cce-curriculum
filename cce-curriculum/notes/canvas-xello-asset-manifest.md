# Canvas Xello Asset Manifest

**Status:** CAPTURE IN PROGRESS. The first 20 licensed files are staged locally in the gitignored Xello asset folder. This manifest governs the documents downloaded from the educator resource panels and rehosted inside the authenticated district Canvas course.

## Delivery standard

For each required Xello lesson:

1. Download the Xello-provided lesson plan, facilitator guide, presentation, worksheet, student directions, or family guide used by the module.
2. Stage the original file under `cce-curriculum/resources/xello-licensed/`. This folder is gitignored and must never be pushed to the public repository.
3. Upload the file to `Canvas Files/Licensed/Xello/Grade 8/<task-slug>/`.
4. Embed teacher-facing files on the module's Teacher Guide page.
5. Embed student-facing files on the student lesson page or assignment.
6. Keep the actual completion task linked to Xello so the district Completion Standards report remains authoritative.
7. Record the Canvas file ID, module item ID, audience, source task, capture date, and license note in this manifest during import.

Do not leave a teacher with only “Open Resources in Xello.” The Canvas module must contain the material needed to teach the lesson.

## Video handling

- Embed Xello's official video player or approved YouTube link when a share link is provided.
- Rehost a video file in Canvas only when Xello supplies a downloadable file or the district has explicit permission for that video.
- Do not extract a media file from a hosted stream merely because it plays in the browser.

## Capture queue

| Priority | Xello task or group | Documents to capture | Canvas placement | Status |
|---:|---|---|---|---|
| 1 | Log in to Xello | Day 1 checklist; introduction presentation | 1SW Wk0 teacher guide and student launch page | Pending capture |
| 2 | Matchmaker quiz | Activity lesson plan; student assessment guide | 1SW onboarding module | Lesson plan captured; student guide pending |
| 3 | Personality Style quiz | Available lesson plan or student guide from the resource panel | 1SW onboarding module | Activity plan captured |
| 4 | Learning Style quiz | My Learning Styles activity plan; applicable student guide | 1SW learning-profile module | Activity and lesson plans captured; student guide pending |
| 5 | Add interests and Add skills | My Interests plan; About Me student guide; applicable assignment directions | 1SW profile module | My Interests and About Me plans captured; assignment directions pending |
| 6 | Favorite clusters | My Career Clusters activity plan | 1SW cluster module | Captured locally; Canvas upload pending |
| 7 | Life, education, volunteer, and work experiences | My Experiences activity plan; About Me student guide | 2SW profile-update modules | My Experiences and About Me plans captured; student guide pending |
| 8 | After high school goal | Activity plan or sample assignment from the resource panel | 1SW Wk0 module | Pending capture |
| 9 | Save careers | My Careers activity plan and student directions | 2SW career-selection module | Activity plan captured; student directions pending |
| 10 | Set goals | My Goals activity plan | 3SW planning module | Captured locally; Canvas upload pending |
| 11 | Explore career matches | Lesson plan; Find Out Why student directions; introduction presentation | 2SW career-matches module | Lesson plan captured; directions and presentation pending |
| 12 | Skills lesson | Lesson plan and any attached student directions or presentation | 3SW skills module | Lesson plan captured; remaining attachments pending |
| 13 | Biases and career choices | Lesson plan; student instructions; introduction presentation | 3SW equity and career-choice module | Full English document pack captured: lesson plan, two student handouts, and PowerPoint |
| 14 | Scholarship profile | Student guide and family-facing material offered in the resource panel | Financial-planning module | Pending capture |
| 15 | Make plans | My Plans activity plan and student directions | Course-planning module | Activity and lesson plans captured; student directions pending |
| 16 | 4-year course plan and Submit course requests | Course Planner student video/guide; educator guide | Counseling-window module | Pending capture |
| 17 | Parent 4-year course plan approval | Family guide and Xello Family presentation | Family approval module | Pending capture |
| 18 | Transition to high school | Lesson plan; student directions; introduction presentation | Spring transition module | Lesson plan captured; directions and presentation pending |

### Local capture summary: 2026-08-06

- 10 prerequisite/activity-plan PDFs captured for Matchmaker, Personality Styles, Learning Styles, Interests, About Me, Career Clusters, Experiences, Careers, Goals, and Plans.
- 7 lesson-plan PDFs captured for Learning Styles, Study Skills and Habits, Plans, Biases and Career Choices, Skills, Explore Career Matches, and Transition to High School.
- The complete English Biases and Career Choices document pack was captured: lesson plan, Career Trailblazers directions, Non-traditional Career Matches directions, and the introduction PowerPoint.
- All binaries are under `cce-curriculum/resources/xello-licensed/`, which is gitignored. No licensed Xello file is staged for GitHub.

## Import record fields

Complete one row per uploaded file during the Canvas import.

| Source task | Original filename | Audience | Canvas file ID | Module item ID | Embedded page | Capture date | Notes |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## Completion gate

A Xello-backed module is not teacher-ready until:

- the required documents are uploaded to Canvas;
- each document is embedded on the page where it is used;
- student and teacher permissions are tested;
- the Xello completion link opens through district SSO;
- prerequisites and instructional time match the live Grade 8 configuration; and
- the module has a short fallback for an SSO or platform outage.
