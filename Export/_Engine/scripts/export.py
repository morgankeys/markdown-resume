#!/usr/bin/env python3
"""Export one resume or all role-folder resumes through Pandoc and LibreOffice."""
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from theme import build_reference

ENGINE = Path(__file__).resolve().parents[1]
ROOT = ENGINE.parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', nargs='?', help='Markdown path relative to the repository')
args = parser.parse_args()
pandoc = shutil.which('pandoc')
bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/MacOS/soffice'
soffice = os.environ.get('SOFFICE') or (str(bundled) if bundled.exists() else shutil.which('soffice'))
if not pandoc or not soffice:
    parser.exit(1, 'Requires Pandoc and LibreOffice. See README.md for setup.\n')
sources = [ROOT / args.source] if args.source else sorted(p for p in ROOT.glob('*/*.md') if p.parts[-2] not in {'Export', 'Reference', 'styles', 'scripts'})
if not sources:
    parser.exit(1, 'No resume Markdown files found.\n')
timestamp = datetime.now(ZoneInfo('America/Denver')).strftime('%Y-%m-%d_%H-%M-%S-%f')
for source in sources:
    source = source.resolve()
    if not source.is_file() or source.suffix.lower() != '.md' or not source.is_relative_to(ROOT):
        parser.exit(1, f'Invalid resume source: {source}\n')
    relative = source.relative_to(ROOT)
    if relative.parts[0] in {'Export', 'Reference', 'styles', 'scripts'} or len(relative.parts) < 2:
        parser.exit(1, 'Choose a resume inside a role folder.\n')
    output = ROOT / 'Export' / relative.parent / f'{source.stem} - {timestamp}'
    # Build in isolation so stale PDFs cannot be mistaken for a successful export.
    with tempfile.TemporaryDirectory(prefix='resume-export-') as temp:
        temp = Path(temp)
        reference = temp / 'reference.docx'
        build_reference(pandoc, ENGINE / 'styles/theme.json', reference)
        docx = temp / source.with_suffix('.docx').name
        subprocess.run([pandoc, str(source), '--reference-doc', str(reference), '-o', str(docx)], check=True)
        subprocess.run([soffice, '-env:UserInstallation=' + (temp / 'lo-profile').as_uri(), '--headless', '--convert-to', 'pdf:writer_pdf_Export', '--outdir', str(temp), str(docx)], check=True)
        pdf = docx.with_suffix('.pdf')
        if not pdf.exists() or pdf.stat().st_size == 0:
            raise RuntimeError('LibreOffice did not produce a PDF')
        # Publish only completed generations; never overwrite an earlier run.
        output.parent.mkdir(parents=True, exist_ok=True)
        output.mkdir(exist_ok=False)
        for file in (docx, pdf):
            shutil.copy2(file, output / file.name)
            print((output / file.name).relative_to(ROOT))
