# -*- coding: utf-8 -*-
"""build_raci.py -- the RACI for order to cash, procure to pay and accounting across the ten departments, with the role boundary checked.

PURPOSE
  Shows who is Responsible, Accountable, Consulted and Informed for every step of order to cash, procure to pay and
  accounting, and for the work
  of building and rolling out the system. It makes the product owner's boundary visible: the product owner owns the
  system, the requirements and the rollout, and holds no R or A on a purchasing or payment decision.

CONFIG
  argv[1]  the repository root. Needs openpyxl. Style: the portfolio's workbook design (Calibri, header #1D5C6B).

WORKFLOW
  1 the matrix is declared below as rows of (id, activity, kind, {column: letter}, note)
  2 write raci/raci.xlsx: Read me, RACI (one row per activity), Role boundary (the product owner's rows), Change log
  3 [CONTROL] every row has exactly one A, except rows marked per-department, where each department is A for its own;
    the product owner has no R or A on any row of kind "Business decision"; both checks are shown able to fire on a
    planted bad row before the real matrix is judged
  rc 0 ok . 2 usage . 3 a check failed

Q&A
  Q: where is the executive sponsor?   A: in the Director's office column; the note says so where it matters.

PITFALLS
  A RACI that gives the product owner an A on a business decision reads as competent and is wrong for this role; the
  boundary check exists so that cannot slip in during an edit.

NOTES
  Tanmark Industries is fictional.
"""
import os
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo

HEADER, HEADER_TEXT, BAND = "1D5C6B", "FFFFFF", "F1F5F6"
DEPTS = ["Director's office", "Product sales", "Technical management", "Production",
         "Warehouse", "Logistics and purchasing", "Price control", "Service sales", "Accounting",
         "Human resources"]
PO, DEV = "Product owner", "Development team"
COLS = DEPTS + [PO, DEV]
EX, SA, EN, PR, WH, PC, PX, SS, FI, HR = DEPTS
ALL = {d: "R/A" for d in DEPTS}  # per-department rows: each department for its own

OP, BIZ, SYS = "Operation", "Business decision", "System and rollout"
ROWS = [
    ("P1", "Save and confirm an order", OP, {SA: "R/A", PC: "I"}, "Two-stage save (D5)"),
    ("P2", "Send an order to logistics", OP, {SA: "R/A", PC: "I"}, "Sales editing locks here (D7)"),
    ("P3", "Decide how to fulfil: from stock or by production", OP, {PC: "R/A", PR: "C", WH: "C"}, ""),
    ("P4", "Raise a material request", OP, {PC: "R", PR: "A", WH: "C"}, "The factory manager answers for the request"),
    ("P5", "Decide what to buy and from whom", BIZ, {PC: "R/A", EN: "C", PR: "C", PX: "C", FI: "I"}, "A buyer's decision, never the product owner's; price control checks the price"),
    ("P6", "Sign a purchase order (on paper)", BIZ, {PC: "R/A", EX: "C", FI: "I"}, "The logistics manager signs; approval stays outside the system (D9)"),
    ("P7", "Receive goods into stock", OP, {WH: "R/A", PC: "I", FI: "I"}, "Receiving counts as approval of the purchase order (D9)"),
    ("P8", "Issue materials to the workshop", OP, {WH: "R/A", PR: "I"}, "No cancel after the first issue (R3)"),
    ("P9", "Build and test tanks, drums and containers", OP, {PR: "R/A", EN: "C"}, "Three workshops in Production"),
    ("P10", "Inspect finished goods", OP, {EN: "R/A", PR: "I"}, "Quality sits in technical management"),
    ("P11", "Plan, dispatch and deliver trips", OP, {PC: "R/A", WH: "R", SA: "I", SS: "I"}, "Ship exactly the plan (R5)"),
    ("P12", "Close an order as cancelled or not completed", BIZ, {SA: "R/A", PC: "C", FI: "I"}, "The closure rule is the sales and logistics leads' (D6)"),
    ("P13", "Raise each trip's invoice before dispatch", OP, {FI: "R/A", PC: "I"}, "One invoice per trip (D16, R9)"),
    ("P14", "Post receipt and payment vouchers", OP, {FI: "R/A"}, "Saving and posting are separate (D10)"),
    ("P15", "Reverse a posted voucher", BIZ, {FI: "R/A", EX: "I"}, "The chief accountant decides (D10)"),
    ("P16", "Set posting and correction policy", BIZ, {FI: "R/A", PO: "C"}, "An accounting policy; the product owner builds it"),
    ("P17", "Rule which sales status combinations are legal", BIZ, {FI: "R/A", SA: "C", PO: "C"}, "D8"),
    ("P18", "Pay suppliers", BIZ, {FI: "R/A", PC: "I"}, "Accounting's function, never the product owner's"),
    ("P19", "Set payment terms and credit limits per contract", BIZ, {FI: "R/A", SA: "C", EX: "I"},
     "30 days unless the contract says otherwise (D17)"),
    ("P20", "Release an order on credit hold", BIZ, {FI: "R/A", SA: "I"}, "The chief accountant, with a reason (D17, R10)"),
    ("P21", "Allocate receipts and chase overdue invoices", OP, {FI: "R/A", SA: "C"}, "Oldest due date first (D17)"),
    ("P22", "Reconcile receivables with each customer", OP, {FI: "R/A", SA: "C"}, "Quarterly, on a statement the customer signs"),
    ("P23", "Reconcile stock with accounting", OP, {FI: "A", WH: "R"}, "Monthly"),
    ("P24", "Review stock forms as drafts before stock moves", BIZ, {WH: "R/A", PO: "C"},
     "A warehouse control; the product owner built it and kept the form number tied to the movement (D15)"),
    ("P25", "Load supplier price lists one week before they take effect", OP, {PX: "R/A", PC: "I", FI: "I"},
     "The dependency that slipped in month 10 (DP-7, W13)"),
    ("S1", "Discover needs and write requirements", SYS, {PO: "R/A", **{d: "C" for d in DEPTS}, DEV: "I"}, "Discovery with every department head"),
    ("S2", "Order the backlog and set each sprint's priorities", SYS, {PO: "R/A", EX: "C", DEV: "C"},
     "The product owner owns the backlog; the director reviews the roadmap weekly"),
    ("S3", "Model states and write Gherkin before the build", SYS, {PO: "R/A", DEV: "C", SA: "C", PC: "C", FI: "C"}, "D11; every error path is a refused move"),
    ("S4", "Build and test the system", SYS, {DEV: "R", PO: "A"}, "A team of six developers: tech lead, four engineers, security"),
    ("S5", "Sign off UAT for the sales stories", SYS, {SA: "A", PO: "R"}, "Order lifecycle and closure"),
    ("S6", "Sign off UAT for delivery and purchasing", SYS, {PC: "A", PO: "R", WH: "C"}, ""),
    ("S7", "Sign off UAT for posting and invoicing", SYS, {FI: "A", PO: "R"}, ""),
    ("S8", "Map access to roles", SYS, {PO: "A", DEV: "R", **{d: "C" for d in DEPTS}}, "Roles agreed with each department head (D4)"),
    ("S9", "Keep the transition table: who may move each document", SYS, {PO: "R/A", DEV: "C", FI: "C", SA: "C"}, "Separate from data access (D4, R7)"),
    ("S10", "Migrate open records, each in its real state", SYS, {PO: "A", DEV: "R", WH: "C", PC: "C", FI: "C", SA: "C"}, "D3"),
    ("S11", "Keep the decided-versus-built register", SYS, {PO: "R/A", DEV: "C"}, "D13"),
    ("S12", "Train each role before its department joins", SYS, {PO: "R/A", **{d: "C" for d in DEPTS}}, "A superuser in each department"),
    ("S13", "Decide go or no-go for each phase", SYS, {PO: "R", EX: "A", DEV: "C"}, "The product owner recommends; the executive sponsor decides"),
    ("S14", "Retire paper after the parallel run", SYS, {PO: "A", **{d: "R" for d in DEPTS}}, "Each department head, after two clean weeks (D12)"),
    ("S15", "Sign off UAT for material requests", SYS, {PR: "A", PO: "R"}, "The factory manager signs"),
]
PER_DEPT = set()


def check(rows):
    """Return a list of problems: the one-A rule and the product owner's boundary."""
    problems = []
    for rid, act, kind, cells, _ in rows:
        a = [c for c, v in cells.items() if "A" in v]
        if rid in PER_DEPT:
            if sorted(a) != sorted(DEPTS):
                problems.append("%s per-department row without an A in every department" % rid)
        elif len(a) != 1:
            problems.append("%s has %d A" % (rid, len(a)))
        if kind == BIZ and any(x in cells.get(PO, "") for x in "RA"):
            problems.append("%s gives the product owner %s on a business decision" % (rid, cells[PO]))
        if not any("R" in v for v in cells.values()):
            problems.append("%s has no R" % rid)
    return problems


def style(ws, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(name="Calibri", size=10, bold=True, color=HEADER_TEXT)
        cell.fill = PatternFill("solid", fgColor=HEADER)
        cell.alignment = Alignment(vertical="top", wrap_text=True)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)


def build(root):
    wb = Workbook()
    rm = wb.active
    rm.title = "Read me"
    rm.append(["Item", "Detail"])
    for k, v in [
        ("Purpose", "Who is Responsible, Accountable, Consulted and Informed for order to cash, procure to pay and accounting at Tanmark "
                    "Industries, and for building and rolling out the system. Tanmark Industries is fictional."),
        ("Version", "v1, 2026-09-29"),
        ("Owner", "Product owner (role)"),
        ("Letters", "R does the work. A answers for it; one A per row. C is asked before. I is told after. "
                    "R/A means the same party does and answers."),
        ("Kinds", "Operation: a step of the process. Business decision: a decision that belongs to the business, never "
                  "to the product owner. System and rollout: the product owner's work."),
        ("Executive sponsor", "The director, in the Director's office column."),
        ("Where it comes from", "Built by raci/build_raci.py, which also checks the one-A rule and the product owner's "
                                "boundary. Change the script, then rebuild."),
    ]:
        rm.append([k, v])
    style(rm, 2)
    rm.column_dimensions["A"].width = 20
    rm.column_dimensions["B"].width = 100

    ws = wb.create_sheet("RACI")
    head = ["ID", "Activity", "Kind"] + COLS + ["Note"]
    ws.append(head)
    for rid, act, kind, cells, note in ROWS:
        ws.append([rid, act, kind] + [cells.get(c, "") for c in COLS] + [note])
    style(ws, len(head))
    last = len(ROWS) + 1
    for i, w in enumerate([6, 34, 16] + [7] * len(COLS) + [78]):
        ws.column_dimensions[ws.cell(row=1, column=i + 1).column_letter].width = w
    for c in range(4, 4 + len(COLS)):
        ws.cell(row=1, column=c).alignment = Alignment(text_rotation=90, vertical="bottom", horizontal="center")
        for r in range(2, last + 1):
            ws.cell(row=r, column=c).alignment = Alignment(horizontal="center", vertical="top")
    ws.row_dimensions[1].height = 190
    span = "D2:%s%d" % (ws.cell(row=1, column=3 + len(COLS)).column_letter, last)
    for val, fill, bold in (("R/A", "1D5C6B", True), ("A", "1D5C6B", True), ("R", "DCEBEE", False)):
        ws.conditional_formatting.add(span, CellIsRule(operator="equal", formula=['"%s"' % val],
                                      fill=PatternFill("solid", fgColor=fill),
                                      font=Font(color="FFFFFF" if fill == "1D5C6B" else "16232B", bold=bold)))
    ws.add_table(Table(displayName="RACI", ref="A1:%s%d" % (ws.cell(row=1, column=len(head)).column_letter, last),
                       tableStyleInfo=TableStyleInfo(name="TableStyleLight1", showRowStripes=True)))
    ws.freeze_panes = "D2"

    rb = wb.create_sheet("Role boundary")
    rb.append(["ID", "Activity", "Kind", "Product owner", "Who holds A"])
    for rid, act, kind, cells, note in ROWS:
        holders = ", ".join(c for c, v in cells.items() if "A" in v)
        if rid in PER_DEPT:
            holders = "each department, for its own"
        rb.append([rid, act, kind, cells.get(PO, "") or "none", holders])
    style(rb, 5)
    for col, w in zip("ABCDE", (6, 36, 18, 14, 40)):
        rb.column_dimensions[col].width = w
    rb.freeze_panes = "A2"

    cl = wb.create_sheet("Change log")
    cl.append(["Date", "Change", "By (role)"])
    cl.append(["2026-09-29", "First version: 13 process rows, 12 system and rollout rows", "Product owner"])
    cl.append(["2026-09-30", "Rebuilt for order to cash, procure to pay and accounting: 18 process rows, 14 system rows", "Product owner"])
    style(cl, 3)
    cl.column_dimensions["B"].width = 60
    out = os.path.join(root, "raci", "raci.xlsx")
    wb.save(out)
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    planted = [("X1", "planted", BIZ, {FI: "A", EX: "A", PO: "R"}, "")]
    caught = check(planted)
    print("[CONTROL] planted row (two A, product owner R on a business decision) -> %d problem(s): %s"
          % (len(caught), caught))
    ok = len(caught) == 2
    problems = check(ROWS)
    print("rows %d . business decisions %d . product owner holds R or A on %d business decision(s)" % (
        len(ROWS), sum(r[2] == BIZ for r in ROWS),
        sum(r[2] == BIZ and any(x in r[3].get(PO, "") for x in "RA") for r in ROWS)))
    for p in problems:
        print("  PROBLEM " + p)
    ok = ok and not problems
    out = build(argv[1])
    back = load_workbook(out)["RACI"]
    ok = ok and back.max_row - 1 == len(ROWS)
    print("written %d rows -> %s" % (back.max_row - 1, out))
    print("[RESULT] %s" % ("ok" if ok else "REFUSED"))
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
