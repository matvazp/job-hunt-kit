# CV & cover letter LaTeX template

A navy-and-black two-page CV and matching one-page cover letter, built to pass ATS
(applicant tracking system) parsing. Used when `documents.format` is `latex` or `both`; the
Word alternative is in [`../word/`](../word/README.md).

`cv-tailor` doesn't write LaTeX directly. It writes the tailored content to `content.json`,
and `skills/cv-tailor/scripts/render.py` generates `cv.tex` and `cover-letter.tex` from it,
using the macros below, and copies `jobcv.sty` into the application folder. `cv.tex` and
`cover-letter.tex` here are hand-written worked examples for a fictional person, useful if you
want to write or edit LaTeX yourself (build hand-edited files with `build.py --no-render`).

## Files

| File | Purpose |
|---|---|
| `jobcv.sty` | Shared style: colours, header band, section commands. Edit this to change the *look*. |
| `cv.tex` | Example CV. |
| `cover-letter.tex` | Example cover letter. |

To customise the look for yourself, copy `jobcv.sty` into your workspace's `templates/` folder.
`cv-tailor` uses that copy instead of the bundled one when it exists.

## Building

```
pdflatex cv.tex
pdflatex cv.tex          # second pass resolves the "1 / 2" page counter
```

Same for `cover-letter.tex`. You need a TeX distribution (TeX Live or MiKTeX) and
**pdflatex specifically**, because the ATS fixes below depend on pdfTeX primitives.
Packages used: geometry, fontenc, inputenc, sourcesanspro, microtype, anyfontsize, xcolor,
multicol, tikz, enumitem, fancyhdr, lastpage, graphicx, ragged2e, needspace, csquotes,
hyperref. All are in a full TeX Live install.

## Identity and eligibility macros

```latex
\cvname{Alex Sample, M.Sc.}
\cvtitle{<exact job title from the posting>}   % header band, running head, PDF metadata
\cvlocation{Utrecht, NL}
\cvphone{+31 6 0000 0000}
\cvemail{alex.sample@example.com}
\cvsite{alexsample.example}{https://alexsample.example}            % optional
\cvlinkedin{linkedin.com/in/alex-sample}{https://linkedin.com/...}  % optional
\cvphoto{headshot.jpg}                                              % optional; off by default

\cvcitizenship{Portuguese}                                % optional
\cveligiblein{Netherlands, Portugal, Germany}             % where you may already work
\cvcountry{Germany}                                       % REQUIRED: this posting's country
\cvpermitnote{work permit required}                       % optional, shown when not eligible
```

`\permitline` (used in At a Glance) turns these into one sentence:

| Case | Output |
|---|---|
| country in `\cveligiblein` | *Portuguese citizen, eligible to work in Germany* |
| country not in the list | *Portuguese citizen, open to relocation to Norway (work permit required)* |
| no `\cvcitizenship` | *Eligible to work in Germany* / *Open to relocation to Norway* |
| `\cvcountry` missing | **build fails** with `Package jobcv Error: \cvcountry not set` |

The failure is deliberate. A hand-typed eligibility line is right for one country and
confidently wrong for every other one, and nobody notices a wrong-but-plausible line when
proofreading. Making the posting's country a required input turns that silent mistake into
a build error. Write the country the same way in `\cvcountry` and `\cveligiblein`: the
comparison is exact text.

## Structure macros

`\makecvheader`, `\cvsection{}`, `\cventry{Role}{Org, Location}{Dates}`,
`\skillgroup{Label}{Content}`, `\eduentrywide{Degree}{Institution}{Years}`, `\langline{}`,
`\quality{}`, `\compactcols{n}{...}`, `cvbullets` environment.
Cover letter: `\cldate{}`, `\clrecipient{}`, `\clsubject{}`, `\clsalutation{}`, `clbody`
environment, `\clclosing{sign-off}{name}`. Links in running text: `\weblink{url}{text}`.

## Design rules

- **12pt base, 1.15 leading.** Chosen for legibility. Two pages hold about **550–600
  extracted words** (measure with `pdftotext cv.pdf - | wc -w`). If a document runs long,
  **cut content; never shrink the type or the leading.** Overrunning doesn't break the layout,
  it just adds a third page without warning.
- **Keep `\documentclass[12pt,a4paper]{article}`.** The structural sizes are scaled for a
  12pt base. At 10pt or 11pt the section headings come out smaller than the body text.
- **Single column.** One reading order, which is the safest structure for weak parsers.
  Short lists (key strengths, at-a-glance facts) use `\compactcols{3}{...}`.
- **Two colours plus one for links.** `navy` for structure, black for body text, and
  `linkblue` only for `\weblink`. hyperref runs with `hidelinks`, so a bare `\href` renders
  black and doesn't look like a link. Don't turn on `colorlinks` globally: it would paint the
  header links dark blue on the navy band.
- **Signature is automatic.** `\clclosing` prints site · email · phone under the name from
  the identity macros. Don't add contact details by hand or they will appear twice.

## ATS compatibility

- **ToUnicode CMap** (`\pdfgentounicode=1`) so ligatures extract as letters ("Profile", not
  "Pro le").
- **No letterspacing** on the job title or section headings. `\textls` makes text extract as
  `E N G I N E E R`.
- **microtype expansion off.** Expansion shifts glyphs enough to split words (`L Tspice`).
- **Explicit separators.** A literal space before every `\hfill`, and a real em dash in
  `\skillgroup`, so neighbouring text never runs together in extraction.
- **No icon fonts.** They extract as private-use junk characters.
- **Drawn list markers**, not glyphs.
- **Hyphenation exceptions for tool names.** A break like `Or-CAD` survives into the text
  layer and defeats keyword matching. Add your own tool names with `\hyphenation{...}`. Keep the
  list to proper nouns, because ordinary words starve the line breaker.
- **PDF metadata** (title, author, subject) is set from `\cvname` and `\cvtitle`.

To check a build, extract the text with `pdftotext` or `pdfminer.six` and confirm that the
job title, section headings, contact details and key tool names all appear as real words.

## Known quirks

- If you change the geometry `top` margin or `\bandheight`, adjust `\headerpush` to match:
  `\headerpush = \bandheight - top + 7mm` (currently 32 − 22 + 7 = 17mm). Changing one alone
  either pushes the page-2 running head against the paper edge or slides page-1 text into the
  navy band.
- The headshot is built into a box before the header's overlay picture (see `\roundphoto`).
  A tikzpicture nested inside an overlay picture inherits `overlay` and puts the image in the
  wrong place.
- Photos are normal in some countries (e.g. Germany, Denmark) and discouraged in others
  (e.g. US, UK). The photo is off unless you call `\cvphoto{...}`.
