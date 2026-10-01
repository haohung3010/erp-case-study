#!/usr/bin/env python
"""to_pdf.py -- convert a .docx to PDF with ONLYOFFICE, keeping the text layer.

CONFIG
    ONLYOFFICE converter   %ProgramFiles%/ONLYOFFICE/DesktopEditors/converter/x2t.exe
    font index             %LOCALAPPDATA%/ONLYOFFICE/DesktopEditors/data/fonts/AllFonts.js (built when ONLYOFFICE first opens)
    PDF format code        513

WORKFLOW
    python to_pdf.py <file.docx> <file.pdf>
    1. find x2t and the font index; refuse if either is missing
    2. write a task file: input, output, format 513, font index, a temp folder
    3. run x2t on the task file and confirm a non-empty PDF exists

Q&A
    Q: why a task file?   A: x2t called with only an input and an output exits without writing anything.

PITFALLS
    - A font neither ONLYOFFICE nor the machine has is substituted; the page count can change. Look at every page.
    - The font index exists only after ONLYOFFICE has been opened once on this machine.

NOTES
    Exit: 0 written . 2 usage . 3 cannot convert (converter or font index missing, or x2t failed).
"""
import os
import subprocess
import sys
import tempfile
from xml.sax.saxutils import escape


def onlyoffice():
    base = os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "ONLYOFFICE", "DesktopEditors")
    x2t = os.path.join(base, "converter", "x2t.exe")
    fonts = os.path.join(os.environ.get("LOCALAPPDATA", ""), "ONLYOFFICE", "DesktopEditors", "data", "fonts")
    if os.path.exists(x2t) and os.path.exists(os.path.join(fonts, "AllFonts.js")):
        return x2t, fonts
    return None


def convert(src, pdf):
    found = onlyoffice()
    if not found:
        return False, "ONLYOFFICE converter or its font index not found; open ONLYOFFICE once to build the index"
    x2t, fonts = found
    tmp = tempfile.mkdtemp(prefix="x2t_")
    task = os.path.join(tmp, "task.xml")
    nl = chr(10)
    xml = nl.join([
        '<?xml version="1.0" encoding="utf-8"?>',
        "<TaskQueueDataConvert>",
        "  <m_sFileFrom>%s</m_sFileFrom>" % escape(src),
        "  <m_sFileTo>%s</m_sFileTo>" % escape(pdf),
        "  <m_nFormatTo>513</m_nFormatTo>",
        "  <m_sAllFontsPath>%s</m_sAllFontsPath>" % escape(os.path.join(fonts, "AllFonts.js")),
        "  <m_sFontDir>%s</m_sFontDir>" % escape(fonts),
        "  <m_sTempDir>%s</m_sTempDir>" % escape(tmp),
        "  <m_bIsNoBase64>true</m_bIsNoBase64>",
        "</TaskQueueDataConvert>", ""])
    with open(task, "w", encoding="utf-8") as fh:
        fh.write(xml)
    r = subprocess.run([x2t, task], cwd=os.path.dirname(x2t), capture_output=True, text=True)
    ok = r.returncode == 0 and os.path.exists(pdf) and os.path.getsize(pdf) > 0
    return ok, "x2t rc=%s %s %s" % (r.returncode, r.stdout.strip(), r.stderr.strip())


def main(argv):
    if len(argv) != 2 or not argv[0].lower().endswith(".docx") or not argv[1].lower().endswith(".pdf"):
        print("usage: to_pdf.py <file.docx> <file.pdf>")
        return 2
    src, pdf = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    if not os.path.exists(src):
        print("[CANNOT CONVERT] no such file: %s" % src)
        return 3
    ok, log = convert(src, pdf)
    if not ok:
        print("[CANNOT CONVERT] " + log)
        return 3
    print("wrote %s (%s bytes)" % (pdf, format(os.path.getsize(pdf), ",")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
