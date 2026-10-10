---
name: job-scout
description: Discover new job vacancies for the user by running a rotating matrix of web searches built from their job-search parameters, screen the hits against their master CV, verify each posting is live and recently published, drop duplicates already collected, and write a tiered list of posting URLs under today's date in their postings list plus an annotated scouting log. Use whenever the user asks to find, hunt for, scout or search for new job postings, to "run the job search", or to refresh today's list of vacancies. Never fabricates postings, companies or URLs, and never lists a posting whose liveness was not checked.
---

# Job Scout

Replaces manual searching across LinkedIn, company career sites, search engines and job boards.
Produces the day's list of candidate vacancy URLs, tiered, deduplicated against everything
collected before, and written where `fit-check` expects to find it.

**Pipeline position:** `job-scout` (discover, verify live, coarse-screen) → `fit-check` (score
1–10 and shortlist) → `cv-tailor` (tailored CV, cover letter, vacancy note). Scout deliberately
stops short of scoring. Its job is recall: surfacing vacancies a keyword search would miss. A
posting wrongly dropped here never reaches `fit-check`, so **on relevance, when in doubt, keep it.**

**On liveness the bias runs the other way: when in doubt, drop it.** A short list of open, recent,
well-matched vacancies is worth more than a long list padded with expired ones. Every posting
written to the list must be inside the freshness window and carry positive evidence it is still
accepting applications (step 5). That gate will end some runs with a handful of keepers, or none.
That is intended; don't loosen the gate to make a run look productive.

## 0. Locate the workspace

The workspace is the folder containing `job-hunt.yaml`, normally the current working directory.
If it isn't there, check parent folders. If there's still none, tell the user and offer to run
`/job-hunt-kit:setup`, then stop.

Read `job-hunt.yaml` in full. Every path below comes from its `paths:` block (relative to the
workspace). Also take `job_search.freshness_days` (default 30) and `job_search.queries_per_run`
(default 30), plus the user's home city, languages and work eligibility.

## Inputs

- **Search parameters** (`paths.search_parameters`): target roles, industries, technologies,
  locations, seniority, exclusions, hard constraints. Read in full, fresh, every run.
- **Master CV** (`paths.master_cv`): defines adjacency. The screen in step 6 depends on knowing
  what the user has actually done, not just which keywords they list. Read in full.
- **Query matrix** (`paths.query_matrix`): the standing queries. If it doesn't exist, or the
  parameters have changed in a way it doesn't reflect (a new technology, country or target role),
  (re)generate it first following `${CLAUDE_PLUGIN_ROOT}/skills/job-scout/references/query-matrix-guide.md`
  and note the regeneration in the scouting log.
- **Sources** (`${CLAUDE_PLUGIN_ROOT}/skills/job-scout/references/sources.md`): domain allowlists,
  posting vs. listing URL patterns, per-host date and closure cues.
- **Target companies** (`paths.target_companies`, optional): employers worth a direct careers-page
  pass.
- **Postings list** (`paths.postings_list`): output, and the dedupe source. `## YYYY-MM-DD`
  heading per day, newest first, bare URLs beneath.
- **Scouting log** (`paths.scouting_log`): output. The annotated record.

## Hard rules

- **Real postings only.** Every URL written must have come back from an actual search or fetch.
  Never construct a plausible-looking job URL, infer a vacancy from a careers homepage, or carry a
  posting over from memory of an earlier session.
- **Freshness window.** Only postings published within `freshness_days` before today reach the
  list. Compute the cut-off date at the start and state it in chat and in the log.
- **Liveness verified, not assumed.** A search engine returning a URL is not evidence;
  indexes carry filled and withdrawn vacancies for months.
- **Bare URLs in the postings list.** Under a date heading: nothing but `- <url>` lines.
  `fit-check` parses that list. Annotations go in the scouting log.

## Workflow

### 1. Read inputs and plan the search set

Read the parameters, the master CV, then the query matrix.

**Fix the freshness cut-off first**: today minus `freshness_days`. State it in chat before
searching (`Freshness cut-off: postings published on or after YYYY-MM-DD`).

Pick about `queries_per_run` queries (25–35 is typical; the real budget is fetches, not searches,
because step 5 spends a fetch on nearly every survivor). If a run is going long, cut queries
rather than liveness checks. Compose the subset so that:
- every category in the matrix is represented, roughly in proportion;
- **at least a third are hidden-match, transferable or skill queries.** These find vacancies
  whose titles the user would never search for, and they are the reason this skill exists. Don't
  let a run collapse into role-title searches just because those return cleaner results;
- queries used in the last two runs (check the scouting log) are skipped unless nothing new was
  found since.

Say in chat which categories and how many queries before starting.

### 2. Run the searches

Batch several independent searches/fetches per message.

**Prefer the LinkedIn guest search endpoint** (see `sources.md`) for most queries. It renders
without login, returns ten postings per fetch each with a posted-age string, and `f_TPR` filters
to the window. Keep volume modest and be considerate of the service.

For `WebSearch`:
- Name the country or city *in the query string*, and add the current year to push out stale
  index entries.
- Pair the query with an `allowed_domains` set from `sources.md` chosen to match the query.
  Prefer allowlists over `site:` operators; `site:` works but a US index bias survives it.
- Run each ATS-category query both ways: once with `site:` as written, once as a plain query with
  that host in `allowed_domains`.

Treat any hit whose snippet already reads as stale ("posted 3 months ago", a closed-application
note, an old year) as dropped at this point.

### 3. Harvest candidate URLs

Keep only **direct posting URLs**. Discard search-result pages, category listings, careers
homepages, and aggregator/scraper pages (`sources.md` lists the patterns per host). Two exceptions
worth following:
- A listing page on a *native* board that plainly covers the target area: fetch it and harvest
  the postings beneath it.
- A company that keeps appearing but whose postings never surface directly: fetch its careers
  page once and harvest from there.

Also do a careers-page pass for a few companies from the target-companies list each run,
rotating through it.

### 4. Deduplicate

Write candidates to a scratch file (never paste dozens of URLs into a shell argument), then:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/job-scout/scripts/dedupe.py" --postings "<workspace>/<paths.postings_list>" --applications "<workspace>/<paths.applications>" < candidates.txt
```

It normalises URLs (strips tracking parameters, collapses LinkedIn URLs to the numeric job ID)
and drops anything already in the postings list under any date or linked from any note in the
applications folder. Survivors on stdout, summary on stderr. Use `python3` if `python` isn't on
PATH. Never skip this step.

### 5. Verify each survivor is live and inside the window

**This is the gate. Nothing reaches the postings list without passing it.**

Fetch each survivor once (for LinkedIn, the guest per-posting endpoint) and answer two questions.
Keep the page in view for step 6, so one fetch serves both.

**Q1: when was it published?** Use the first of these the page gives:
1. JSON-LD `JobPosting` `datePosted` / `validThrough`;
2. a visible posted date or age ("3 days ago"; anything at or beyond "1 month ago" fails a 30-day
   window);
3. a date in the URL or slug;
4. an application deadline implying a recent posting (corroboration only, never alone).

On or after the cut-off passes. Before it fails: log under `Outside the freshness window` with
link and date, even if the posting is clearly still open. If **no date** can be established, keep
it only with strong positive evidence from Q2, and log it as `undated, liveness inferred`.

**Q2: is it still open?** Any one closure signal disqualifies:
- "No longer accepting applications", "Position filled", "Applications closed", or a local-
  language equivalent (see `sources.md`);
- a deadline already passed, or `validThrough` in the past;
- HTTP 404/410, or a redirect to a generic careers page, board root or search page. **Check the
  URL you actually landed on**, because a redirect to the board root is the classic silent expiry;
- an ATS "job not found" page (often HTTP 200);
- the apply route absent, disabled, or replaced by "see our other openings".

Positive evidence, at least one: a working apply route; `datePosted` in the window with no past
`validThrough`; a future deadline; the posting still present on the company's own board.

**When the two questions conflict, or the page is too thin to answer either, drop it** and log
it. **Two fetches maximum per posting.** If a login wall or bot check blocks verification twice,
keep it only if the search snippet itself carried a date inside the window, mark it `unverified`,
otherwise drop it under `Unverifiable`.

### 6. Screen the survivors

Coarse keep/drop on relevance, from the page already fetched. **Drop** only for:
- an exclusion from the parameters file;
- a different discipline entirely;
- an explicit hard blocker the user can't meet (citizenship, clearance, a language at a level they
  don't have, per `job-hunt.yaml` and the parameters). Log these under `Blocked by eligibility`
  rather than dropping them silently; the pattern is useful information;
- a location outside the target set with nothing else to recommend it.

**Keep** anything where the day-to-day work plausibly matches the CV even if the title is
unfamiliar. Seniority mismatch alone is not grounds to drop.

### 7. Tier the keepers

| Tier | Meaning |
|---|---|
| **A — strong** | Core skills are the substance of the role, location workable, no visible blocker |
| **B — worth assessing** | Real overlap but a significant unknown: adjacent domain, unclear seniority, partial match |
| **C — stretch or hidden** | Non-obvious match from a hidden/transferable query, or a strong match with a stated blocker |

Keep tier C. A C that `fit-check` scores at 8 is exactly what this pipeline is built for.

### 8. Write the postings list

Under today's `## YYYY-MM-DD` heading, append `- <url>` lines, tier A first, then B, then C.
- If today's heading exists (the user may add links by hand), append beneath the existing links.
  Don't create a second heading or touch what's there.
- If not, create it at the top, above the most recent day, matching the existing heading style.
- If a `fit-check` table already sits under today's heading, say so and ask before appending,
  since new links below an existing table would be missed.

### 9. Write the scouting log

Prepend a section (newest first). Create the file with a one-line header if it doesn't exist.

```markdown
## YYYY-MM-DD

**Freshness cut-off:** YYYY-MM-DD
**Queries run:** N (role X · skill X · domain X · tools X · transferable X · hidden X · ATS X)
**Hits:** N candidates → N after dedupe → N passed liveness → N kept

| Tier | Company | Title | Location | Posted | Liveness evidence | Found by | Why kept |
|---|---|---|---|---|---|---|---|
| A | … | [Title](url) | … | YYYY-MM-DD or "6 days ago" | the actual signal | query # or text | one clause |

### Outside the freshness window
- Company - [Title](url) — posted YYYY-MM-DD, N days old

### Closed or expired
- Company - [Title](url) — the closure signal found

### Unverifiable
- Company - [Title](url) — what blocked verification; kept as `unverified` or dropped

### Dropped
- Company - [Title](url) — reason

### Blocked by eligibility
- Company - [Title](url) — the stated bar

### Queries used this run
- …

### Notes for the next run
- …
```

`Posted` and `Liveness evidence` are the audit trail for the gate. Name the actual signal
(`datePosted 2026-08-04, apply form live`, `deadline 2026-09-01`, `present on Greenhouse board`),
never just "confirmed open".

**Every posting named in the log carries its link.** Two permitted exceptions, stated inline: a
bulk drop line covering many postings (`(bulk drop, no individual links kept)`), and a live
posting with no capturable URL, logged under `### Live but uncapturable` with the page it was
found on.

If a run drops far more postings to "outside the window" and "closed" than it keeps, say so in
chat. It usually means the queries are hitting aggregators rather than live boards.

### 10. Present

Keep the chat reply short; the detail lives in the log.
- One line of counts including the gate: queries, candidates, duplicates removed, **failed
  freshness, failed liveness**, kept by tier. Restate the cut-off.
- Tier A and B keepers as `Company - [Title](url) — location, posted <date or age>`. Tier C as a
  count plus the two or three most interesting, also linked.
- Anything needing a decision: an existing `fit-check` table today, a category that returned
  nothing (say which query needs rewriting), postings blocked purely by eligibility (linked).
- End with the next step: `/job-hunt-kit:fit-check` to score the day's list.

## Notes

- **Zero new postings is a real outcome.** Say so plainly, name the queries that ran, and suggest
  rotating to unused matrix entries rather than padding the list.
- If the user asks to widen or narrow the window for one run ("go back 60 days"), honour it, use
  it everywhere, and record the override in the log header.
- If the user asks for a specific slice ("just Germany today", "only ATS boards"), narrow the
  query subset and say in the log that the run was scoped.
- When a company proves productive, add it to the target-companies file and note that in the log.
- If the user wants only the queries, produce the subset table from the matrix and stop.
