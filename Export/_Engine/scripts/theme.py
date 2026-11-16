"""Build a temporary Pandoc Word reference using only a JSON theme and stdlib."""
from io import BytesIO
import json
import re
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
ET.register_namespace('w', W)
def tag(name):
    return f'{{{W}}}{name}'

def set_element(parent, name, **attrs):
    node = parent.find(tag(name))
    if node is None:
        node = ET.SubElement(parent, tag(name))
    node.attrib.clear()
    node.attrib.update({tag(k): str(v) for k, v in attrs.items()})
    return node

def properties(parent, name):
    node = parent.find(tag(name))
    return node if node is not None else ET.SubElement(parent, tag(name))

def apply(style, values):
    link = style.find(tag('link'))
    if link is not None:
        style.remove(link)
    run = properties(style, 'rPr')
    paragraph = properties(style, 'pPr')
    # Remove built-in theme fonts, sizes, and colors before applying our values.
    for name in ('rFonts', 'sz', 'szCs', 'color', 'b', 'bCs', 'i', 'iCs'):
        node = run.find(tag(name))
        if node is not None:
            run.remove(node)
    set_element(run, 'rFonts', ascii=values['font'], hAnsi=values['font'], eastAsia=values['font'], cs=values['font'])
    for name in ('sz', 'szCs'):
        set_element(run, name, val=round(values['size_pt'] * 2))
    color = values['color'].lstrip('#')
    if not re.fullmatch('[0-9a-fA-F]{6}', color):
        raise ValueError(f'Expected six-digit hex color, got {values["color"]!r}')
    set_element(run, 'color', val=color.upper())
    for name in ('b', 'bCs'):
        set_element(run, name, val=int(values.get('bold', False)))
    for name in ('i', 'iCs'):
        set_element(run, name, val=0)
    set_element(paragraph, 'spacing', before=round(values['space_before_pt'] * 20), after=round(values['space_after_pt'] * 20), line=round(values['line_spacing'] * 240), lineRule='auto')
    set_element(paragraph, 'jc', val='left')
    set_element(paragraph, 'ind', left=0, right=0, firstLine=0)
    set_element(paragraph, 'keepNext', val=int(values.get('keep_with_next', False)))
    set_element(paragraph, 'pageBreakBefore', val=0)

def build_reference(pandoc, theme_path, output):
    theme = json.loads(theme_path.read_text())
    base = subprocess.check_output([pandoc, '--print-default-data-file=reference.docx'])
    with ZipFile(BytesIO(base)) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    fonts = ET.fromstring(files['word/fontTable.xml'])
    for font in {theme['body']['font']} | {v['font'] for v in theme.values() if isinstance(v, dict) and 'font' in v}:
        if not any(f.get(tag('name')) == font for f in fonts):
            item = ET.SubElement(fonts, tag('font'), {tag('name'): font})
            set_element(item, 'family', val='swiss')
            set_element(item, 'pitch', val='variable')
    # Do not embed Arial Black here. Pandoc copies the embed relationship into the
    # exported document and drops the font file, and LibreOffice then refuses to open it.
    # Export installs Arial Black and subsets it into the PDF instead.
    files['word/fontTable.xml'] = ET.tostring(fonts, encoding='utf-8', xml_declaration=True)
    styles = ET.fromstring(files['word/styles.xml'])
    by_id = {s.get(tag('styleId')): s for s in styles.findall(tag('style'))}
    groups = {'Normal': {}, 'BodyText': {}, 'FirstParagraph': {}, 'Title': theme['title'], 'Heading1': theme['section_heading'], 'Heading2': theme['job_heading'], 'Compact': theme['bullets']}
    for name, overrides in groups.items():
        values = dict(theme['body'], **overrides)
        values['keep_with_next'] = name in ('Title', 'Heading1', 'Heading2')
        apply(by_id[name], values)
    hyperlink = properties(by_id['Hyperlink'], 'rPr')
    color = theme['links']['color'].lstrip('#')
    if not re.fullmatch('[0-9a-fA-F]{6}', color):
        raise ValueError('Invalid link color')
    set_element(hyperlink, 'color', val=color.upper())
    set_element(hyperlink, 'u', val='single' if theme['links']['underline'] else 'none')
    document = ET.fromstring(files['word/document.xml'])
    section = document.find('.//' + tag('sectPr'))
    page = theme['page']
    set_element(section, 'pgSz', w=round(page['width_in'] * 1440), h=round(page['height_in'] * 1440))
    set_element(section, 'pgMar', **{side: round(page[f'margin_{side}_in'] * 1440) for side in ('top', 'bottom', 'left', 'right')}, header=720, footer=720, gutter=0)
    # ElementTree drops unused prefix declarations; remove compatibility hints
    # that could refer to those prefixes after serialization.
    for root in (styles, document):
        for element in root.iter():
            element.attrib.pop('{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable', None)
    files['word/styles.xml'] = ET.tostring(styles, encoding='utf-8', xml_declaration=True)
    files['word/document.xml'] = ET.tostring(document, encoding='utf-8', xml_declaration=True)
    with ZipFile(output, 'w') as archive:
        for name, content in files.items():
            archive.writestr(name, content)
