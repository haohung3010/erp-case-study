# -*- coding: utf-8 -*-
"""build_srs.py -- write srs/srs.md, the software requirements specification, from the sources it summarises.

PURPOSE
  The requirements of this case study live in several places: the state model and its transition table, the business
  rules (W6), the non-functional requirements (W5), the interface (W7), the scope (W1) and the roadmap (W13). An SRS
  that restates them by hand drifts from them on the first edit. This builds the SRS from those sources, in the
  structure of the SRS template at github.com/jam01/SRS-Template (CC0),
  so the SRS is the one place a reader can see every requirement with its ID, statement, rationale, acceptance
  criteria and verification method.

CONFIG
  argv[1]  the repository root
  Reads   state/transitions.csv . state/state-model.md (R1-R10) . working-papers/W05 (N1-N13), W06 (B1-B11), W01, W13
          stories/*.feature through uat/build_uat.py's parser (UAT IDs and refusal messages)
  Writes  srs/srs.md
  Exit    0 written . 1 a control or a check failed . 2 usage

WORKFLOW
  1 read the sources
  2 one functional requirement per row of the transition table: an allowed move is a "shall allow", a refused move a
    "shall refuse"; its acceptance criteria are the UAT scenarios that exercise that move, matched on document, state
    and event
  3 quality, compliance and design requirements from W5 and W6, each keeping its source ID
  4 the verification matrix lists every requirement, its method and its UAT rows; a requirement no UAT row exercises
    is listed as such, not hidden
  5 [CONTROL] a planted transition must be reported as untested, and a real tested one must not

Q&A
  Q: why one requirement per transition?   A: the transition table is what the business signed (E8); each row is
     already one testable statement about one document, one state and one actor.
  Q: why keep the old IDs (R, B, N, D)?   A: every other paper cites them; the SRS adds REQ IDs and cross-references
     them, so nothing that cites R9 breaks.

NOTES
  Tanmark Industries is fictional. Generated; do not edit srs/srs.md by hand.
"""
import csv
import io
import os
import re
import sys

AREA = {"N1": "OBS", "N2": "SEC", "N3": "SEC", "N4": "COMP", "N5": "SEC", "N6": "SEC", "N7": "AVAIL", "N8": "PERF",
        "N9": "INT", "N10": "COMP", "N11": "CM", "N12": "INST", "N13": "AVAIL"}
DOC_NAME = {"sales-order": "sales order", "delivery-trip": "delivery trip", "material-request": "material request",
            "purchase-order": "purchase order", "sales-invoice": "sales invoice", "sale-statuses": "sale",
            "voucher": "accounting voucher"}
RELEASE = {"sales-order": "R1 (pilot, week 1)", "delivery-trip": "R1 (pilot, week 1)",
           "purchase-order": "R1 (pilot, week 1)", "material-request": "R1; draft forms R2 (week 8)",
           "voucher": "R2 (week 8)", "sales-invoice": "R1 per trip; receivables R3 (week 9)",
           "sale-statuses": "R3 (week 9)"}


def read(root, *p):
    return io.open(os.path.join(root, *p), encoding="utf-8").read()


def table(text, prefix):
    """Rows of a markdown table whose first cell starts with prefix (e.g. 'N', 'B', 'R')."""
    out = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("| ") and re.fullmatch(prefix + r"\d+", cells[0]):
            out.append(cells)
    return out


def ensure(x, who="The system"):
    """A W5 statement as a 'shall ensure that' clause, with its rationale."""
    text = x[2].rstrip(".")
    stmt = "%s shall ensure that %s." % (who, text[0].lower() + text[1:])
    m = re.search(r"\((R\d+|D\d+)\)", x[2])
    if m and m.group(1).startswith("R"):
        why = ("Restates %s as a quality of the whole system: no route, including imports, interfaces and administrator "
               "screens, may break it (W5)." % m.group(1))
    elif m:
        why = "Follows decision %s in the decision log (W5, %s)." % (m.group(1), x[0])
    else:
        why = "Target agreed with the owning department (W5, %s)." % x[0]
    return stmt, why

def key(document, frm, event):
    return (document, frm.strip().lower(), event.strip().lower())


def uat_index(rows):
    idx = {}
    for r in rows:
        if r["refused"]:
            d, frm, ev = r["refused"]
            idx.setdefault(key(d, frm, ev), []).append(r)
            continue
        m = re.match(r"(.+?): (.+?), to (.+)$", r["transition"])
        if m:
            idx.setdefault(key(r["document"], m.group(1), m.group(2)), []).append(r)
    return idx


def functional(transitions, idx):
    reqs, n = [], 0
    for t in transitions:
        n += 1
        doc = DOC_NAME.get(t["document"], t["document"])
        rid = "REQ-FUNC-%03d" % n
        tests = idx.get(key(t["document"], t["from"], t["event"]), [])
        if t["kind"] == "allowed":
            who = t["roles"] or "the permitted role"
            stmt = 'The system shall allow the %s to "%s" a %s in state %s, moving it to %s' % (
                who[0].lower() + who[1:], t["event"], doc, t["from"], t["to"])
            stmt += (" (condition: %s)." % t["condition"]) if t["condition"] else "."
            if t["system_action"]:
                stmt += " On that move the system shall record: %s." % t["system_action"]
            rationale = "Agreed line by line in the transition workshop (E8)" + (", rule %s" % t["rule"] if t["rule"] else "") + "."
        else:
            stmt = 'The system shall refuse "%s" on a %s in state %s, and tell the user: "%s"' % (
                t["event"], doc, t["from"], t["condition"])
            rationale = "Enforces rule %s of the state model." % (t["rule"] or "(none named)")
        acc = ["%s: %s" % (r["id"], r["scenario"]) for r in tests]
        reqs.append({"id": rid, "doc": t["document"], "title": "%s: %s, %s" % (doc, t["from"], t["event"]),
                     "statement": stmt, "rationale": rationale, "rule": t["rule"],
                     "acceptance": acc, "method": "Test" if tests else "Inspection",
                     "tests": [r["id"] for r in tests], "story": sorted({r["story"] for r in tests})})
    return reqs


def control(transitions, rows):
    idx = uat_index(rows)
    planted = [{"document": "sales-order", "from": "Nowhere", "event": "teleport", "to": "Open", "roles": "x",
                "condition": "", "system_action": "", "kind": "allowed", "rule": ""}]
    real = [t for t in transitions if idx.get(key(t["document"], t["from"], t["event"]))][:1]
    p = functional(planted, idx)[0]
    q = functional(real, idx)[0] if real else None
    return (p["method"] == "Inspection" and not p["tests"]) and bool(q and q["tests"])


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = argv[1]
    sys.path.insert(0, os.path.join(root, "uat"))
    from build_uat import parse
    rows = parse(root)[0]
    transitions = list(csv.DictReader(io.open(os.path.join(root, "state", "transitions.csv"), encoding="utf-8")))
    ok = control(transitions, rows)
    print("[CONTROL] planted transition reported untested, real one tested: %s" % ok)
    if not ok:
        return 1
    idx = uat_index(rows)
    by_name = {r["scenario"]: r["id"] for r in rows}

    def uat(name):
        if name not in by_name:
            raise SystemExit("REFUSED: no UAT scenario named %r" % name)
        return by_name[name]

    func = functional(transitions, idx)
    rules = table(read(root, "state", "state-model.md"), "R")
    nfr = table(read(root, "working-papers", "W05-non-functional-requirements.md"), "N")
    brules = table(read(root, "working-papers", "W06-business-rules.md"), "B")
    used = {r["id"] for r in rows}
    tested = {u for f in func for u in f["tests"]}
    print("functional requirements %d . with a UAT test %d . UAT rows %d . UAT rows matched to a requirement %d"
          % (len(func), sum(1 for f in func if f["tests"]), len(rows), len(tested)))

    md = []
    w = md.append
    w("# Software Requirements Specification")
    w("## For the Tanmark Industries back-office system")
    w("")
    w("Version 1.0  ")
    w("Prepared by the product owner  ")
    w("Tanmark Industries (fictional)  ")
    w("")
    w("**Generated by `srs/build_srs.py` from the state model and the working papers; do not edit by hand.** Structure "
      "follows the SRS template at [github.com/jam01/SRS-Template](https://github.com/jam01/SRS-Template) (CC0).")
    w("")
    w("## Revision History")
    w("")
    w("| Name | Date | Reason For Changes | Version |")
    w("|------|------|--------------------|---------|")
    w("| Product owner | week 13 | First issue: the requirements of the state model and the working papers gathered into one SRS, each with an ID | 1.0 |")
    w("")
    w("## 1. Introduction")
    w("")
    w("### 1.1 Document Purpose")
    w("This SRS states what the back-office system must do, not how it is built. The sales and logistics leads, the "
      "chief accountant and the warehouse lead use it to confirm the rules they agreed; the developers build from it; "
      "the UAT testers verify against it. It gathers requirements already agreed in the state model and the working "
      "papers, adds an ID to each, and links each to its test.")
    w("")
    w("### 1.2 Product Scope")
    w("The system moves Tanmark's order to cash, procure to pay and accounting from paper, email and spreadsheets onto "
      "one system, so every order, purchase and voucher has a visible state and a traceable history (charter, W1).")
    w("")
    w("| In scope | Out of scope |")
    w("|---|---|")
    scope = read(root, "working-papers", "W01-charter-and-scope.md")
    sec = scope.split("| In scope | Out of scope |", 1)[1].split("\n\n", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| ") and not line.startswith("|---"):
            w(line)
    w("")
    w("### 1.3 Definitions, Acronyms, and Abbreviations")
    w("")
    w("| Term | Definition |")
    w("|------|------------|")
    for term, d in [
            ("Credit hold", "A contract over its credit limit or with an invoice past due; it gets no new order unless the chief accountant releases it (R10)"),
            ("Draft form", "A stock form before the stock moves; it has no official number (R8)"),
            ("Not completed", "The closure of an order that had started production; received stock is kept (R3)"),
            ("Post", "To make a voucher final; a posted voucher never changes (R2)"),
            ("Refused move", "A move the transition table forbids; the system blocks it and says why"),
            ("Reversing voucher", "The only correction to a posted voucher (B6)"),
            ("State", "A named stage in a document's lifecycle, such as Open or Posted"),
            ("Transition table", "`state/transitions.csv`: every allowed and refused move, with who may make it"),
            ("Trip", "One delivery run; it carries one invoice (R9)"),
            ("UAT", "User acceptance testing; the script is `uat/uat-script.xlsx`")]:
        w("| %s | %s |" % (term, d))
    w("")
    w("### 1.4 References")
    w("")
    w("| Reference | Location | Normative or informative |")
    w("|---|---|---|")
    for ref, loc, kind in [
            ("State model and its ten rules", "state/state-model.md", "normative"),
            ("Transition table", "state/transitions.csv", "normative"),
            ("Business rules and decision table", "working-papers/W06-business-rules.md", "normative"),
            ("Non-functional requirements", "working-papers/W05-non-functional-requirements.md", "normative"),
            ("Interface: sales to accounting", "working-papers/W07-interface-sales-to-accounting.md", "normative"),
            ("Data model and dictionary", "working-papers/W04-data-model.md", "informative"),
            ("Decision log, D1 to D17", "decisions/decision-log.md", "informative"),
            ("User stories, Gherkin", "stories/", "normative (acceptance criteria)"),
            ("UAT script and sign-off", "uat/uat-script.xlsx", "informative (evidence)"),
            ("Release roadmap", "working-papers/W13-release-roadmap.md", "informative")]:
        w("| %s | `%s` | %s |" % (ref, loc, kind))
    w("")
    w("### 1.5 Document Overview")
    w("Section 2 gives the context: the product, its users, its constraints and which release carries what. Section 3 "
      "lists every requirement with an ID of the form REQ-AREA-NNN, a statement using \"shall\", its rationale, its "
      "acceptance criteria and its verification method. Section 4 is the verification matrix. A requirement's source ID "
      "(R, B, N or D) is kept beside its REQ ID.")
    w("")
    w("## 2. Product Overview")
    w("")
    w("### 2.1 Product Perspective")
    w("A new system replacing paper forms, email and spreadsheets. It has two applications: sales and logistics, and "
      "accounting. They exchange the data listed in W7, and only accounting writes payment status and credit hold. "
      "The product owner owns the transition table; each department lead owns the rules for their documents (RACI).")
    w("")
    w("### 2.2 Product Functions")
    for d, txt in [("sales-order", "take an order from request to completion, with a lock once logistics has it"),
                   ("material-request", "request and issue materials to the workshop"),
                   ("purchase-order", "raise purchase orders and record receipts"),
                   ("delivery-trip", "plan, issue and dispatch delivery trips, each with its invoice"),
                   ("sales-invoice", "raise one invoice per trip, with terms and a due date, and track receivables"),
                   ("sale-statuses", "track a sale as invoiced, delivered and paid, independently"),
                   ("voucher", "save, post and reverse receipt and payment vouchers")]:
        w("* **%s**: %s." % (DOC_NAME[d].capitalize(), txt))
    w("")
    w("### 2.3 Product Constraints")
    w("These rules bind every requirement in section 3. Each is enforced by refused moves, not by user discipline.")
    w("")
    for r in rules:
        w("* **%s.** %s" % (r[0], r[1]))
    w("* **D9.** Purchase-order approval must stay a paper signature; the system must not add an approval step.")
    w("")
    w("### 2.4 User Characteristics")
    roles = sorted({x.strip() for t in transitions for x in re.split(r"[,;]", t["roles"])
                    if x.strip() and x.strip() != "System"})
    w("Roles that move documents (from the transition table): " + ", ".join(roles) + ". Most users are on the "
      "warehouse floor or the factory, some on night shifts; each department has a superuser for the first two weeks "
      "(N12). Access to data and the right to move a document are granted separately (R7).")
    w("")
    w("### 2.5 Assumptions and Dependencies")
    raid = read(root, "working-papers", "W10-raid-log.md")
    w("")
    w("| ID | Assumption | If false |")
    w("|---|---|---|")
    for line in raid.splitlines():
        if line.startswith("| A-"):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            w("| %s | %s | %s |" % (c[0], c[1], c[2] if len(c) > 2 else ""))
    w("")
    w("### 2.6 Apportioning of Requirements")
    w("")
    w("| Requirements | Release (W13) |")
    w("|---|---|")
    for d in DOC_NAME:
        ids = [f["id"] for f in func if f["doc"] == d]
        if ids:
            w("| %s to %s (%s) | %s |" % (ids[0], ids[-1], DOC_NAME[d], RELEASE[d]))
    w("| Quality, compliance and rollout requirements (3.1, 3.3 to 3.5) | from R1; each checked before its phase |")
    w("")
    w("## 3. Requirements")
    w("")
    w("Each requirement: **ID**, **Statement**, **Rationale**, **Acceptance Criteria**, **Verification Method**. "
      "Functional requirements are one per row of the transition table; acceptance criteria are the UAT scenarios "
      "that exercise that move.")
    w("")
    w("### 3.1 External Interfaces")
    w("")
    w("#### 3.1.1 User Interfaces")
    n9 = [x for x in nfr if x[0] == "N9"][0]
    w("- ID: REQ-INT-001 (from N9)")
    w("- Statement: The system shall show, on every refused move and locked document, why it is refused and what to do instead.")
    w("- Rationale: %s" % "A pilot user could not see the lock after handoff (E9, DB-2).")
    w("- Acceptance Criteria: %s" % n9[3])
    w("- Verification Method: Test")
    w("")
    w("#### 3.1.2 Hardware Interfaces")
    w("None specified. Users work on the warehouse network (see REQ-PERF-001).")
    w("")
    w("#### 3.1.3 Software Interfaces")
    w("The sales-to-accounting boundary is specified in W7, item by item: what crosses, who sends it, and when.")
    w("")
    for i, (stmt, why, acc) in enumerate([
            ("The sales application shall send the order total after discount, and accounting shall never re-apply a discount.",
             "A discount applied on both sides leaves every screen right and the ledger wrong (W7 rule 1).",
             "an order with a discount reaches accounting with the same net total and tax as the sales screen"),
            ("Accounting shall not write an order's lifecycle state, except the chief accountant's release of an order on credit hold, which is logged with a reason.",
             "One owner per state (W7 rule 2, R10, D17).",
             "%s; an interface call from accounting that sets any other order state is refused" % uat("The chief accountant releases one order, with a reason")),
            ("The accounting application shall return the invoice number and due date before the trip may be dispatched.",
             "Goods leave only with their invoice (R9).",
             "%s: a trip without its raised invoice cannot be dispatched" % uat("A trip cannot leave without its invoice"))], 2):
        w("- ID: REQ-INT-%03d" % i)
        w("- Statement: %s" % stmt)
        w("- Rationale: %s" % why)
        w("- Acceptance Criteria: %s" % acc)
        w("- Verification Method: Test (interface test) and Inspection of W7")
        w("")
    w("### 3.2 Functional")
    w("")
    cur = None
    for f in func:
        if f["doc"] != cur:
            cur = f["doc"]
            w("#### %s" % DOC_NAME[cur].capitalize())
            w("")
        w("- ID: %s" % f["id"])
        w("- Title: %s" % f["title"])
        w("- Statement: %s" % f["statement"])
        w("- Rationale: %s" % f["rationale"])
        w("- Acceptance Criteria: %s" % ("; ".join(f["acceptance"]) if f["acceptance"]
                                         else "no UAT scenario exercises this move; verified by inspection of the configured transition table"))
        w("- Verification Method: %s" % f["method"])
        w("")
    w("### 3.3 Quality of Service")
    w("")
    groups = [("3.3.1 Performance", "PERF"), ("3.3.2 Security", "SEC"), ("3.3.3 Reliability", "REL"),
              ("3.3.4 Availability", "AVAIL"), ("3.3.5 Observability", "OBS")]
    qid = {}
    for title, area in groups:
        w("#### %s" % title)
        mine = [x for x in nfr if AREA.get(x[0]) == area]
        if not mine:
            w("No separate requirement; data integrity is covered by REQ-SEC and REQ-COMP below.")
            w("")
        for k, x in enumerate(mine, 1):
            rid = "REQ-%s-%03d" % (area, k)
            qid[x[0]] = rid
            w("- ID: %s (from %s, %s)" % (rid, x[0], x[1]))
            st, why = ensure(x)
            w("- Statement: %s" % st)
            w("- Rationale: %s" % why)
            w("- Acceptance Criteria: %s" % x[3])
            w("- Verification Method: %s" % ("Test" if "UAT" in x[3] or "test" in x[3] else "Analysis"))
            w("")
    w("### 3.4 Compliance")
    w("")
    for k, x in enumerate([x for x in nfr if AREA.get(x[0]) == "COMP"], 1):
        rid = "REQ-COMP-%03d" % k
        qid[x[0]] = rid
        w("- ID: %s (from %s, %s)" % (rid, x[0], x[1]))
        st, why = ensure(x)
        w("- Statement: %s" % st)
        w("- Rationale: %s" % why)
        w("- Acceptance Criteria: %s" % x[3])
        w("- Verification Method: %s" % ("Test" if "test" in x[3] else "Inspection"))
        w("")
    w("The business rules B1 to B11 (W6) are operative obligations; each maps to the requirements that enforce it:")
    w("")
    w("| Rule | Enforced as | Owner |")
    w("|---|---|---|")
    for b in brules:
        w("| %s %s | %s | %s |" % (b[0], b[1], b[3], b[2]))
    w("")
    w("### 3.5 Design and Implementation")
    w("")
    for title, area in [("3.5.1 Installation", "INST"), ("3.5.10 Change Management", "CM")]:
        w("#### %s" % title)
        for k, x in enumerate([x for x in nfr if AREA.get(x[0]) == area], 1):
            rid = "REQ-%s-%03d" % (area, k)
            qid[x[0]] = rid
            w("- ID: %s (from %s, %s)" % (rid, x[0], x[1]))
            st, why = ensure(x, "The rollout")
            w("- Statement: %s" % st)
            w("- Rationale: %s" % why)
            w("- Acceptance Criteria: %s" % x[3])
            w("- Verification Method: Inspection")
            w("")
    w("#### 3.5.8 Deadline")
    w("Releases R1 to R4 and their gates are in W13; full go-live, when the system becomes the record, is week 13.")
    w("")
    w("Sections 3.5.2 to 3.5.7 and 3.5.9 (build, distribution, maintainability, reusability, portability, cost, proof "
      "of concept) are not specified: this case study covers the business requirements, and the team's engineering "
      "standards apply.")
    w("")
    w("### 3.6 AI/ML")
    w("Not applicable: the system makes no model-based decisions.")
    w("")
    w("## 4. Verification")
    w("")
    w("Methods: **Test** (a UAT scenario in `uat/uat-script.xlsx`), **Inspection** (review of configuration or a "
      "document), **Analysis** (a report or measurement). Status is the sign-off of the story that holds the test.")
    w("")
    w("| Requirement ID | Source | Verification Method | Test/Artifact Link | Story |")
    w("|---|---|---|---|---|")
    for f in func:
        w("| %s | %s | %s | %s | %s |" % (f["id"], f["rule"] or "transition table", f["method"],
                                         ", ".join(f["tests"]) or "state/transitions.csv", ", ".join(f["story"]) or "none"))
    for x in nfr:
        if x[0] in qid:
            w("| %s | %s | %s | %s | |" % (qid[x[0]], x[0], "Test" if "UAT" in x[3] else "Analysis/Inspection", x[3]))
    w("")
    untested = [f["id"] for f in func if not f["tests"]]
    w("**Coverage.** %d of %d functional requirements are exercised by a UAT scenario. The other %d are moves "
      "configured in the transition table and checked by inspection: %s." % (
          len(func) - len(untested), len(func), len(untested), ", ".join(untested) or "none"))
    unmatched = sorted(used - tested)
    if unmatched:
        w("")
        w("UAT rows that check a state rather than a move, so map to no single transition: %s." % ", ".join(unmatched))
    w("")
    w("## 5. Appendixes")
    w("* Data model and data dictionary: `working-papers/W04-data-model.md`")
    w("* State diagrams: `state/diagrams/`")
    w("* Process maps (BPMN 2.0): `process/`")
    w("* Requirements traceability from objectives to tests: `working-papers/W08-traceability-matrix.md`")
    out = os.path.join(root, "srs", "srs.md")
    io.open(out, "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
    print("wrote %s . %d lines" % (out, len(md)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
