---
name: cv-tailor
description: Tailor the user's master CV into a job-specific 2-page CV and matching 1-page cover letter (ATS-safe PDFs built from a LaTeX template), plus a markdown vacancy note holding the fit assessment and the verbatim job description, given a job posting link or pasted job description. Handles a single posting or a batch. Use whenever the user pastes a job link or description and asks to tailor a CV, write a cover letter, or "apply to this job", even without naming the skill. Never fabricates or embellishes anything not present in the source documents.
---

# CV Tailor

Turns a job posting into three deliverables in one application folder: a tailored CV (PDF), a
matching cover letter (PDF), and a vacancy note carrying the fit assessment, suggestions and
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
- **Output format:** PDF, built from the LaTeX template. Not DOCX, not markdown.
- **Application folder:** `<paths.applications>/YYYYMMDD - Company - Position/` (today's date;
  company and position exactly as posted, with `/ \ : * ? " < > |` replaced by `-`). It holds:
  - `vacancy.md`: the vacancy note;
  - `cv.tex`, `cover-letter.tex`, a copy of `jobcv.sty`, and a copy of the photo if one is used;
  - `YYYYMMDD - Company - Position - CV.pdf` and `... - CL.pdf`.

  Copy the style (and photo) in rather than referencing them, so each application stays
  rebuildable years later even if the template changes.
- **Template:** `<paths.latex_override>/jobcv.sty` if that file exists in the workspace (the user's
  customised look), otherwise `${CLAUDE_PLUGIN_ROOT}/latex/jobcv.sty`. Worked examples:
  `${CLAUDE_PLUGIN_ROOT}/latex/cv.tex` and `cover-letter.tex`; design rules and ATS rationale:
  `${CLAUDE_PLUGIN_ROOT}/latex/README.md`. Read the README before changing anything structural.
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
- For larger batches, a small Python driver that holds a dict per role and writes the `.tex`
  files, then calls the build script per folder, keeps the set consistent and easy to rebuild.

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

### 5. Write the tailored CV (`cv.tex`)

Copy the structure of the example `cv.tex`. **Write to the word budget** in
`documents.cv_word_budget` (default 550–600 extracted words for 2 pages at the template's 12pt
base). Treat ~620 as the point where it spills onto a third page:

- **Bullets: one line each, two at most** (~15–22 words). State what was owned or achieved and
  stop.
- **`\skillgroup` lines: ~18 words.** These are keyword payloads. Keep every tool name and proper
  noun (they're what an ATS matches) and cut the connecting words.
- **Profile: 2–3 lines** (~30 words), adapted from a reusable paragraph for this role.
- **Lead role gets three bullets; older roles get one.** Anything over ~10 years old earns a
  single line unless the posting calls for it.
- Reorganise freely: lead with what the posting emphasises most. Cut anything not relevant enough
  to earn space. Standard sections: profile, key strengths, core competencies, professional
  experience, education, languages, and an "At a Glance" block (headline counts such as
  publications or products shipped, plus the eligibility line).

**Identity and eligibility macros**, all from `job-hunt.yaml`:

```latex
\cvname{<identity.name_with_title>}
\cvtitle{<exact job title from the posting>}
\cvlocation{<identity.location>}
\cvphone{<identity.phone>}
\cvemail{<identity.email>}
\cvsite{<website.label>}{<website.url>}          % omit if no website
\cvlinkedin{<linkedin.label>}{<linkedin.url>}    % omit if none
\cvphoto{<photo filename>}                       % only if identity.photo is set
\cvcitizenship{<work_eligibility.citizenship>}   % omit if null
\cveligiblein{<work_eligibility.eligible_countries, comma-separated>}
\cvcountry{<country of THIS posting>}            % REQUIRED — build fails without it
\cvpermitnote{<work_eligibility.permit_note>}    % omit if null
```

Use `\quality{\permitline}` in At a Glance; never type an eligibility sentence by hand. Write
`\cvcountry` exactly as the country appears in `\cveligiblein` (the comparison is exact text).
After building, grep the extracted text for the eligibility line and confirm the country matches
the posting.

Paper size: `\documentclass[12pt,<documents.paper>]{article}`. Keep 12pt.

**Photo:** use it only if `identity.photo` is set. For postings in countries where photos are
discouraged (e.g. US, UK, Ireland, Canada), mention in chat that you left it out, or offer to.

### 6. Write the cover letter (`cover-letter.tex`)

`documents.cover_letter_words` (default 300–380 words), one page, three paragraphs:
- Subject line naming the role, not "Cover Letter".
- Salutation: the named hiring manager if the posting gives one, otherwise "Dear Hiring Team,".
- **Para 1**: company-specific motivation drawn from the actual posting.
- **Para 2**: professional match against the posting's real tasks, grounded only in the sources.
  Close with one honest, confident gap sentence reusing step 3's weaknesses, e.g. "I haven't yet
  worked directly with X, but I pick up new tools quickly and I'm motivated to get there fast."
- **Para 3**: fit as a colleague and working style, grounded in real facts (teams led,
  cross-functional work, mentoring), not invented traits.
- **Portfolio link:** if `portfolio_pages` lists any, link exactly one in para 3, picked by
  matching its `use_for` to the role. Make the surrounding sentence earn it by tying it to
  something already argued; a bare "see my website" is worse than no link. Place it before the
  closing invitation. Write it as `\weblink{<url>}{<label>}` (not `\href`, which renders
  invisibly black).
- Date line: `\cldate{<documents.date_city>, <D Month YYYY>}`. Sign-off:
  `\clclosing{<documents.sign_off>}{<identity.name>}`. The signature contact line is automatic, so
  don't add contact details under the name.
- `\enquote{}` is available for quoting the posting back to the employer.
- Voice: direct, polite, first person, addressed to the company. No generic filler ("I am a highly
  motivated professional…"). The master CV's opening fragments are raw material, not templates.

### 7. Build

1. Create the application folder; copy in `jobcv.sty` (and the photo, if used).
2. Write `cv.tex` and `cover-letter.tex`.
3. Run the build script:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/skills/cv-tailor/scripts/build.py" "<application folder>" --name-prefix "YYYYMMDD - Company - Position" --cv-pages <documents.cv_pages>
   ```

   It runs pdflatex twice per document, reports pages, extracted word count and overfull boxes,
   copies the PDFs to their final names, and cleans `.aux/.log/.out`. Non-zero exit means a build
   failed or missed its page budget. Use `python3` if `python` isn't on PATH. If `pdflatex` is
   missing, tell the user to install TeX Live or MiKTeX. Never fall back to another format
   silently.
4. **If the CV is 3 pages, cut content.** Never shrink type, leading or margins. If it's well
   under budget and on 2 pages, that's fine.
5. Spot-check the extracted text (`pdftotext` or `pdfminer.six` if available): the job title,
   section headings, contact details and the posting's key tool names should all appear as real
   words.

Template rules that matter (details in the latex README):
- Links in running text use `\weblink{url}{text}`, never bare `\href`.
- Don't change `top` or `\headerpush` in isolation; they're coupled.
- Don't undo the ATS measures (no letterspacing, microtype expansion off, ToUnicode, explicit
  separators, no icon fonts). If a tool name in the posting gets hyphenated across a line, add it
  to `\hyphenation{...}` in the document preamble.

### 8. Present

Keep the chat reply short; the assessment lives in the vacancy note.
- The fit score, one line (one per posting in a batch).
- The application folder path and the two PDF names.
- Anything blocking or needing a decision: verbatim text not captured, framing choices to
  confirm, files that already existed, page-count problems, photo choices.

Don't repeat the strengths, weaknesses or suggestions in chat.

## Notes

- If the posting can't be fetched (paywalled, login-gated), ask the user to paste the text.
- If the application folder already exists, ask before overwriting.
- Default is a clean tailored document. If the user wants changes tracked against the master CV,
  ask rather than assume.
- If a portal demands an editable DOCX, say so plainly and ask before producing one. The LaTeX
  PDF is the ATS-checked artefact; a converted Word file isn't.
