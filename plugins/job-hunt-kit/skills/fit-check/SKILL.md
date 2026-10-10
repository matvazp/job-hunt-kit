---
name: fit-check
description: Batch-assess the fit between the user's master CV and every job posting listed under today's date in their postings list, then append a six-column comparison table plus a shortlist recommendation to that same file. Use whenever the user asks to score, rank, triage or "fit-check" the day's job postings, or asks which of today's postings are worth applying to. Never fabricates or embellishes anything not present in the source documents.
---

# Fit Check

Reads the day's collected posting links, scores each against the master CV, and writes one
comparison table back into the postings list so the user can decide where to spend application
effort.

Related: `job-scout` fills the list; once the user picks from the shortlist, `cv-tailor` produces
the CV, cover letter and vacancy note.

## 0. Locate the workspace

The workspace is the folder containing `job-hunt.yaml`, normally the current working directory
(check parent folders if not). If there's none, offer `/job-hunt-kit:setup` and stop. Read
`job-hunt.yaml`. Paths below come from its `paths:` block.

## Inputs and hard rules

- **Postings list** (`paths.postings_list`), input *and* output. A `## YYYY-MM-DD` heading per day
  followed by bullet URLs. **Only process links under today's heading.** If there's no heading for
  today, say so and stop. Don't silently fall back to the most recent day. (If the user names a
  date, use that one instead.)
- **Master CV** (`paths.master_cv`), the source of truth. Read it in full, fresh, every run. Use its
  "Known self-assessed gaps" section where present.
- **Contributions record** (`paths.contributions`, optional). Read it in full if it exists. It
  often supplies evidence the CV only implies.
- **The user's constraints** from `job-hunt.yaml`: home city (commuting range), work eligibility,
  languages. Also the hard constraints in `paths.search_parameters`.
- **No fabrication.** Every claim traces to the source documents. A requirement they don't
  support is a weakness to name, not paper over.
- **Read the real posting.** Never score from the URL, the company name, or a guess. If the
  text can't be retrieved, mark the row unfetched (step 2).

## Workflow

### 1. Read all inputs

Read the source documents, then extract every URL under today's heading. Report the count before
fetching ("12 postings under 2026-08-05, fetching now").

### 2. Fetch each posting

For each URL, in list order (batch independent fetches):
1. `WebFetch`. Ask for company, title, location, employment type, seniority, full
   responsibilities, required and preferred qualifications, any "you don't need to meet every
   requirement" statement, named contact, and deadline. For LinkedIn, the guest endpoint
   `https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/<numeric-id>` usually renders the
   full posting without a login.
2. If that fails or returns a gated/empty page, and a browser tool is available (e.g. Claude in
   Chrome: `navigate` + `get_page_text`), try it. The user may be logged in.
3. If both fail, still give the posting a row: company/title if known (else the bare URL), `—` in
   FIT, `Could not retrieve posting text` in REQUIREMENTS, other cells empty. Never invent content
   and never quietly drop the posting.

Watch for:
- **Softening language**: "you don't need to tick every box", "willingness to learn", "if you meet
  most of the requirements we encourage you to apply". This affects the score (step 3).
- **Hard blockers** not framed as ordinary requirements: security clearance, a citizenship the user
  doesn't hold, a language at a level they don't have, a driving licence, shift work, a location
  outside commuting range with no relocation option. These cap the score.

### 3. Score the fit

Two sub-scores, each 1–10, then a weighted total to one decimal.

**A. Requirements (60%).** How well the stated professional and personal requirements are met.
Judge each must-have and nice-to-have as *met with direct evidence*, *met by adjacent evidence*,
or *not evidenced*, weighting must-haves far more heavily. Include personal requirements
(independence, seniority, communication, languages, travel, work eligibility).

Anchors: **9–10** every must-have directly evidenced plus most nice-to-haves · **7–8** all
must-haves met, some via adjacent evidence · **5–6** one significant must-have missing or several
met only by analogy · **3–4** a headline must-have absent with no bridge · **1–2** different
discipline or a hard blocker.

**B. Activities (40%).** For the day-to-day tasks the posting describes: has the user done
something similar? Judge task by task against actual experience and projects, not keyword lists.
The question is "have they done this work", not "does the word appear in the CV". Credit close
analogues from other domains, and say so explicitly rather than passing them off as exact matches.

Anchors: **9–10** has performed nearly all these tasks as a core part of a role · **7–8** most,
some in a different domain or scale · **5–6** about half, mostly by analogy · **3–4** isolated
overlaps · **1–2** essentially new work.

**Total = 0.6 × A + 0.4 × B**, one decimal.

**Softening adjustment:** if the posting explicitly relaxes requirements or emphasises potential
over completed experience, add **+0.3 to +0.8** (more when it covers exactly what the user lacks,
less when it reads as boilerplate). Note it in REQUIREMENTS so the number is traceable.
**Hard blocker:** cap the total at **3.0** and name the blocker first in WEAKNESSES.

### 4. Write the table

Append directly below today's links, still under today's heading:

| Column | Content |
|---|---|
| `Job Description` | `Company - Job Title`, exactly as posted, as a markdown link to the URL |
| `FIT` | Weighted total, one decimal |
| `REQUIREMENTS` | Must-haves/nice-to-haves met and not met; personal requirements; softening and adjustment. Lead with the decisive one |
| `ACTIVITIES` | Task by task: what the user has done that is the same or closely analogous (name the concrete prior work), and what would be new |
| `STRENGTHS` | Strengths that move this fit, highest impact first |
| `WEAKNESSES` | Gaps that move this fit, highest impact first |

Rules:
- **Sort rows by FIT, highest first.**
- Cells of roughly 25–60 words: semicolon-separated clauses, no line breaks (they break markdown
  tables); `<br>` only if a cell genuinely needs a list. Escape literal `|` as `\|`.
- Prefer specifics from the sources (named projects, real numbers) over generic labels.
- Leave the list of links above the table untouched.
- If a table already exists under today's heading, ask before overwriting. The user may have
  annotated it.

### 5. Write the shortlist

Below the table, a `### Shortlist` recommending **three to five** postings, each with one or two
sentences on why. Rank by score, but override where judgement says so and explain why. For example,
a 6.8 with explicit "willingness to learn" framing in a direction the user is targeting can beat a
7.5 that repeats work they've already done sideways. Mention deadlines and named contacts.

Flag in one line any well-scoring posting that needs a decision first (relocation, travel load,
seniority mismatch, contract type).

### 6. Present

Short chat reply; the assessment lives in the file.
- How many postings were assessed and how many failed to fetch.
- A compact ranked list, `Company - Title — X.X`, one per line.
- The shortlist names.
- Anything blocking: unretrievable postings, a table that would be overwritten, hard blockers.
- Next step: `/job-hunt-kit:cv-tailor` with the chosen posting(s).

## Notes

- A posting assessed on an earlier day still gets assessed fresh today. Postings change, and so
  does the CV.
- Duplicate URL in today's list: assess once and say so.
- If the user wants the assessment in chat instead of the file, give the same table and skip the
  write.
