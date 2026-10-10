---
name: setup
description: Set up or update a job-hunt-kit workspace. Creates the folder structure and settings file (job-hunt.yaml), interviews the user for their contact details, work eligibility, languages and job-search parameters, turns their existing CV(s) into a master CV without inventing anything, generates their search query matrix, and checks that Python and LaTeX are installed. Use when the user wants to start using job-hunt-kit, set up their job search, onboard, or change their profile or search parameters, or when another job-hunt-kit skill finds no job-hunt.yaml.
---

# Setup

Creates a job-hunt-kit workspace in a folder and fills it with the user's real information, so
`job-scout`, `fit-check` and `cv-tailor` can run. Safe to re-run: it never overwrites an existing
file without asking, and on an existing workspace it updates only the sections the user picks.

Template files are in `${CLAUDE_PLUGIN_ROOT}/template/`. A fully worked fictional example master
CV and search-parameters file are in `${CLAUDE_PLUGIN_ROOT}/examples/`. Use them to show the user
what "good" looks like.

## 1. Choose the folder

- Default: the current working directory. If the user named a path, use that.
- If the folder already contains `job-hunt.yaml`, this is an **update**: read it, summarise what's
  configured, and ask which parts to revisit (identity, eligibility, languages, search parameters,
  master CV, query matrix). Skip to those steps.
- If the folder is non-empty and isn't a job-hunt-kit workspace (and isn't a fresh copy of the
  job-hunt-kit template repo), confirm before creating files there, or suggest a new subfolder
  such as `job-search/`.

Remind the user once: this folder will hold their CV, contact details and application history.
If it's a git repo, keep it **private**, or keep the default `.gitignore`, which excludes the
personal folders.

## 2. Check prerequisites

Run these and report in one short line each. Don't block on missing tools; explain what each
one is needed for:
- `python --version` (or `python3`): needed by job-scout's dedupe script and cv-tailor's build
  script.
- `pdflatex --version`: needed to build PDFs. Install TeX Live (tug.org/texlive) or MiKTeX on
  Windows; on macOS, MacTeX; on Debian/Ubuntu,
  `sudo apt install texlive-latex-extra texlive-fonts-extra`.
- Optional: `pdftotext` (poppler) or `pip install pypdf` for word counts and text-extraction
  checks.
- Optional: a browser tool (e.g. Claude in Chrome) for capturing full job descriptions from sites
  that need a login.

## 3. Create the structure

Create these, copying from `${CLAUDE_PLUGIN_ROOT}/template/`. **Never overwrite an existing file.**
If one exists, keep it and tell the user.

```
job-hunt.yaml                 ← template/job-hunt.yaml
CLAUDE.md                     ← template/CLAUDE.md (if a CLAUDE.md exists, append its content under a "## Job search" heading instead)
.gitignore                    ← template/gitignore (if .gitignore exists, append only the missing lines)
profile/master-cv.md          ← template/master-cv.md
profile/contributions.md      ← template/contributions.md
profile/search-parameters.md  ← template/search-parameters.md
search/target-companies.md    ← template/target-companies.md
postings/job-postings-list.md ← template/job-postings-list.md
postings/scouting-log.md      ← template/scouting-log.md
applications/                 (empty folder)
```

## 4. Interview

Ask in small groups, not one long form. Use `AskUserQuestion` for multiple-choice items and plain
questions for free text. Accept "skip" for anything optional. Write answers into `job-hunt.yaml`
as you go.

1. **Identity**: full name as on the CV (and with title/post-nominals, e.g. "Ph.D."), short
   location for the CV header ("Utrecht, NL"), home city, phone, email, website and LinkedIn
   (optional), photo (optional: path to a square image, copied to `profile/`). Note that photos
   are normal in some countries and discouraged in others.
2. **Work eligibility**: citizenship (adjective form, or leave off), the countries they can
   already work in (e.g. all EU/EEA countries for an EU citizen: list them explicitly), and the
   note to show elsewhere (default "work permit required").
3. **Languages** and levels, as they'd write them on a CV.
4. **Portfolio pages** (optional): URLs a cover letter may link to, each with the kind of role it
   suits.
5. **Document preferences**: paper size (A4 or US Letter), sign-off, the city for the letter date
   line. Defaults are fine for most people.

## 5. Build the master CV

This is the most important step. Everything downstream depends on it.

1. Ask for their existing material: CV(s) in PDF/DOCX/Markdown, a LinkedIn profile PDF export,
   cover letters they've written, a portfolio. Read everything provided (use the pdf/docx skills
   if available).
2. Fill `profile/master-cv.md` following the template's sections. **Transfer facts faithfully. Do
   not invent, inflate or "improve" anything.** Merge duplicates across documents; where sources
   disagree (dates, titles), ask.
3. The master CV should be *longer* than any CV they've sent. Ask follow-up questions to draw out
   what their short CVs left out: concrete results with numbers, tools used per role, team sizes,
   projects, things they're proud of. Keep it conversational, a few questions at a time.
4. Draft 2–4 **reusable profile paragraphs** for the role families they target, from facts in the
   CV only, and ask them to approve or edit.
5. Fill **Known self-assessed gaps** by asking which requirements they commonly see in postings but
   don't meet. Don't guess these.
6. Put longer-form evidence (mentoring, publications, patents, talks, grants, open source) in
   `profile/contributions.md`, or delete that file and its `paths.contributions` line if they have
   none.
7. Show a short summary of what was captured and what's still thin. Remind them the file is theirs
   to keep enriching; the more it holds, the better the tailoring.

## 6. Search parameters

Fill `profile/search-parameters.md` with them: target roles (plus adjacent titles they'd accept),
seniority, industries, technologies/skills to search on (prompt with ones from the master CV
that rarely appear in job titles), locations in priority order and remote/hybrid preference,
posting languages, exclusions, hard constraints. Offer suggestions drawn from the master CV, but
let them decide.

Optionally seed `search/target-companies.md` with employers they already know they want.

Ask whether 30 days is the right freshness window and ~30 queries per run the right size (store
both in `job_search`).

## 7. Generate the query matrix

Following `${CLAUDE_PLUGIN_ROOT}/skills/job-scout/references/query-matrix-guide.md`, write
`search/query-matrix.md` from the search parameters and master CV. Every query traces to those
sources. Show the category counts and a handful of example queries, especially hidden-match ones,
and invite edits.

## 8. Verify the LaTeX toolchain (if pdflatex is present)

Build the bundled example once in a temporary folder to confirm the toolchain works:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/cv-tailor/scripts/build.py" "<temp folder with copies of ${CLAUDE_PLUGIN_ROOT}/latex/jobcv.sty, cv.tex, cover-letter.tex>"
```

If it fails on a missing package, name the package and the install command for their TeX
distribution (MiKTeX installs missing packages on first use if allowed). Delete the temp folder
afterwards.

## 9. Finish

Summarise briefly:
- What was created and where.
- Anything left to fill in (thin master-CV sections, skipped fields).
- How to run the pipeline:
  1. `/job-hunt-kit:job-scout`: find today's postings.
  2. `/job-hunt-kit:fit-check`: score and shortlist them.
  3. `/job-hunt-kit:cv-tailor <url>`: tailored CV, cover letter and vacancy note.
- To change the look of the documents: copy `jobcv.sty` into `latex/` in the workspace and edit
  it there.
