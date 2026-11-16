# Markdown resume

Edit resumes in role folders, then export Word and PDF copies with shared styling.

## Export

Requires Python 3.9+, Pandoc (`brew install pandoc`), and LibreOffice. In Codex, the export script automatically uses the bundled LibreOffice. Elsewhere, put `soffice` on PATH or set `SOFFICE` to its executable path (on macOS, typically `/Applications/LibreOffice.app/Contents/MacOS/soffice`).

```sh
make -f Export/_Engine/Makefile export
```

Export a particular version:

```sh
make -f Export/_Engine/Makefile export SOURCE='Design jobs/Resume 2026 -  Design.md'
```

Or run `python3 Export/_Engine/scripts/export.py 'Design jobs/Resume 2026 -  Design.md'` directly.

The engine resolves paths from its own location, so the direct Python command also works from another directory when given the full script path. Source arguments are always relative to the repository root.

Each run writes two copies of every resume, and only after both the Word file and the PDF have been generated successfully.

1. A timestamped folder under `Export/<role folder>/` named `[resume name] - [timestamp]`, containing the source filename with `.docx` and `.pdf` extensions. For example: `Export/Design jobs/Resume 2026 -  Design - 2026-11-13_12-30-00-123456/`. Timestamps use America/Denver time and include microseconds to distinguish quick repeat runs. All resumes exported in one run share the same timestamp. Earlier generations are preserved and never overwritten.
2. The same two files, with no timestamp in the name, at `Export/Latest/<role folder>/`. This copy is replaced on every run. For the current design resume the stable files are `Export/Latest/Design jobs/Resume 2026 -  Design.pdf` and `Export/Latest/Design jobs/Resume 2026 -  Design.docx`. Another Markdown resume in a role folder gets its own pair beside those, named from its filename.

`Export/_Engine/` is tracked. Generated resumes are ignored for ordinary commits, so a local preview export does not become part of a content change. Once CI has published `Export/Latest/`, a later local export will modify those tracked files; leave them out of the commit. Pushing to `main` republishes them.

## Published copies

Pushing resume Markdown or export-engine changes to `main` runs `.github/workflows/export-resumes.yml`. The workflow installs Pandoc, LibreOffice, Arial, and Arial Black, runs the export, and commits both the timestamped record and the `Latest` copies. Those faces are subset into the PDF, so the published file does not depend on the viewer's fonts. README-only edits do not trigger it. The publish commit is made with the Actions token, which does not start another workflow run, and the commit contains only files under `Export/`, which are outside the workflow's path filter.

The portfolio site should link to the Latest PDF on `main`. This repository is public, so the address below keeps serving the newest export without changing the path:

https://github.com/morgankeys/markdown-resume/raw/main/Export/Latest/Design%20jobs/Resume%202026%20-%20%20Design.pdf

That link is a direct file URL a visitor can open or download. It keeps working only while this path stays on `main`. Do not rename the role folder or the Markdown file, move `Export/Latest/`, or stop committing the Latest files. Renaming the source changes the filename and breaks the site. GitHub serves the file from the repository; it is not a separate CDN, and embedding the PDF in an iframe on another site may be blocked. A new resume version needs its own link, using the same `Export/Latest/<role folder>/<markdown name>.pdf` pattern.

## Content and versions

- `Design jobs/`: current design resumes. Add a separate Markdown file for each named version or tailored application.
- Add other role folders alongside it when needed. The default export finds Markdown files directly inside each role folder.
- `Reference/`: future case studies and supporting material; excluded from exports.
- `Export/_Engine/styles/theme.json`: editable fonts, colors, spacing, and page setup. Kept separate from supporting reference materials.
- Git tracks the editing history of each Markdown version.

Markdown conventions: YAML `title` for your name, `#` for section headings, `##` for job or school headings, `*` for bullets, and normal Markdown links and bold text. Blank lines separate paragraphs; extra blank lines do not add export spacing.

## Styling

Edit `Export/_Engine/styles/theme.json` in any text editor, save it, then rerun the export. No Word template editing is needed. The exporter generates a temporary DOCX style reference from this config on each run using Pandoc's built-in defaults. The old `reference.docx` is no longer used.

- `body`: default font, size, color, line spacing, and paragraph spacing.
- `title`: your name.
- `section_heading`: `#` headings (currently red `#CC0000`).
- `job_heading`: `##` job and school headings.
- `bullets`: bullet paragraph text and spacing.
- `links`: hyperlink color and underline.
- `page`: page dimensions and margins in inches.

All text groups inherit unspecified properties from `body`. Sizes and paragraph spacing use points; `line_spacing` is a multiplier (e.g. `1.15`). Colors are six-digit hex strings such as `"#CC0000"`. Set `bold` to `true` or `false`. JSON does not allow comments or trailing commas.

For example, to make section headings blue with more space above them, change `section_heading.color` to `"#245B8F"` and `section_heading.space_before_pt` to `24`.

The source Google Doc used some manual blank paragraphs and direct formatting. This template preserves its core typography while expressing spacing through styles. PDF is generated from the exported DOCX, so both follow the same layout engine. Word or Google Docs may repaginate the DOCX when opened; the PDF is the fixed-layout version. Install the same fonts for consistent results across computers.
