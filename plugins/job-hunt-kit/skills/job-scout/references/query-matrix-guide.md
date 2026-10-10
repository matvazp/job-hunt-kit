# Building the query matrix

`job-scout` searches from a standing matrix of queries kept in the user's workspace
(`paths.query_matrix`, default `search/query-matrix.md`). This guide is how to (re)generate it.
`setup` generates the first version; `job-scout` regenerates it when `search-parameters.md`
gains a role, technology or location no query reflects.

## Rules

- **Every query traces to the sources.** Each must come from something in
  `search-parameters.md` or `master-cv.md`. Never invent a skill, tool or domain to search for.
- **About 100 queries across seven categories**, in roughly these proportions. Scale down for a
  narrow profile (60 is fine), but keep every category.

| Category | Share | What it is |
|---|---|---|
| A. Role-based | 20% | Target job titles and close variants, paired with locations |
| B. Skill-based | 20% | Specific technologies, tools, methods or materials the user has actually used |
| C. Domain / industry | 15% | Target industries and sectors, paired with a function |
| D. Tools / equipment / technique | 15% | Named instruments, platforms, software or techniques. These find specialist roles whose titles say nothing |
| E. Transferable-skill | 10% | The user's core capabilities phrased as other professions would phrase them |
| F. Hidden-match | 10% | **Deliberately avoids the user's target titles.** Describes the work, not the job title. Highest yield; never drop the whole block from a run |
| G. ATS / company careers | 10% | `site:` queries against ATS hosts from `sources.md`, combining role/skill keywords |

- **Spread locations** across the countries/cities in the parameters file, weighted by the user's
  priority, plus some region-wide queries ("Europe", "remote EU", etc.).
- **Language.** Add local-language forms of queries only for languages the user is fluent in.
  Queries in a language they don't speak surface ads that require it.
- Keep queries short (3–7 terms). Long queries over-constrain search engines.

## File format

```markdown
# Query matrix

Built from `search-parameters.md` and `master-cv.md`. Last regenerated **YYYY-MM-DD**.

**Category counts:** role N · skill N · domain N · tools N · transferable N · hidden N · ATS N.
**Location coverage:** <country N · country N · …>

## A. Role-based (N)

| # | Query | Location | Reason |
|---|---|---|---|
| 1 | `<query terms>` | <location> | <what in the sources this traces to> |

## B. Skill-based (N)
…
## G. ATS / company careers (N)
```

Number queries consecutively across categories so the scouting log can reference them by number.
The **Reason** column is the trace back to the sources; keep it to one clause.

## Execution notes for job-scout

- Run most role/skill/domain/tools/transferable/hidden queries through the LinkedIn guest search
  endpoint (see `sources.md`). It is pre-filtered to recent postings and returns dated results.
- Run ATS queries with `WebSearch`, once with the `site:` operator as written and once as a plain
  query with the host in `allowed_domains`.
- Use `WebSearch` with an allowlist for native national boards that LinkedIn covers poorly.
