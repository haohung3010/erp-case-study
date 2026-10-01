# -*- coding: utf-8 -*-
"""build_docs.py -- build the report and the cutover plan: Markdown to .docx to PDF, numbers filled from one file.

PURPOSE
  The case study quotes the same numbers in four places. Here every number is a {{key}} placeholder filled from
  docs/numbers.json (written by docs/figures.py), so the report, the cutover plan, the README and the deck cannot
  disagree. The build refuses rather than ship a document with an unfilled number or a broken writing rule.

CONFIG
  argv[1]  the repository root; optional argv[2:] names to build only matching sources.
  Needs python-docx and pypdf; PDF by ONLYOFFICE through scripts/to_pdf.py.
  Style: the portfolio's report design (ink #16232B, primary #1D5C6B, accent #906915, rule #D5DDE0, surface
  #F1F5F6). IBM Plex is not installed on the build machine, so headings are Cambria and body text Calibri.

WORKFLOW
  1 for each document: read its Markdown, fill {{key}} from numbers.json
  2 lint: refuse an unfilled {{key}} or an em dash; list every sentence over 30 words (a warning)
  3 write .docx: cover or title block, headings, paragraphs, bullets, numbered lists, tables, figures with captions,
    callouts ("> **Label.** text"), page breaks ("\\pagebreak"), landscape and portrait sections ("\\landscape",
    "\\portrait"), inline code in backticks, a footer with the product name and page n of N
  4 convert to PDF; read it back with pypdf: the text layer holds the title and no "{{", and the page count is within
    the document's limit
  5 [CONTROL] the lint is shown able to refuse a planted unfilled key and a planted em dash before any document runs
  rc 0 ok . 2 usage . 3 a document was refused

Q&A
  Q: why not Pandoc?   A: it is not installed; python-docx is, and the author's other harness builds its documents
                          the same way (python-docx, then ONLYOFFICE).
  Q: why a subset of Markdown?   A: the documents need only these constructs; anything else would pass through as text
                                    and be seen on the page, never silently dropped.

PITFALLS
  A page limit is checked on the PDF, not the .docx: the two can paginate differently. Look at every page.
  pypdf's text extraction drops some spacing, so the title test uses the part before the first colon only.

NOTES
  MARKDOWN SUBSET: "% " lines at the top (title, subtitle, then meta lines). "# " and "## " headings. "* " bullets.
  "1. " numbered. "|" tables with a separator row. "![caption](path)" a figure. "**bold**" inline.
  Tanmark Industries is fictional.
"""
import io
import json
import os
import re
import subprocess
import sys

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from pypdf import PdfReader

INK, PRIMARY, ACCENT, MUTED = "16232B", "1D5C6B", "906915", "5B6B73"
RULE, SURFACE, SOFT = "D5DDE0", "F1F5F6", "E3EEF0"
HEAD, BODY = "Cambria", "Calibri"
PRODUCT = "Tanmark Industries: an ERP case study"

DOCS = [  # source, output stem, page limit, cover
    ("docs/cutover-plan.md", "docs/cutover-plan", 1, False),
    ("docs/report.md", "docs/case-study-report", 16, True),
]
MD_DOCS = [  # Markdown out, same fill and lint: the README is generated so its numbers match the report
    ("docs/readme.md", "README.md"),
    ("working-papers/src/W11-business-case.md", "working-papers/W11-business-case.md"),
]


def rgb(h):
    return RGBColor.from_string(h)


def shade(obj, fill):
    if hasattr(obj, "_tc"):
        pr = obj._tc.get_or_add_tcPr()
    else:
        pr = obj._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pr.append(shd)


def border_bottom(par, color=RULE, size=6):
    ppr = par._p.get_or_add_pPr()
    b = OxmlElement("w:pBdr")
    e = OxmlElement("w:bottom")
    for k, v in (("w:val", "single"), ("w:sz", str(size)), ("w:space", "2"), ("w:color", color)):
        e.set(qn(k), v)
    b.append(e)
    ppr.append(b)


def cell_borders(table):
    pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom", "insideH"):
        e = OxmlElement("w:" + edge)
        for k, v in (("w:val", "single"), ("w:sz", "4"), ("w:color", RULE)):
            e.set(qn(k), v)
        borders.append(e)
    for edge in ("left", "right", "insideV"):
        e = OxmlElement("w:" + edge)
        e.set(qn("w:val"), "nil")
        borders.append(e)
    pr.append(borders)


def runs(par, text, size=None, color=INK, font=BODY, bold=False):
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part:
            continue
        b = part.startswith("**") and part.endswith("**")
        code = part.startswith("`") and part.endswith("`")
        r = par.add_run(part[2:-2] if b else (part[1:-1] if code else part))
        r.bold = bold or b
        face = "Consolas" if code else font
        r.font.name = face
        r._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), face)
        r.font.color.rgb = rgb(color)
        if size:
            r.font.size = Pt(size)
    return par


def field(par, code, size=8):
    for kind, text in (("begin", None), (None, code), ("end", None)):
        r = par.add_run()
        r.font.size = Pt(size)
        r.font.color.rgb = rgb(MUTED)
        if kind:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            r._r.append(fc)
        else:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = text
            r._r.append(it)


def setup(doc, one_page):
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    m = Inches(0.6 if one_page else 0.9)
    sec.left_margin = sec.right_margin = m
    sec.top_margin = Inches(0.5 if one_page else 0.9)
    sec.bottom_margin = Inches(0.5 if one_page else 0.8)
    st = doc.styles["Normal"]
    st.font.name = BODY
    st.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), BODY)
    st.font.size = Pt(9 if one_page else 10)
    st.font.color.rgb = rgb(INK)
    st.paragraph_format.space_after = Pt(2 if one_page else 6)
    st.paragraph_format.line_spacing = 1.05 if one_page else 1.2
    foot = sec.footer.paragraphs[0]
    runs(foot, PRODUCT + " . fictional company, illustrative numbers . page ", size=8, color=MUTED)
    field(foot, "PAGE")
    runs(foot, " of ", size=8, color=MUTED)
    field(foot, "NUMPAGES")


def cover(doc, meta):
    for _ in range(6):
        doc.add_paragraph()
    p = runs(doc.add_paragraph(), meta[0], size=26, font=HEAD, bold=True)
    p.paragraph_format.space_after = Pt(10)
    runs(doc.add_paragraph(), meta[1], size=13, color=PRIMARY, font=HEAD)
    border_bottom(doc.add_paragraph(), PRIMARY, 12)
    for line in meta[2:]:
        runs(doc.add_paragraph(), line, size=10, color=MUTED)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def title_block(doc, meta):
    p = runs(doc.add_paragraph(), meta[0], size=16, font=HEAD, bold=True)
    p.paragraph_format.space_after = Pt(1)
    p = runs(doc.add_paragraph(), " . ".join(meta[1:]), size=8.5, color=MUTED)
    border_bottom(p, PRIMARY, 8)


def heading(doc, text, level, one_page):
    size = {1: 11.5 if one_page else 16, 2: 10 if one_page else 11.5}[level]
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5 if one_page else (14 if level == 1 else 8))
    p.paragraph_format.space_after = Pt(1 if one_page else 4)
    p.paragraph_format.keep_with_next = True
    runs(p, text, size=size, color=PRIMARY if level == 1 else INK, font=HEAD if level == 1 else BODY, bold=True)


def table(doc, rows, one_page):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    cell_borders(t)
    size = 8 if one_page else 8.5
    t.autofit = False
    usable = 7.3 if one_page else 6.7  # inches of text width
    weight = [min(max(max(len(r[j].strip()) for r in rows), 9), 45) for j in range(len(rows[0]))]  # 9: a short bold header fits on one line
    widths = [Inches(usable * w / sum(weight)) for w in weight]
    for i, row in enumerate(rows):
        for j, text in enumerate(row):
            c = t.cell(i, j)
            c.width = widths[j]
            c.paragraphs[0].paragraph_format.space_after = Pt(0 if one_page else 1)
            if j > 0 and re.fullmatch(r"[-+]?[\d.,]+%?( days)?", text.strip()):
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
            runs(c.paragraphs[0], text.strip(), size=size, bold=(i == 0))
            if i == 0:
                shade(c, SURFACE)
    gap = doc.add_paragraph()
    gap.paragraph_format.space_after = Pt(0)
    gap.paragraph_format.line_spacing = 0.6 if one_page else 1.0


def figure(doc, root, caption, path, n):
    sec = doc.sections[-1]
    width = sec.page_width - sec.left_margin - sec.right_margin
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(os.path.join(root, path), width=min(width, Inches(9.2)))
    runs(doc.add_paragraph(), "Figure %d. %s" % (n, caption), size=8.5, color=MUTED)


def callout(doc, text):
    p = doc.add_paragraph()
    shade(p, SOFT)
    p.paragraph_format.left_indent = Inches(0.08)
    runs(p, text)


def lint(text):
    problems = []
    left = re.findall(r"\{\{[^}]+\}\}", text)
    if left:
        problems.append("unfilled: %s" % sorted(set(left)))
    if "—" in text:
        problems.append("em dash on %d line(s)" % sum("—" in l for l in text.splitlines()))
    long = []
    for line in text.splitlines():
        if line.startswith(("|", "%", "![")):
            continue
        for s in re.split(r"(?<=[.!?])\s+", line.replace("**", "")):
            if len(s.split()) > 30:
                long.append(s[:70])
    return problems, long


def build(root, src, stem, limit, has_cover, nums):
    text = io.open(os.path.join(root, src), encoding="utf-8").read()
    text = re.sub(r"\{\{(\w+)\}\}", lambda m: nums.get(m.group(1), m.group(0)), text)
    problems, long = lint(text)
    for s in long:
        print("  [WARN] %s: sentence over 30 words: %s..." % (src, s))
    if problems:
        return False, "%s refused: %s" % (src, "; ".join(problems))
    lines = text.splitlines()
    meta = [l[2:].strip() for l in lines if l.startswith("% ")]
    body = [l for l in lines if not l.startswith("% ")]
    doc = Document()
    setup(doc, not has_cover)
    (cover if has_cover else title_block)(doc, meta)
    fig_n, i = 0, 0
    while i < len(body):
        line = body[i]
        if not line.strip():
            i += 1
            continue
        if line.strip() == "\\pagebreak":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        elif line.strip() in ("\\landscape", "\\portrait"):
            wide = line.strip() == "\\landscape"
            sec = doc.add_section(WD_SECTION.NEW_PAGE)
            sec.orientation = WD_ORIENT.LANDSCAPE if wide else WD_ORIENT.PORTRAIT
            sec.page_width, sec.page_height = (Inches(11), Inches(8.5)) if wide else (Inches(8.5), Inches(11))
            sec.top_margin = sec.bottom_margin = Inches(0.7 if wide else 0.9)
        elif line.startswith("## "):
            heading(doc, line[3:], 2, not has_cover)
        elif line.startswith("# "):
            heading(doc, line[2:], 1, not has_cover)
        elif line.startswith("!["):
            m = re.match(r"!\[(.*)\]\((.*)\)", line)
            fig_n += 1
            figure(doc, root, m.group(1), m.group(2), fig_n)
        elif line.startswith("> "):
            callout(doc, line[2:])
        elif line.startswith("|"):
            rows = []
            while i < len(body) and body[i].startswith("|"):
                cells = body[i].strip().strip("|").split("|")
                if not all(re.fullmatch(r"\s*:?-+:?\s*", c) for c in cells):
                    rows.append(cells)
                i += 1
            table(doc, rows, not has_cover)
            continue
        elif re.match(r"(\* |\d+\. )", line):
            p = doc.add_paragraph(style="List Bullet" if line.startswith("* ") else "List Number")
            p.paragraph_format.space_after = Pt(0 if not has_cover else 3)
            runs(p, re.sub(r"^(\* |\d+\. )", "", line))
        else:
            runs(doc.add_paragraph(), line)
        i += 1
    docx = os.path.join(root, stem + ".docx")
    pdf = os.path.join(root, stem + ".pdf")
    doc.save(docx)
    r = subprocess.run([sys.executable, os.path.join(root, "scripts", "to_pdf.py"), docx, pdf],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return False, "%s: PDF conversion failed: %s" % (src, r.stdout.strip())
    reader = PdfReader(pdf)
    txt = " ".join(pg.extract_text() or "" for pg in reader.pages)
    key = meta[0].split(":")[0]
    ok = key in txt and "{{" not in txt and len(reader.pages) <= limit
    return ok, "%s -> %s pages %d (limit %d) . text layer %d chars . title found %s" % (
        src, os.path.basename(pdf), len(reader.pages), limit, len(txt), key in txt)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = argv[1]
    nums = json.load(io.open(os.path.join(root, "docs", "numbers.json"), encoding="utf-8"))
    probs, _ = lint("{{no_such_key}} a — b")
    ok = len(probs) == 2
    print("[CONTROL] lint refuses a planted unfilled key and em dash: %s" % ok)
    only = argv[2:]
    for src, out in MD_DOCS:
        if only and not any(o in src for o in only):
            continue
        text = io.open(os.path.join(root, src), encoding="utf-8").read()
        text = re.sub(r"\{\{(\w+)\}\}", lambda m: nums.get(m.group(1), m.group(0)), text)
        problems, long = lint(text)
        for s in long:
            print("  [WARN] %s: sentence over 30 words: %s..." % (src, s))
        good = not problems
        if good:
            io.open(os.path.join(root, out), "w", encoding="utf-8", newline="\n").write(text)
        print(("  ok  %s -> %s" % (src, out)) if good else ("  REFUSED %s: %s" % (src, "; ".join(problems))))
        ok = ok and good
    for src, stem, limit, has_cover in DOCS:
        if only and not any(o in src for o in only):
            continue
        good, msg = build(root, src, stem, limit, has_cover, nums)
        print(("  ok  " if good else "  REFUSED ") + msg)
        ok = ok and good
    print("[RESULT] %s" % ("ok" if ok else "REFUSED"))
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
