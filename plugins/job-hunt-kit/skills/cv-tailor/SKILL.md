---
name: cv-tailor
description: Tailor the user's master CV into a job-specific 2-page CV and matching 1-page cover letter (ATS-safe Word documents with PDFs, or LaTeX PDFs, per the user's settings), plus a markdown vacancy note holding the fit assessment and the verbatim job description, given a job posting link or pasted job description. Handles a single posting or a batch. Use whenever the user pastes a job link or description and asks to tailor a CV, write a cover letter, or "apply to this job", even without naming the skill. Never fabricates or embellishes anything not present in the source documents.
---

# CV Tailor

Turns a job posting into three deliverables in one application folder: a tailored CV, a
matching cover letter, and a vacancy note carrying the fit assessment, suggestions and
the verbatim job description. **All three are produced for every posting**, including in batches.

## 0. Locate the workspace

The workspace is the folder containing `job-hunt.yaml`, normally the current working directory
(check parent folders if not). If there's none, offer `/job-hunt-kit:setup` and stop. Read
`job-hunt.yaml` in full: identity, work eligibility, languages, portfolio pages, paths and
document settings all come from it.

## Inputs and conventions

- **Master CV** (`paths.master_cv`): the source of truth. Read it in full, fresh, before drafting.
  Honour its "How to use this document" notes, use its reusable profile paragraphs (adapted, not
  pasted) and its known-gaps section.
- **Contributions record** (`paths.contributions`, optional). Read it in full if present. If
  something in it relates to the posting, surface it in the vacancy note's Suggestions, not in the
  CV, and say whether it's worth adding to the CV or letter.
- **Output format:** `documents.format` in `job-hunt.yaml`: `docx` (the default: Word files plus
  PDFs), `latex` (PDFs from the LaTeX template) or `both`. If the key is missing, use `docx`. The
  user can override it for one request ("give me the LaTeX version too").
- **One source, two renderers.** You write the tailored content once, as `content.json` in the
  application folder (schema: `references/content-schema.md`; full example:
  `${CLAUDE_PLUGIN_ROOT}/examples/example-content.json`). `scripts/build.py` renders it to Word
  and/or LaTeX, builds the PDFs and checks the page counts. Never write `.tex` or `.docx` by hand.
- **Application folder:** `<paths.applications>/YYYYMMDD - Company - Position/` (today's date;
  company and position exactly as posted, with `/ \ : * ? " < > |` replaced by `-`). It holds:
  - `vacancy.md`: the vacancy note;
  - `content.json`: the tailored content, and the file to edit for any later change;
  - Word: `YYYYMMDD - Company - Position - CV.docx` and `- CL.docx`, plus matching `.pdf`s;
  - LaTeX: `cv.tex`, `cover-letter.tex`, a copy of `jobcv.sty`, and `... - CV.pdf` / `- CL.pdf`;
  - with `both`, the Word PDFs are tagged `- CV (Word).pdf` so the two don't collide;
  - a copy of the photo, if one is used.

  Everything needed to rebuild lives in the folder, so an application stays rebuildable years
  later even if the templates change.
- **Templates (the look):** the workspace's `paths.templates` folder (default `templates/`; older
  workspaces may have `paths.latex_override` instead) may hold `jobcv-template.docx` (Word styles)
  and/or `jobcv.sty` (LaTeX style). Pass that folder to the build script with `--templates`. It
  uses the user's files where they exist and the bundled ones otherwise
  (`${CLAUDE_PLUGIN_ROOT}/word/jobcv-template.docx`, `${CLAUDE_PLUGIN_ROOT}/latex/jobcv.sty`).
  Design rules and ATS rationale: `${CLAUDE_PLUGIN_ROOT}/word/README.md` and
  `${CLAUDE_PLUGIN_ROOT}/latex/README.md`.
- **Hard rule: no fabrication.** Every fact (titles, dates, tools, results) must trace to the source
  documents. Rephrasing, reordering, re-emphasising and translating into the posting's vocabulary
  are fine; inventing metrics, tools or experience is not. A requirement the sources don't support
  is a gap to name. The same goes for the job description: never reconstruct or paraphrase it and
  present it as verbatim.

## Batch runs

When the user supplies several postings (pasted links, or a shortlist from `fit-check`):
- Produce all three deliverables for every posting. A CV and letter without a vacancy note is an
  incomplete run, even if a fit-check table already exists. The note holds the verbatim
  description, which the table does not.
- Read the source documents once at the start, not once per posting.
- Capture every verbatim description (step 2) **before** generating documents. Some sites
  throttle after the first few page loads in a session.
- If the user narrows scope ("just the CVs"), honour it and say which deliverables were skipped.
- Each posting gets its own `content.json` and its own build-script run.

## Workflow

### 1. Read all inputs

Fetch and read the full posting (`WebFetch` for a URL; for LinkedIn try the guest endpoint
`https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/<numeric-id>`). Read the source
documents. Note must-haves, nice-to-haves, the actual day-to-day tasks, compensation, and any
named hiring manager, recruiter or team.

### 2. Capture the job description verbatim

The vacancy note needs the posting's real text, not a summary. `WebFetch` returns a
model-written summary, which is **not** acceptable for the Job Description section. To get the
real text:
1. Prefer a browser tool if one is available (e.g. Claude in Chrome: `navigate` +
   `get_page_text`). The user may be logged in to the job site.
2. Otherwise, the LinkedIn guest endpoint or the raw page may contain the full text. Copy it
   exactly.
3. Otherwise ask the user to paste the description.
4. Never fill the section from a summary. If verbatim text can't be obtained, put
   `> [!warning] Verbatim description not captured — paste here` in the section and say so in
   chat.

Stop after 2–3 failed attempts per page rather than grinding. The summary is fine for the
*assessment*; only the Job Description section must be verbatim. Real text often reveals details
a summary drops (specific tools, test methods, standards) that change how the CV should be framed.

### 3. Score the fit

- Overall fit score (X/10) with a one-line rationale.
- **Strengths**: requirements clearly evidenced in the sources.
- **Weaknesses**: requirements not evidenced or only weakly. Reuse the master CV's known gaps.
- Anything material outside the JD: citizenship/clearance typical of the sector, relocation,
  language level. Check against `work_eligibility` and `languages` in `job-hunt.yaml`.

### 4. Write the vacancy note (`vacancy.md`)

If a vacancy note for the same posting URL already exists anywhere under the applications folder,
stop and ask before writing. It may hold annotations or a verbatim description that can't be
recaptured.

Frontmatter:

```yaml
---
company: <exactly as posted>
role: <exactly as posted>
fit: 7                      # score out of 10
location: <city, country>
type:
  - Industry                # one of Industry, Startup, Academia, Public sector
date: YYYY-MM-DD            # today
status:
  - Shortlisted
contact: <Name | email | phone, as given; blank if none>
link: <the posting URL>
---
```

`type` and `status` use YAML list form, so tools like Obsidian read them as multi-value
properties.

Body:

```markdown
# Assessment

**Fit: X/10** — one-line rationale.

## Strengths

| Strength | Why |
|---|---|
| … | … |

## Weaknesses

| Gap | Why |
|---|---|
| … | … |

## Suggestions

- …

# Job Description

<verbatim posting text>
```

Suggestions cover anything that would improve the application: CV framing, cover-letter angles,
skills or certifications worth pursuing, contributions-record items worth adding, gaps worth
raising head-on in an interview, and framing choices the user should confirm.

### 5. Write the tailored CV (the `cv` part of `content.json`)

Follow `references/content-schema.md` and the shape of the example. **Write to the word budget**
in `documents.cv_word_budget` (default 550–600 extracted words for 2 pages, in either format).
Treat ~620 as the point where it spills onto a third page:

- **Bullets: one line each, two at most** (~15–22 words). State what was owned or achieved and
  stop.
- **Skill-group lines: ~18 words.** These are keyword payloads. Keep every tool name and proper
  noun (they're what an ATS matches) and cut the connecting words.
- **Profile: 2–3 lines** (~30 words), adapted from a reusable paragraph for this role.
- **Lead role gets three bullets; older roles get one.** Anything over ~10 years old earns a
  single line unless the posting calls for it.
- Reorganise freely: lead with what the posting emphasises most. Cut anything not relevant enough
  to earn space. Standard sections: profile, key strengths, core competencies, professional
  experience, education, languages, and an "At a Glance" (`glance`) section with headline counts
  such as publications or products shipped.

**Identity and eligibility**, all from `job-hunt.yaml`:
- `identity`: copy `name`, `name_with_title`, `location`, `phone`, `email`, `website` and
  `linkedin` (null when absent). `photo`: only if `identity.photo` is set; copy the file into the
  application folder and give just its filename.
- `eligibility`: `citizenship`, `eligible_countries` and `permit_note` from `work_eligibility`,
  plus `country` = **the country of this posting** (required; the build fails without it).
  Spell it as in `eligible_countries`.
- `cv.title`: the exact job title from the posting. `paper`: `documents.paper`.

The eligibility sentence is generated and appended to the `glance` section; never type one. After
building, confirm the sentence names the posting's country.

**Photo:** use it only if `identity.photo` is set. For postings in countries where photos are
discouraged (e.g. US, UK, Ireland, Canada), mention in chat that you left it out, or offer to.

### 6. Write the cover letter (the `letter` part of `content.json`)

`documents.cover_letter_words` (default 300–380 words), one page, three paragraphs:
- `subject` names the role, not "Cover Letter".
- `salutation`: the named hiring manager if the posting gives one, otherwise "Dear Hiring Team,".
- **Para 1**: company-specific motivation drawn from the actual posting.
- **Para 2**: professional match against the posting's real tasks, grounded only in the sources.
  Close with one honest, confident gap sentence reusing step 3's weaknesses, e.g. "I haven't yet
  worked directly with X, but I pick up new tools quickly and I'm motivated to get there fast."
- **Para 3**: fit as a colleague and working style, grounded in real facts (teams led,
  cross-functional work, mentoring), not invented traits.
- **Portfolio link:** if `portfolio_pages` lists any, link exactly one in para 3, picked by
  matching its `use_for` to the role, written as `[label](url)`. Make the surrounding sentence
  earn it by tying it to something already argued; a bare "see my website" is worse than no
  link. Place it before the closing invitation.
- `date`: `<documents.date_city>, <D Month YYYY>`. `sign_off`: `documents.sign_off`.
  `signature_name`: `identity.name`. The signature contact line is added automatically, so don't
  put contact details in the paragraphs.
- Voice: direct, polite, first person, addressed to the company. No generic filler ("I am a highly
  motivated professional…"). The master CV's opening fragments are raw material, not templates.

### 7. Build

1. Create the application folder (and copy the photo in, if used). Write `content.json`.
2. Run the build script with the format from `documents.format`:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/skills/cv-tailor/scripts/build.py" "<application folder>" --format <docx|latex|both> --name-prefix "YYYYMMDD - Company - Position" --cv-pages <documents.cv_pages> --templates "<workspace>/<paths.templates>"
   ```

   It renders `content.json`, builds the documents, reports pages and extracted word counts,
   copies the outputs to their final names and cleans up. Use `python3` if `python` isn't on
   PATH.
   - Exit `1`: a document failed or missed its page budget, or `content.json` is invalid (the
     error names the field). Fix and rerun.
   - Exit `2`: a tool is missing. For Word, `pip install python-docx`. For LaTeX, TeX Live or
     MiKTeX. Tell the user; never switch format silently.
   - Word PDFs need Microsoft Word, LibreOffice or docx2pdf. Without one, the `.docx` is still
     produced but the output says `pages NOT checked`. Tell the user to check the page count when
     they open it, or to install LibreOffice.
3. **If the CV runs to 3 pages, cut content** in `content.json` and rebuild. Never shrink type,
   leading or margins. Well under budget on 2 pages is fine.
4. Spot-check a PDF's extracted text (`pdftotext` or pypdf): the job title, section headings,
   contact details, the eligibility sentence and the posting's key tool names should all appear
   as real words.

Rules that matter:
- **LaTeX:** if a tool name from the posting gets hyphenated across a line, add it to
  `cv.hyphenation_exceptions`. Don't undo the template's ATS measures (see the latex README).
- **Word:** single column, real headings, no text boxes or layout tables, contact details in the
  body rather than the page header. Keep it that way if the user asks for design changes.

### 8. Present

Keep the chat reply short; the assessment lives in the vacancy note.
- The fit score, one line (one per posting in a batch).
- The application folder path and the output file names.
- Anything blocking or needing a decision: verbatim text not captured, framing choices to
  confirm, files that already existed, page-count problems, photo choices.

Don't repeat the strengths, weaknesses or suggestions in chat.

## Notes

- If the posting can't be fetched (paywalled, login-gated), ask the user to paste the text.
- If the application folder already exists, ask before overwriting.
- Default is a clean tailored document. If the user wants changes tracked against the master CV,
  ask rather than assume.
- **Later edits** ("make the profile shorter", "lead with the IoT role"): edit `content.json`
  and rerun the build script. If the user has already edited the `.docx` in Word, a rebuild
  overwrites their edits, so ask first.
- **Hand-edited LaTeX:** `--no-render` builds the existing `.tex` files as they are.
