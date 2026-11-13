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

Each run creates a new folder under `Export/<role folder>/` named `[resume name] - [timestamp]`, containing the source filename with `.docx` and `.pdf` extensions. For example: `Export/Design jobs/Resume 2026 -  Design - 2026-11-13_12-30-00-123456/`. Timestamps use America/Denver time and include microseconds to distinguish quick repeat runs. All resumes exported in one run share the same timestamp. The folder is created after both formats have been generated successfully; earlier generations are preserved. Generated files are ignored by Git; `Export/_Engine/` is tracked.

The engine resolves paths from its own location, so the direct Python command also works from another directory when given the full script path. Source arguments are always relative to the repository root.

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
