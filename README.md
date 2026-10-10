# Job Hunt Kit

A job-search pipeline for [Claude Code](https://code.claude.com). It finds live vacancies that
match your profile, scores each one against your CV, and writes a tailored two-page CV and
one-page cover letter for the ones worth applying to. You choose the output: **Word documents**
(editable `.docx` plus PDF, the default) or **LaTeX-typeset PDFs**. Both are ATS-safe. One rule
runs through all of it: **nothing is invented.** Every claim in every document traces back to a
master CV that you write and control.

<p align="center">
  <img src="docs/sample-word-cv-1.png" width="24%" alt="Sample Word CV, page 1">
  <img src="docs/sample-word-cover-letter-1.png" width="24%" alt="Sample Word cover letter">
  <img src="docs/sample-cv-1.png" width="24%" alt="Sample LaTeX CV, page 1">
  <img src="docs/sample-cover-letter-1.png" width="24%" alt="Sample LaTeX cover letter">
</p>
<p align="center"><sub>The same content for a fictional candidate: Word (left two) and LaTeX (right two).</sub></p>

## How it works

```mermaid
flowchart LR
    P[("master CV +<br>search parameters")] --> S
    S["<b>job-scout</b><br>search, verify live,<br>dedupe, tier"] -->|today's URLs| F
    F["<b>fit-check</b><br>score 1–10,<br>shortlist"] -->|chosen postings| T
    T["<b>cv-tailor</b><br>CV + cover letter<br>(Word or LaTeX),<br>vacancy note"]
```

| Skill | What it does | Writes |
|---|---|---|
| `/job-hunt-kit:setup` | Creates your workspace, interviews you, turns your existing CVs into a master CV, builds your search query matrix | `job-hunt.yaml`, `profile/`, `search/` |
| `/job-hunt-kit:job-scout` | Runs ~30 searches from a rotating matrix (including "hidden-match" queries that find roles whose titles you'd never search for), keeps only postings that are **recent and verifiably still open**, removes ones you've already seen, and sorts the rest into tiers | `postings/job-postings-list.md`, `postings/scouting-log.md` |
| `/job-hunt-kit:fit-check` | Reads every posting in today's list and scores it: requirements met (60%) and day-to-day tasks you've actually done (40%). Adjusts for "you don't need every skill" wording and caps the score for hard blockers. Adds a ranked table and a shortlist | appended to the postings list |
| `/job-hunt-kit:cv-tailor` | For each chosen posting: a CV, a cover letter, and a vacancy note with the fit assessment and the verbatim job description | `applications/YYYYMMDD - Company - Position/` |

Each step also works on its own. You can paste a job link straight into `cv-tailor` without ever
running the scout.

## Requirements

- **Claude Code** with web search/fetch available.
- **Python 3.9+** for the dedupe and build scripts.
- For **Word** output (default): `pip install python-docx`, plus Microsoft Word or
  [LibreOffice](https://www.libreoffice.org/) to make the PDFs and check the page count. Without
  either you still get `.docx` files.
- For **LaTeX** output: a distribution with `pdflatex`: [TeX Live](https://tug.org/texlive/),
  [MiKTeX](https://miktex.org/) (Windows) or [MacTeX](https://tug.org/mactex/). On
  Debian/Ubuntu: `sudo apt install texlive-latex-extra texlive-fonts-extra`.
- Optional: `pip install pypdf` (or `pdftotext` from poppler) for page and word counts, and a
  browser tool such as Claude in Chrome for capturing full job descriptions from sites that need
  a login.

`setup` asks which format you want, checks what's installed and offers to install what's missing.
You can switch later with `documents.format` in `job-hunt.yaml` (`docx`, `latex` or `both`).

## Install

Pick one of two routes. Both end with running `setup`.

### Option A: install the plugin (recommended)

In Claude Code:

```
/plugin marketplace add matvazp/job-hunt-kit
/plugin install job-hunt-kit@job-hunt-kit
```

Then make a folder for your job search, open Claude Code in it, and run:

```
/job-hunt-kit:setup
```

To get updates later: `/plugin marketplace update job-hunt-kit`, or turn on auto-update for the
marketplace under **Marketplaces** in `/plugin`.

### Option B: start from this template

1. Click **Use this template → Create a new repository** on GitHub. **Make it private**: it will
   hold your CV and contact details.
2. Clone it and open Claude Code in the folder. When you trust the folder, Claude Code registers
   the `job-hunt-kit` marketplace from `.claude/settings.json` and offers to install the plugin.
   (If it doesn't, use the two commands from option A.)
3. Run `/job-hunt-kit:setup`.

The template's `.gitignore` keeps your personal folders (`profile/`, `postings/`,
`applications/`, `search/`, `job-hunt.yaml`) out of git by default. If your repo is private and you
want them backed up, delete those lines.

## Daily use

Open Claude Code in your job-search folder. You can type the commands below, or just ask in
plain words ("find me new jobs", "tailor my CV for this link") and Claude picks the right skill.

**1. Find: `/job-hunt-kit:job-scout`.** Runs about 30 searches built from your search
parameters. It keeps only postings published in the last 30 days that it can confirm are still
open, skips anything you've already collected, and sorts the rest into tiers. The URLs go under
today's date in `postings/job-postings-list.md`. What it searched, kept and dropped, with
reasons, goes in `postings/scouting-log.md`. You can narrow a run: "just Germany today", "go
back 60 days", "only company career pages".

**2. Score: `/job-hunt-kit:fit-check`.** Reads every posting under today's date and scores it
1–10 against your master CV. 60% of the score is requirements met, 40% is day-to-day tasks
you've actually done. It adds a comparison table and a **Shortlist** of 3–5 picks to the same
file. Read it and decide where to apply.

**3. Tailor: `/job-hunt-kit:cv-tailor`.** Give it your picks ("tailor for 2, 4 and 5 from
today's shortlist") or paste links. Each posting gets its own
`applications/YYYYMMDD - Company - Position/` folder:

- `… - CV.docx` + `… - CV.pdf` (or just the PDF with LaTeX): two pages, ordered so the
  posting's must-haves come first, with the work-eligibility line set for that country.
- `… - CL.docx` + `… - CL.pdf`: a one-page cover letter.
- `vacancy.md`: the fit assessment, the gaps, and the job description copied word for word,
  so you still have it if the ad is taken down.
- `content.json`: the tailored content both formats are built from.

Review the documents, then apply.

**Shortcuts**

- **Skip the scout.** If someone sends you a job link, paste it with "tailor my CV for this"
  and you go straight to step 3.
- **Login-gated ads.** If a posting can't be fetched, Claude asks you to paste the text.
- **Edits.** Ask "make the profile shorter" or "lead with the IoT role" and Claude updates
  `content.json` and rebuilds. Or open the `.docx` in Word and polish it yourself. Just ask
  for any further changes in Word too, since a rebuild replaces the file.
- **Need the other format?** "Give me the LaTeX version of this one too" rebuilds the same
  content in the other format.

**Keeping it working well**

- **Keep adding to your master CV.** Tailoring only selects and rewords what's in it, never
  adds to it. When a skill flags a gap you can actually fill ("I did use Zephyr, at my last
  job"), add it to `profile/master-cv.md`, and every later application benefits.
- **Changed what you're looking for?** Run `/job-hunt-kit:setup` again. It updates only the
  parts you pick and regenerates your search queries.

## Your workspace

```
job-hunt.yaml                  ← settings: identity, eligibility, languages, paths, preferences
profile/
  master-cv.md                 ← the source of truth: long, detailed, everything you've done
  contributions.md             ← optional: publications, mentoring, patents, talks…
  search-parameters.md         ← target roles, industries, technologies, locations, exclusions
search/
  query-matrix.md              ← generated search queries (regenerated when parameters change)
  target-companies.md          ← employers to check directly
postings/
  job-postings-list.md         ← one heading per day: URLs, then the fit-check table
  scouting-log.md              ← what each scout run searched, kept and dropped, and why
applications/
  20261010 - Acme - Embedded Engineer/
    vacancy.md                 ← fit assessment + verbatim job description
    content.json               ← the tailored content; both formats are built from it
    20261010 - Acme - Embedded Engineer - CV.docx / .pdf
    20261010 - Acme - Embedded Engineer - CL.docx / .pdf
    (LaTeX: cv.tex, cover-letter.tex, jobcv.sty and the two PDFs)
templates/                     ← optional: your own jobcv-template.docx or jobcv.sty
```

Everything is plain Markdown with YAML frontmatter, so it works in any editor, and in
[Obsidian](https://obsidian.md) the vacancy notes show up as filterable properties.

**The master CV is what makes this work.** Tailoring only ever selects, reorders and rephrases what's
in it. So make it long, specific and full of numbers, and add to it whenever you remember
something. `setup` drafts it from your existing CVs and asks follow-up questions;
[`examples/example-master-cv.md`](plugins/job-hunt-kit/examples/example-master-cv.md) shows a
complete one for a fictional engineer.

## Design choices worth knowing

- **No fabrication, anywhere.** A requirement your sources don't support is named as a gap (in
  the fit assessment, and honestly in the cover letter), never papered over. Job descriptions in
  vacancy notes are verbatim or clearly marked as missing, never a summary passed off as the
  original.
- **Liveness over volume.** `job-scout` would rather report three open, recent postings than
  thirty stale ones. Every posting it lists has a publication date inside your window (default
  30 days) and positive evidence that it's still open. Everything it rejects is logged, with the
  reason.
- **One content file, two formats.** `cv-tailor` writes the tailored text once
  (`content.json`). Word and LaTeX are just renderers, so the no-invention rule, word budgets and
  eligibility check are identical whichever you pick, and switching formats never means
  rewriting.
- **ATS-safe documents.** Both formats avoid the usual parsing failures. Both: one column, no
  text boxes or icon fonts, and real text for headings and separators. Word: contact details in
  the body rather than the page header. LaTeX: also no broken ligatures, letter-spaced headings
  or tool names split by hyphenation. Details in
  [`word/README.md`](plugins/job-hunt-kit/word/README.md) and
  [`latex/README.md`](plugins/job-hunt-kit/latex/README.md).
- **Page counts are checked, not hoped for.** Every build converts to PDF and checks that the CV
  is two pages and the letter one. If it runs over, Claude cuts content instead of shrinking the
  type.
- **Your work-eligibility line can't silently be wrong.** The CV's "eligible to work in…" line
  is generated from the posting's country and your list of countries. If the country is missing,
  the build fails instead of shipping a CV that names the wrong country.

## Customising

- **Look and feel (Word):** copy
  [`word/jobcv-template.docx`](plugins/job-hunt-kit/word/jobcv-template.docx) to
  `templates/jobcv-template.docx` in your workspace, open it in Word and modify the styles
  (keep their names). No code involved.
- **Look and feel (LaTeX):** copy `plugins/job-hunt-kit/latex/jobcv.sty` to
  `templates/jobcv.sty` in your workspace and edit it.

  `cv-tailor` uses your copies when they exist.
- **Search regions:** `job-scout`'s domain allowlists in
  [`references/sources.md`](plugins/job-hunt-kit/skills/job-scout/references/sources.md) lean
  towards Europe. Other regions work, and the skill builds allowlists as needed. PRs adding
  regions are welcome.
- **Scoring weights, word budgets, freshness window:** see `job-hunt.yaml` and the skill files.

## A note on job sites

`job-scout` uses ordinary web search plus LinkedIn's public, logged-out job pages. It never logs
in on your behalf or scrapes behind a login. Keep run sizes modest and respect each site's terms
of use.

## Contributing

Issues and pull requests are welcome. To work on the plugin locally:

```bash
git clone https://github.com/matvazp/job-hunt-kit
claude plugin validate ./job-hunt-kit
claude --plugin-dir ./job-hunt-kit/plugins/job-hunt-kit
```

## License

[MIT](LICENSE)
