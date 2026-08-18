# CCE Canvas image fix

**What it fixes.** In CCE courses imported from Canvas Commons, the lesson-page images (and the folders they live in) arrived locked, so students see a padlock instead of the picture. A Commons update does not reopen them.

**What it does.** For each course you name, it finds the Canvas files used by `<img>` tags on that course's pages and sets those files and their folders to published/unlocked. Nothing else changes: no modules or pages are published, the home page is untouched, no student data is read.

## One-time setup (Mac or Windows)

1. Python 3.9 or newer.
2. `pip3 install httpx`

## Run

Dry run first (reports, changes nothing):

```
python3 cce_image_access_fix.py --check --course-id 97981
```

Apply:

```
python3 cce_image_access_fix.py --course-id 97981
```

Several courses at once: repeat `--course-id`, or put one course ID per line in a text file and use `--courses-file ids.txt`.

When it asks for the **Canvas access token**, paste an admin token (Account → Settings → New Access Token). It is typed hidden and never saved. Delete the token in Canvas when you are done.

## Reading the result

One line per course, for example:

```
ok   course 97981 S1 - CC EXPLOR - GRIFFIN: images=307 folders=150 locked_before={'files': 34, 'folders': 150} still_locked={'files': [], 'folders': []}
```

`still_locked` empty = fixed. Have the teacher reload Student View. Course IDs are the number in the course URL (`/courses/97981`).

Questions: Elisha Lucero, elucero@irvingisd.net.
