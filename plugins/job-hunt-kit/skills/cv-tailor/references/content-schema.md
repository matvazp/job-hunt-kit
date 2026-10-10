# content.json: the tailored content of one application

`cv-tailor` writes one `content.json` per application folder. It is the **single source** for
both output formats: `scripts/render.py` turns it into `cv.docx`/`cover-letter.docx` (Word) or
`cv.tex`/`cover-letter.tex` (LaTeX), and `scripts/build.py` renders, builds and checks them.
To change a document, edit `content.json` and rebuild. Don't edit the generated files.

A complete worked example (fictional) is at `${CLAUDE_PLUGIN_ROOT}/examples/example-content.json`.
Copy its shape.

## Top level

| Key | Required | Notes |
|---|---|---|
| `paper` | no | `a4paper` (default) or `letterpaper`, from `documents.paper` |
| `identity` | yes | copied from `job-hunt.yaml` (below) |
| `eligibility` | yes | from `work_eligibility`, plus the posting's country |
| `cv` | yes | title and ordered sections |
| `letter` | no | omit to produce no cover letter |

Keys starting with `_` (e.g. `_comment`) are ignored.

## identity

```json
{
  "name": "Alex Sample",                       // identity.name: letter signature, metadata
  "name_with_title": "Alex Sample, M.Sc.",     // CV header and running head
  "location": "Utrecht, NL",
  "phone": "+31 6 0000 0000",
  "email": "alex.sample@example.com",
  "website":  { "label": "alexsample.example", "url": "https://alexsample.example" },  // or null
  "linkedin": { "label": "linkedin.com/in/alex", "url": "https://www.linkedin.com/in/alex/" },  // or null
  "photo": null                                 // or a filename COPIED INTO the application folder
}
```

## eligibility

```json
{
  "citizenship": "Portuguese",                  // or null
  "eligible_countries": ["Netherlands", "Portugal", "Germany"],
  "permit_note": "work permit required",        // or null
  "country": "Germany"                          // REQUIRED: the country of THIS posting
}
```

The renderer generates the eligibility sentence and appends it to the `glance` section. **Never
type an eligibility sentence yourself.** A missing `country` stops the build on purpose. A
country matching a listed one ignoring case is normalised to the listed spelling.

| Case | Sentence |
|---|---|
| country listed | Portuguese citizen, eligible to work in Germany |
| not listed | Portuguese citizen, open to relocation to Norway (work permit required) |
| no citizenship | Eligible to work in Germany / Open to relocation to Norway |

## cv

```json
{
  "title": "<exact job title from the posting>",
  "hyphenation_exceptions": ["LoRaWAN"],        // optional, LaTeX only: tool names never to hyphenate
  "sections": [ ... ]                           // rendered in this order
}
```

Every section has `type` and `heading`. Types:

| type | Fields | Word / LaTeX rendering |
|---|---|---|
| `paragraph` | `text`: string or list of strings | body paragraph(s) |
| `qualities` | `items`: short phrases; `columns` (LaTeX, default 3) | one line, `·`-separated / balanced columns |
| `glance` | like `qualities` | same, **plus the eligibility sentence last**. Exactly one per CV, required |
| `skills` | `groups`: `[{label, text}]` | bold navy label — keyword list |
| `experience` | `entries`: `[{role, org, dates, bullets: []}]` | role, org line with right-aligned dates, bullets |
| `education` | `entries`: `[{degree, institution, dates}]` | degree with dates, institution below |
| `languages` | `items`: `[{language, level}]` | one line: **English** — Fluent · … |
| `list` | `items`: strings | plain bullets (projects, publications, certifications…) |

The usual order: Profile (`paragraph`), Key Strengths (`qualities`), Core Competencies
(`skills`), Professional Experience, Education, Languages, At a Glance (`glance`). Reorder or add
`list` sections when the posting calls for it.

## letter

```json
{
  "title": "<job title>",                       // optional, defaults to cv.title
  "date": "Utrecht, 10 October 2026",           // "<documents.date_city>, <D Month YYYY>"
  "recipient": ["Company", "Hiring Manager, Title", "Street", "Postcode City, Country"],
  "subject": "Application: <job title>",
  "salutation": "Dear Hiring Team,",
  "paragraphs": ["…", "…", "…"],
  "sign_off": "Kind regards,",                  // documents.sign_off
  "signature_name": "Alex Sample"               // identity.name
}
```

The signature contact line (site · email · phone) is added automatically. Don't put contact
details in the paragraphs.

## Inline markup (all text fields)

- `**bold**`
- `[label](https://url)` for a link (the cover letter's one portfolio link)
- `"straight quotes"` become curly quotes in both formats

Everything else is literal: write `&`, `%`, `#`, `µ`, `²` and so on as plain characters; the
renderer escapes them for LaTeX. Write dates with an en dash: `2019 – 2022`.
