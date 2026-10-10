# Sources

Domain allowlists, URL patterns and freshness/liveness signals for `job-scout`. The user's own
target-company list lives in their workspace (`paths.target_companies` in `job-hunt.yaml`), not
here.

The allowlists below are a starting point weighted towards Europe. If the user searches in a
region not covered, build an equivalent set for it (national job boards, the region's common ATS
hosts, LinkedIn) and suggest they add it to their workspace notes.

## Why allowlists matter

`WebSearch` may run from a US locale. Unfiltered non-US job queries tend to return US postings,
Glassdoor/Indeed category pages and index entries a year stale. Pairing the query with
`allowed_domains` is the single most effective fix: the same query that returns aggregator
category pages unfiltered returns live postings on native boards with an allowlist.

Also put the country or city in the query string itself, and add the current year to push out
stale entries.

## Allowlist sets

**Nordic** — Denmark, Sweden, Norway, Finland.
```
jobindex.dk, jobbank.dk, thehub.io, jobsinenglish.dk, workindenmark.dk,
arbetsformedlingen.se, finn.no, duunitori.fi, teamtailor.com, linkedin.com
```

**EU-wide** — Europe, Germany, Netherlands, Belgium, Ireland, Austria.
```
eures.europa.eu, linkedin.com, thehub.io, academictransfer.com,
stepstone.de, indeed.nl, irishjobs.ie, vdab.be, karriere.at
```

**Southern Europe** — Spain, Portugal, Italy. Run local-language forms of queries too when the
user speaks the language; they reach employers the English form never returns.
```
linkedin.com, infojobs.net, tecnoempleo.com, net-empregos.com, infojobs.it,
jobs.smartrecruiters.com, apply.workable.com, myworkdayjobs.com, boards.greenhouse.io
```

**UK & Ireland**
```
linkedin.com, reed.co.uk, totaljobs.com, cwjobs.co.uk, jobs.ac.uk, irishjobs.ie
```

**North America**
```
linkedin.com, wellfound.com, builtin.com, usajobs.gov, jobbank.gc.ca
```

**ATS hosts** — for ATS-category queries, and whenever a company's own board is the likeliest
place a role lives.
```
boards.greenhouse.io, job-boards.greenhouse.io, jobs.lever.co, jobs.smartrecruiters.com,
apply.workable.com, jobs.ashbyhq.com, myworkdayjobs.com, teamtailor.com, jobvite.com,
recruitee.com, jobylon.com, emply.com, hr-manager.net, personio.de, bamboohr.com
```

**Research / academic-adjacent** — research-scientist, research-engineer and lab roles.
Industrial R&D roles appear here too; apply the user's exclusions (e.g. PhD-student positions).
```
euraxess.ec.europa.eu, nature.com, academictransfer.com, jobs.ac.uk, academicpositions.com
```
EURAXESS often serves postings whose deadlines are long past as current results. Always check
the deadline there.

## Direct posting vs. listing URLs

Keep only direct postings:

| Host | Posting (keep) | Listing / search page (follow, then harvest) |
|---|---|---|
| linkedin.com | `/jobs/view/<id>` | `/jobs/search/?…`, `/jobs/<keyword>-jobs-…` |
| jobindex.dk | `/vis-job/<id>`, `/jobannonce/<id>/…` | `/jobsoegning?q=…` |
| thehub.io | `/jobs/<hash>` | `/jobs/location/…`, `/jobs?…` |
| euraxess.ec.europa.eu | `/jobs/<id>` | `/jobs/search?…` |
| boards.greenhouse.io | `/<company>/jobs/<id>` | `/embed/job_board?for=…`, `/<company>` |
| jobs.lever.co | `/<company>/<uuid>` | `/<company>` (company board) |
| *.myworkdayjobs.com | `/…/job/<location>/<title>_<req>` | `/…/<board>` with only query filters |
| apply.workable.com | `/<company>/j/<id>/` | `/<company>/` |
| jobs.smartrecruiters.com | `/<company>/<numeric-id>-<slug>` | `/<company>` |
| jobsinenglish.dk | `/ads/<slug>-<date>/` | `/category/…` |

**Always discard:** glassdoor.com, indeed.* job-category pages, ziprecruiter, expertini, jooble,
talent.com and similar scrapers. Their pages are aggregated re-posts that go stale, often lack the
real application route, and duplicate postings already found at source. A scraped re-post
routinely outlives the vacancy it copied and still looks current. Also discard Wikipedia and
company "about" pages.

**Company careers homepages** are not postings. They are still worth one fetch when a company
keeps surfacing without direct hits, and again later to confirm whether a req found elsewhere is
still open.

## Freshness and liveness signals

**Check JSON-LD first, everywhere.** Most ATS hosts and major boards embed a
`schema.org/JobPosting` block carrying `datePosted` and `validThrough`. It is exact, present when
the visible page shows no date, and a `validThrough` in the past definitively means the posting is
closed.

**LinkedIn guest endpoints** render server-side without a login:

```
Discovery (10 dated postings per page, past 30 days):
https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=<terms>&location=<country or city>&f_TPR=r2592000&start=0

Per posting (description, posted age, closure notice):
https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/<numeric-id>
```

`f_TPR=r2592000` = past 30 days, `r604800` = past week. Page with `&start=10`, `&start=20`. Each
search result carries a posted-age string, so one fetch applies the freshness gate to ten
candidates at once. Be considerate: keep request volume modest, don't hammer these endpoints, and
respect LinkedIn's terms. If they stop working, fall back to `WebSearch` with the allowlists
above.

**Recency-filtered listing views** triage a page of candidates for the cost of one fetch:

| Host | Recency control |
|---|---|
| linkedin.com | `&f_TPR=r2592000` (30 days) / `r604800` (week) |
| jobindex.dk | `&sort=date` on `/jobsoegning?q=…` |
| thehub.io | `/jobs?sorting=newest` |
| greenhouse / lever / workable | company boards list current reqs only. Presence on the board *is* the liveness check |

**Per-host date and closure cues**

| Host | Where the date is | What closure looks like |
|---|---|---|
| linkedin.com | Relative age ("18 hours ago", "3 weeks ago") via the guest endpoint | "No longer accepting applications"; redirect to `/jobs/` |
| jobindex.dk | Posted date on listing; `Ansøgningsfrist` on posting | *Ansøgningsfristen er udløbet*; 404 |
| thehub.io | "Posted" date on job page | 404 or redirect to `/jobs` |
| jobsinenglish.dk | Date in the slug | Deadline passed in body text |
| euraxess.ec.europa.eu | Explicit posted and deadline fields | Deadline in the past (very common) |
| boards.greenhouse.io | JSON-LD | "This job is no longer available"; redirect to board root |
| jobs.lever.co | JSON-LD | "Job not found" page, often HTTP 200 |
| *.myworkdayjobs.com | "Posted On" ("Posted 30+ Days Ago" = fail) | Redirect to the board landing page |
| apply.workable.com | JSON-LD `datePosted` | "This job is closed" banner |
| jobs.smartrecruiters.com | JSON-LD `datePosted` | 404, or redirect to company board |

**Closure phrases in other languages** (extend for the user's markets):
Danish *Ansøgningsfristen er udløbet*, *Stillingen er besat*; Swedish *Ansökningstiden har gått
ut*; German *Diese Stelle ist nicht mehr verfügbar*, *Bewerbungsfrist abgelaufen*; Dutch *Deze
vacature is gesloten*; Spanish *Esta oferta ya no está disponible*, *Oferta cerrada*; French
*Cette offre n'est plus disponible*; Portuguese *Esta vaga já não está disponível*.

**Watch the landed URL, not the requested one.** The most common silent expiry on every ATS host
is a 200-OK redirect from a dead req to the board root or a generic careers page. The page looks
healthy and lists other jobs, but the vacancy is gone. Always confirm the URL you ended up on
still identifies the specific posting.
