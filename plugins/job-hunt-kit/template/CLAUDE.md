# Job search workspace

This folder is a job-hunt-kit workspace. The `job-hunt-kit` plugin's skills read and write the
files here; `job-hunt.yaml` tells them where everything is.

## Pipeline

1. `/job-hunt-kit:job-scout` — find new, live, recent vacancies → `postings/job-postings-list.md`
   (bare URLs under today's date) and `postings/scouting-log.md` (annotated).
2. `/job-hunt-kit:fit-check` — score today's postings against the master CV → a ranked table and
   shortlist appended under today's date in the postings list.
3. `/job-hunt-kit:cv-tailor <posting URL(s)>` — tailored CV + cover letter (Word + PDF, or LaTeX PDF, per `documents.format`) and a
   vacancy note with the fit assessment → `applications/YYYYMMDD - Company - Position/`.

## Ground rules

- `profile/master-cv.md` is the source of truth. Never invent facts that aren't in it or in
  `profile/contributions.md`; a requirement the sources don't support is a gap to name.
- Never list or score a posting whose text wasn't actually read.
- Keep the postings list as bare URLs under date headings; annotations go in the scouting log.
