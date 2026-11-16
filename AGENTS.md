# Agent context

`Export/Latest/` is the address the portfolio site uses for the current resume. A push of resume Markdown or export-engine changes to `main` runs `.github/workflows/export-resumes.yml`, which overwrites the PDF and Word files there and stores that same run under a timestamped folder in `Export/<role>/`.

Do not rename role folders or resume Markdown filenames, move or delete `Export/Latest/`, or change those output names. Any of those breaks the public URL. The link and the rest of the publishing setup are in the README section "Published copies".
