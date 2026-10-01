# -*- coding: utf-8 -*-
"""model.py -- the state model: every Tanmark document's states, who may move it, and what may never happen.

PURPOSE
  Deliverable 10. One declaration of each document's lifecycle, from which everything else is generated and checked:
  the state diagrams (Mermaid for GitHub, SVG and PNG for the report and deck), the transition table, the rules that must
  always hold, and the decided-versus-built register. The stories' error paths are checked against it, so a story cannot
  test a rule the model does not have.

CONFIG
  argv[1]  the repository root. Standard library only for the model and checks; PNGs by headless Edge when present.
  Tanmark Industries is fictional. The patterns are real ones from order-processing and accounting systems.

WORKFLOW
  1 DOCUMENTS below: per document, its states (initial first), terminal states, and transitions
    (from, event, to, roles, guard, system action); REFUSED lists moves the system must refuse, each with its reason
  2 checks: every state reachable from the initial state; every non-terminal state has an exit; terminal states have
    none; every role is a declared role; every refused move is absent from the transitions
  3 write state/state-model.md (diagrams, tables, rules, register), state/transitions.csv, state/diagrams/<doc>.svg and
    docs/img/state-<doc>.png
  4 [CONTROL] the checks are run first on a planted model with an unreachable state, a dead end and an unknown role,
    and must catch all three
  rc 0 ok . 2 usage . 3 a check failed

Q&A
  Q: why is there no Approved state on the purchase order?   A: approval is deliberately outside the system (decision
                                                              D9): the signature stays on paper, and Received counts as
                                                              approved. The trade-off is in the decision log.
  Q: why can nothing be deleted?   A: rule R1. Every closure is a state (Cancelled, Not completed, Voided, Reversed), so
                                    the record and its sequence number survive.

PITFALLS
  A transition table can pass every structural check and still permit a move the business forbids. That is why REFUSED
  lists the forbidden moves explicitly, and why the story error paths are checked against it.

NOTES
  Tanmark Industries is fictional.
"""
import csv
import html
import io
import os
import re
import subprocess
import sys

ROLES = ["Sales staff", "Sales manager", "Logistics coordinator", "Purchasing staff", "Warehouse keeper",
         "Factory manager", "Accountant", "Chief accountant", "System"]

# (from, event, to, roles, guard, system action)
DOCUMENTS = {
    "sales-order": {
        "name": "Sales order",
        "states": ["Request", "Open", "With logistics", "In production", "Receiving and shipping", "Completed",
                   "Cancelled", "Not completed"],
        "terminal": ["Completed", "Cancelled", "Not completed"],
        "transitions": [
            ("Request", "confirm order", "Open", ["Sales staff"],
             "customer, lines and prices complete; the contract is not on credit hold",
             "order number assigned; fulfilment can start"),
            ("Request", "confirm with credit release", "Open", ["Chief accountant"],
             "the contract is on credit hold; a reason is recorded", "order number assigned; the release is logged"),
            ("Request", "cancel", "Cancelled", ["Sales staff"], "", "kept as a cancelled request"),
            ("Open", "send to logistics", "With logistics", ["Sales staff"],
             "a salesperson is assigned", "sales editing locks; logistics sees the order"),
            ("Open", "cancel", "Cancelled", ["Sales staff", "Sales manager"], "", "flag only; nothing is deleted"),
            ("With logistics", "request materials", "In production", ["Logistics coordinator"],
             "a production plan exists", "material request raised for the workshop"),
            ("With logistics", "plan delivery from stock", "Receiving and shipping", ["Logistics coordinator"],
             "finished goods already in stock", "delivery trips planned"),
            ("With logistics", "cancel", "Cancelled", ["Sales manager"],
             "", "flag only; nothing is deleted"),
            ("In production", "receive finished goods", "Receiving and shipping", ["Warehouse keeper"],
             "", "stock increases; delivery trips can be planned"),
            ("In production", "close as not completed", "Not completed", ["Sales manager"],
             "", "stock already received stays valid; open demand is dropped"),
            ("Receiving and shipping", "last trip delivered", "Completed", ["System"],
             "every trip is Delivered or Returned", "order and its trips freeze"),
            ("Receiving and shipping", "close as not completed", "Not completed", ["Sales manager"],
             "", "stock already received stays valid; undelivered lines are dropped"),
        ],
        "refused": [
            ("Request", "confirm on credit hold", "The customer is over its credit limit or overdue. The chief accountant must release the order."),
            ("With logistics", "sales edit", "After handoff, sales cannot edit the order. Raise a new order for an increase."),
            ("In production", "cancel", "Production has started. Close the order as Not completed instead."),
            ("Receiving and shipping", "cancel", "Goods exist. Close the order as Not completed instead."),
            ("Completed", "edit", "A completed order is frozen."),
        ],
        "notes": ["After **send to logistics**, sales can no longer edit the order. A quantity may be reduced at any "
                  "stage; an increase is raised as a new order.",
                  "The sales document also carries three statuses, rolled up from its trips and invoices (see **Sale statuses**).",
                  "A contract is on credit hold while its balance is above the credit limit or an invoice is past its due date (R10)."],
    },
    "delivery-trip": {
        "name": "Delivery trip",
        "states": ["Planned", "Issued", "In transit", "Delivered", "Returned"],
        "terminal": ["Delivered", "Returned"],
        "transitions": [
            ("Planned", "issue", "Issued", ["Warehouse keeper"],
             "issued quantity equals planned quantity", "stock decreases; issue form numbered"),
            ("Issued", "dispatch", "In transit", ["Logistics coordinator"],
             "departure time set; the trip's invoice is Raised", "the trip leaves with its invoice"),
            ("In transit", "confirm delivery", "Delivered", ["Logistics coordinator"],
             "arrival time set", "trip becomes read-only"),
            ("In transit", "record return", "Returned", ["Warehouse keeper"],
             "", "returned goods received back into stock; the trip's invoice is credited"),
        ],
        "refused": [
            ("Delivered", "edit times or quantities", "A delivered trip is read-only."),
            ("Planned", "issue a different quantity", "Issue exactly the plan, or revise the plan first."),
            ("Planned", "edit when the order is closed", "A completed, cancelled or not-completed order freezes its trips."),
            ("Planned", "download numbered form", "No stock has moved yet. Preview the draft form; its number is given when the goods are issued."),
            ("Issued", "dispatch without an invoice", "Goods leave only with their invoice. Raise the trip's invoice first."),
        ],
        "notes": ["Each line on a trip has its own status (issued, received, returned) that rolls up to the trip.",
                  "Each trip has exactly one invoice, raised after the goods are issued and before the trip leaves (R9).",
                  "Before the stock moves, the warehouse keeper can preview and download the form as a draft with no number; the official number is given with the movement (D15, R8)."],
    },
    "material-request": {
        "name": "Material request",
        "states": ["Open", "Issuing", "Completed", "Cancelled"],
        "terminal": ["Completed", "Cancelled"],
        "transitions": [
            ("Open", "issue first materials", "Issuing", ["Warehouse keeper"],
             "the factory manager is assigned", "stock decreases; issue form numbered"),
            ("Open", "cancel", "Cancelled", ["Factory manager"], "nothing issued", "flag only"),
            ("Issuing", "issue more materials", "Issuing", ["Warehouse keeper"], "lines still open",
             "stock decreases; a new issue form numbered"),
            ("Issuing", "issue last materials", "Completed", ["Warehouse keeper"], "every line issued in full", "issue form numbered"),
        ],
        "refused": [
            ("Issuing", "cancel", "Materials have left the warehouse. Complete the request, or close the order as Not completed."),
            ("Open", "download numbered form", "No stock has moved yet. Preview the draft form; its number is given when the materials are issued."),
        ],
        "notes": ["Before the stock moves, the warehouse keeper can preview and download the form as a draft with no number; the official number is given with the movement (D15, R8)."],
    },
    "purchase-order": {
        "name": "Purchase order",
        "states": ["Open", "Received", "Completed", "Cancelled"],
        "terminal": ["Completed", "Cancelled"],
        "transitions": [
            ("Open", "receive into stock", "Received", ["Warehouse keeper"],
             "goods counted against the order", "stock increases; receipt form numbered; the order counts as approved (D9)"),
            ("Received", "receive more", "Received", ["Warehouse keeper"], "goods counted against the open lines",
             "stock increases; a new receipt form numbered"),
            ("Open", "cancel", "Cancelled", ["Purchasing staff"], "nothing received", "flag only"),
            ("Received", "close", "Completed", ["Purchasing staff"],
             "every line received; the supplier invoice is recorded", ""),
        ],
        "refused": [
            ("Received", "cancel", "Goods are in stock. Return them to the supplier instead."),
            ("Open", "download numbered form", "No stock has moved yet. Preview the draft form; its number is given when the goods are received."),
        ],
        "notes": ["There is no Approved state. The signature stays on paper, outside the system (decision D9).",
                  "Before the stock moves, the warehouse keeper can preview and download the form as a draft with no number; the official number is given with the movement (D15, R8)."],
    },
    "sales-invoice": {
        "name": "Sales invoice and receivable (one per trip)",
        "states": ["Draft", "Raised", "Partly paid", "Paid", "Credited"],
        "terminal": ["Paid", "Credited"],
        "transitions": [
            ("Draft", "raise", "Raised", ["Accountant"], "the trip is Issued; one invoice per trip",
             "invoice number assigned; due date set from the contract's payment terms"),
            ("Raised", "record payment", "Paid", ["Accountant"],
             "the trip is Delivered; a receipt allocated, equal to the balance", "balance cleared"),
            ("Raised", "record part payment", "Partly paid", ["Accountant"],
             "the trip is Delivered; a receipt allocated, less than the balance", "balance due updated"),
            ("Raised", "credit in part", "Raised", ["Chief accountant"],
             "a credit note for less than the balance: a price correction or a short return",
             "credit note issued; balance reduced"),
            ("Partly paid", "credit in part", "Partly paid", ["Chief accountant"],
             "a credit note for less than the balance still due", "credit note issued; balance reduced"),
            ("Partly paid", "record part payment", "Partly paid", ["Accountant"], "a balance is still due",
             "balance due updated"),
            ("Partly paid", "record final payment", "Paid", ["Accountant"], "receipts equal the amount due",
             "balance cleared"),
            ("Raised", "credit in full", "Credited", ["Chief accountant"], "the trip is Returned",
             "credit note issued; balance cleared"),
        ],
        "refused": [
            ("Draft", "raise before the trip is issued",
             "Raise the invoice for goods the warehouse has issued to the trip."),
            ("Raised", "edit amount", "Correct an invoice with a credit note, never by editing it."),
        ],
        "notes": ["The due date is the invoice date plus the payment terms of the customer's contract: 30 days unless "
                  "the contract sets other terms (R10).",
                  "Overdue is not a state. It is the invoice's age past its due date, shown in the ageing view: "
                  "current, 1 to 30, 31 to 60, 61 to 90 and over 90 days.",
                  "A customer's transfer usually pays several invoices. The receipt voucher is allocated to them, "
                  "oldest due date first, and only to invoices whose trip is Delivered; anything else is held "
                  "unallocated and flagged to finance.",
                  "Each quarter, the open receivables are reconciled with every customer on a statement the customer "
                  "signs."],
    },
    "sale-statuses": {
        "name": "Sale statuses: invoiced, delivered, paid",
        "states": ["Not invoiced", "Partly invoiced", "Invoiced", "Not delivered", "Partly delivered", "Delivered",
                   "Unpaid", "Partly paid", "Paid"],
        "terminal": ["Invoiced", "Delivered", "Paid"],
        "axes": [["Not invoiced", "Partly invoiced", "Invoiced"], ["Not delivered", "Partly delivered", "Delivered"],
                 ["Unpaid", "Partly paid", "Paid"]],
        "transitions": [
            ("Not invoiced", "first trip invoiced", "Partly invoiced", ["System"], "trips still to invoice", ""),
            ("Partly invoiced", "last trip invoiced", "Invoiced", ["System"], "every trip has its invoice", ""),
            ("Not invoiced", "every trip invoiced", "Invoiced", ["System"], "a single trip, or all at once", ""),
            ("Not delivered", "first trip delivered", "Partly delivered", ["System"], "trips still in transit", ""),
            ("Partly delivered", "last trip delivered", "Delivered", ["System"], "every trip is Delivered or Returned", ""),
            ("Not delivered", "every trip delivered", "Delivered", ["System"], "a single trip, or all at once", ""),
            ("Unpaid", "first payment allocated", "Partly paid", ["System"], "a balance is still due", ""),
            ("Partly paid", "last payment allocated", "Paid", ["System"], "every invoice is Paid or Credited", ""),
            ("Unpaid", "paid in full", "Paid", ["System"], "every invoice is Paid or Credited", ""),
        ],
        "refused": [
            ("Not invoiced", "deliver before invoicing", "A trip leaves only with its invoice. Raise the trip's invoice first."),
        ],
        "notes": ["Each status rolls up from the trips and their invoices; nobody sets it by hand.",
                  "A returned trip counts as closed for both roll-ups: its goods are back in stock, and its invoice "
                  "is credited. So a return does not leave the sale, or the order, waiting for ever.",
                  "The three move in order. A trip leaves only with its invoice (R9), and customers pay on credit "
                  "terms after delivery (R10), so a sale is never more delivered than invoiced, or paid before it is "
                  "delivered. The legal combinations are in working paper W6."],
    },
    "voucher": {
        "name": "Accounting voucher (receipt or payment)",
        "states": ["Saved", "Posted", "Voided", "Reversed"],
        "terminal": ["Voided", "Reversed"],
        "transitions": [
            ("Saved", "post", "Posted", ["Accountant"], "the entries balance", "voucher locks; ledger updated"),
            ("Saved", "void", "Voided", ["Accountant"], "", "amount set to zero; number kept in the sequence"),
            ("Posted", "reverse", "Reversed", ["Chief accountant"], "a reason is recorded",
             "an offsetting voucher is posted; the original stays"),
        ],
        "refused": [
            ("Posted", "edit", "A posted voucher is locked. Reverse it instead."),
            ("Saved", "delete", "Nothing is ever deleted. Void it instead."),
        ],
        "notes": ["Saving and posting are separate acts. Only posting reaches the ledger."],
    },
}

# The rule each move enforces (document, from state, event) -> rule id. Refused moves must all have one.
RULE_FOR = {
    ("sales-order", "Open", "send to logistics"): "R6",
    ("sales-order", "Request", "cancel"): "R1",
    ("sales-order", "Open", "cancel"): "R1",
    ("sales-order", "With logistics", "cancel"): "R1",
    ("sales-order", "In production", "close as not completed"): "R3",
    ("sales-order", "Receiving and shipping", "close as not completed"): "R3",
    ("sales-order", "Receiving and shipping", "last trip delivered"): "R4",
    ("sales-order", "With logistics", "sales edit"): "R6",
    ("sales-order", "In production", "cancel"): "R3",
    ("sales-order", "Receiving and shipping", "cancel"): "R3",
    ("sales-order", "Completed", "edit"): "R4",
    ("delivery-trip", "Planned", "issue"): "R5",
    ("delivery-trip", "In transit", "confirm delivery"): "R4",
    ("delivery-trip", "Delivered", "edit times or quantities"): "R4",
    ("delivery-trip", "Planned", "issue a different quantity"): "R5",
    ("delivery-trip", "Planned", "edit when the order is closed"): "R4",
    ("material-request", "Open", "cancel"): "R1",
    ("material-request", "Issuing", "cancel"): "R3",
    ("purchase-order", "Open", "cancel"): "R1",
    ("purchase-order", "Received", "cancel"): "R3",
    ("sales-order", "Request", "confirm on credit hold"): "R10",
    ("sales-order", "Request", "confirm with credit release"): "R10",
    ("delivery-trip", "Issued", "dispatch"): "R9",
    ("delivery-trip", "Issued", "dispatch without an invoice"): "R9",
    ("sales-invoice", "Draft", "raise"): "R9",
    ("sale-statuses", "Not invoiced", "deliver before invoicing"): "R9",
    ("sales-invoice", "Draft", "raise before the trip is issued"): "R9",
    ("sales-invoice", "Raised", "edit amount"): "R2",
    ("sales-invoice", "Raised", "credit in full"): "R2",
    ("sales-invoice", "Raised", "credit in part"): "R2",
    ("sales-invoice", "Partly paid", "credit in part"): "R2",
    ("voucher", "Saved", "post"): "R2",
    ("voucher", "Saved", "void"): "R1",
    ("voucher", "Posted", "reverse"): "R2",
    ("voucher", "Posted", "edit"): "R2",
    ("voucher", "Saved", "delete"): "R1",
    ("material-request", "Open", "issue first materials"): "R8",
    ("material-request", "Issuing", "issue last materials"): "R8",
    ("material-request", "Open", "download numbered form"): "R8",
    ("purchase-order", "Open", "receive into stock"): "R8",
    ("purchase-order", "Received", "receive more"): "R8",
    ("material-request", "Issuing", "issue more materials"): "R8",
    ("purchase-order", "Open", "download numbered form"): "R8",
    ("delivery-trip", "Planned", "download numbered form"): "R8",
}

RULES = [
    ("R1", "No document is ever deleted. Every closure is a state, so each record and its number survive."),
    ("R2", "A posted voucher or a raised invoice never changes. A correction is a reversing voucher or a credit note."),
    ("R3", "Nothing that has moved stock is cancelled. An order in production closes as Not completed; a material "
           "request that has issued completes; a received purchase order is returned to the supplier."),
    ("R4", "A delivered trip is read-only, and a closed order freezes itself and all its trips."),
    ("R5", "The warehouse issues exactly the planned quantity, or the plan is revised first."),
    ("R6", "After an order goes to logistics, sales cannot edit it. A quantity may fall in place; a rise is a new order."),
    ("R7", "Roles grant access to data; the transition table grants the right to move a document. The two are separate."),
    ("R8", "A stock form gets its official number only when the stock moves. Before that it is a draft with no number."),
    ("R9", "Goods leave only with their invoice: each trip has one invoice, raised before the trip is dispatched."),
    ("R10", "Sales are on credit terms set per customer and contract, 30 days unless the contract says otherwise. A "
            "customer over its credit limit, or with an invoice past due, gets no new order unless the chief "
            "accountant releases it."),
]

# Tanmark's decided-versus-built register, found during UAT (fictional; the kind of gap is real).
REGISTER = [
    ("DB-1", "R2 posted vouchers are locked", "vouchers had no posted status; saved and posted looked the same",
     "found in UAT; ticketed; a go / no-go criterion for finance"),
    ("DB-2", "R6 sales cannot edit after handoff", "sales could still edit an order with logistics",
     "found in UAT; fixed before the parallel run"),
    ("DB-3", "R7 account changes need a role", "chart-of-accounts permission checks were switched off during the build",
     "found in UAT; switched on before the parallel run"),
    ("DB-4", "R3 nothing that has moved stock is cancelled", "built as decided", "no gap"),
]


def check(docs, roles):
    problems = []
    for key, d in docs.items():
        states, term = d["states"], set(d["terminal"])
        out = {}
        for f, ev, t, rs, _, _ in d["transitions"]:
            for s in (f, t):
                if s not in states:
                    problems.append("%s: transition uses an undeclared state %s" % (key, s))
            out.setdefault(f, []).append(t)
            for r in rs:
                if r not in roles:
                    problems.append("%s: unknown role %s" % (key, r))
        starts = [a[0] for a in d["axes"]] if "axes" in d else [states[0]]
        seen, todo = set(starts), list(starts)
        while todo:
            s = todo.pop()
            for n in out.get(s, []):
                if n not in seen:
                    seen.add(n)
                    todo.append(n)
        for s in states:
            if s not in seen:
                problems.append("%s: state %s is unreachable" % (key, s))
            if s not in term and not out.get(s):
                problems.append("%s: state %s is a dead end" % (key, s))
            if s in term and out.get(s):
                problems.append("%s: terminal state %s has an exit" % (key, s))
        legal = {(f, ev) for f, ev, *_ in d["transitions"]}
        for f, ev, _ in d.get("refused", []):
            if docs is DOCUMENTS and (key, f, ev) not in RULE_FOR:
                problems.append("%s: refused move %s from %s names no rule" % (key, ev, f))
        for f, ev, _ in d.get("refused", []):
            if (f, ev) in legal:
                problems.append("%s: refused move %s from %s is also a transition" % (key, ev, f))
    return problems


def mermaid(d):
    ident = {s: "s%d" % i for i, s in enumerate(d["states"])}
    lines = ["```mermaid", "stateDiagram-v2", "    direction LR"]
    for s in d["states"]:
        lines.append('    state "%s" as %s' % (s, ident[s]))
    starts = [a[0] for a in d["axes"]] if "axes" in d else [d["states"][0]]
    for s in starts:
        lines.append("    [*] --> %s" % ident[s])
    for f, ev, t, *_ in d["transitions"]:
        lines.append("    %s --> %s: %s" % (ident[f], ident[t], ev))
    for s in d["terminal"]:
        lines.append("    %s --> [*]" % ident[s])
    lines.append("```")
    return "\n".join(lines)


def svg(d):
    """A layered layout: the longest forward path on row 0, every other state on the rows below, under its source."""
    states = d["states"]
    out = {}
    for f, _, t, *_ in d["transitions"]:
        out.setdefault(f, []).append(t)
    if "axes" in d:
        pos = {s: (i, r) for r, axis in enumerate(d["axes"]) for i, s in enumerate(axis)}
    else:
        path, s = [states[0]], states[0]
        while out.get(s):
            nxt = [n for n in out[s] if n not in path and n not in d["terminal"]] or \
                  [n for n in out[s] if n not in path]
            s = nxt[0]
            path.append(s)
        pos = {s: (i, 0) for i, s in enumerate(path)}
        row = 1
        for s in states:
            if s in pos:
                continue
            src = min((pos[f][0] for f, _, t, *_ in d["transitions"] if t == s and f in pos), default=0)
            pos[s] = (src + 1, row)
            row += 1
    W, H, GX, GY, X0, Y0 = 190, 56, 150, 58, 30, 84
    cols = max(c for c, _ in pos.values()) + 1
    rows = max(r for _, r in pos.values()) + 1
    width, height = X0 * 2 + cols * W + (cols - 1) * GX, Y0 + rows * (H + GY) - GY + 30
    box = {s: (X0 + c * (W + GX), Y0 + r * (H + GY)) for s, (c, r) in pos.items()}
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'font-family="Segoe UI, Arial, sans-serif">' % (width, height, width, height),
         '<rect width="100%" height="100%" fill="#FFFFFF"/>',
         '<defs><marker id="a" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
         '<path d="M0,0 L10,5 L0,10 z" fill="#16232B"/></marker></defs>',
         '<text x="%d" y="28" font-size="17" font-weight="600" fill="#16232B">%s</text>' % (X0, html.escape(d["name"]))]
    shared = {}
    for f, ev, t, *_ in d["transitions"]:
        (fx, fy), (tx, ty) = box[f], box[t]
        if f == t:  # a move that keeps its state: a small loop, above the box unless a row-skipping arc runs there
            arc_over = any(box[a][1] == fy and box[b][1] == fy and abs(box[b][0] - box[a][0]) > W + GX
                           and min(box[a][0], box[b][0]) < fx < max(box[a][0], box[b][0])
                           for a, _, b, *_ in d["transitions"])
            y0, dy = (fy + H, 22) if arc_over else (fy, -22)
            off = W * 0.5 * shared.get((f, t), 0)  # a second loop on the same box sits beside the first
            pts = [(fx + W * 0.08 + off, y0), (fx + W * 0.08 + off, y0 + dy), (fx + W * 0.42 + off, y0 + dy),
                   (fx + W * 0.42 + off, y0)]
            lx, ly = fx + W * 0.25 + off, y0 + dy + (14 if arc_over else -5)
        elif fy == ty and abs(tx - fx) > W + GX:  # skips a column: arc over the row so no box hides it
            top = fy - 26
            pts = [(fx + W / 2, fy), (fx + W / 2, top), (tx + W / 2, top), (tx + W / 2, ty)]
            lx, ly = (fx + tx + W) / 2, top - 6
        elif fy == ty:
            pts = [(fx + W, fy + H / 2), (tx, ty + H / 2)]
            lx, ly = (fx + W + tx) / 2, fy + H / 2 - 7
        elif fx == tx:  # straight down into the top of the target
            pts = [(fx + W / 2, fy + H), (tx + W / 2, ty)]
            lx, ly = fx + W / 2 + 8, (fy + H + ty) / 2 + 4
        else:  # down from the source, then along into the nearer side of the target
            sx = fx + W / 2
            ex = tx if tx > fx else tx + W
            pts = [(sx, fy + H), (sx, ty + H / 2), (ex, ty + H / 2)]
            lx, ly = (sx + ex) / 2, ty + H / 2 - 7
        k = shared.get((f, t), 0)  # a second move along the same arrow puts its label under the line
        shared[(f, t)] = k + 1
        if k and fy == ty and f != t:
            ly += 20 * k
        o.append('<polyline points="%s" fill="none" stroke="#16232B" stroke-width="1.3" marker-end="url(#a)"/>'
                 % " ".join("%d,%d" % p for p in pts))
        anchor = "start" if fx == tx and fy != ty else "middle"
        o.append('<text x="%d" y="%d" font-size="11" fill="#5B6B73" text-anchor="%s">%s</text>'
                 % (lx, ly, anchor, html.escape(ev)))
    for s, (x, y) in box.items():
        terminal = s in d["terminal"]
        o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="%s" stroke-width="%s"/>'
                 % (x, y, W, H, 28, "#F1F5F6" if terminal else "#DCEBEE", "#1D5C6B", 2.4 if terminal else 1.4))
        o.append('<text x="%d" y="%d" font-size="14" text-anchor="middle" fill="#16232B">%s</text>'
                 % (x + W / 2, y + H / 2 + 5, html.escape(s)))
    o.append("</svg>")
    return "\n".join(o), width, height


def to_png(svg_path, png_path, w, h):
    edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge):
        return "skipped, Edge not found"
    subprocess.run([edge, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=%d,%d" % (w, h), "--screenshot=%s" % os.path.abspath(png_path),
                    "file:///" + os.path.abspath(svg_path).replace(os.sep, "/")], capture_output=True)
    return os.path.basename(png_path) if os.path.exists(png_path) else "FAILED"


def markdown():
    md = ["# State model: Tanmark Industries", "",
          "**Tanmark Industries is fictional.** The patterns are real ones from order-processing and accounting "
          "systems. Generated by `state/model.py`; do not edit by hand.", "",
          "Every document below has a lifecycle. Each move names its event, the role allowed to make it, the condition "
          "that must hold, and what the system does. Moves the system must refuse are listed too, because each one is "
          "an error path in the user stories.", "",
          "## Rules that always hold", "", "| ID | Rule |", "|---|---|"]
    md += ["| %s | %s |" % r for r in RULES]
    for key, d in DOCUMENTS.items():
        md += ["", "## %s" % d["name"], "", mermaid(d), ""]
        md += ["| From | Event | To | Who | Condition | System action |", "|---|---|---|---|---|---|"]
        md += ["| %s | %s | %s | %s | %s | %s |" % (f, ev, t, ", ".join(rs), g or "none", a or "none")
               for f, ev, t, rs, g, a in d["transitions"]]
        if d.get("refused"):
            md += ["", "**Refused:**", ""]
            md += ["* %s: **%s** is refused. %s" % (f, ev, why) for f, ev, why in d["refused"]]
        md += [""] + ["%s" % n for n in d["notes"]]
    md += ["", "## Decided versus built", "",
           "Rules decided in the meetings, checked against the build during UAT. **Fictional entries; the kind of gap "
           "is real.** A BA finds these by testing each rule, not by reading the code.", "",
           "| ID | Decided | Found in the build | Outcome |", "|---|---|---|---|"]
    md += ["| %s | %s | %s | %s |" % r for r in REGISTER]
    return "\n".join(md) + "\n"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = argv[1]
    planted = {"x": {"name": "x", "states": ["A", "B", "C"], "terminal": ["C"],
                     "transitions": [("A", "go", "C", ["Nobody"], "", "")], "refused": []}}
    caught = check(planted, ROLES)
    kinds = {k for k in ("unreachable", "dead end", "unknown role") if any(k in p for p in caught)}
    print("[CONTROL] planted defects caught: %s" % sorted(kinds))
    if len(kinds) != 3:
        return 3
    problems = check(DOCUMENTS, ROLES)
    for p in problems:
        print("  PROBLEM " + p)
    if problems:
        print("[RESULT] REFUSED")
        return 3
    sd = os.path.join(root, "state")
    os.makedirs(os.path.join(sd, "diagrams"), exist_ok=True)
    io.open(os.path.join(sd, "state-model.md"), "w", encoding="utf-8", newline="\n").write(markdown())
    with io.open(os.path.join(sd, "transitions.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["document", "from", "event", "to", "roles", "condition", "system_action", "kind", "rule"])
        for key, d in DOCUMENTS.items():
            for fr, ev, t, rs, g, a in d["transitions"]:
                w.writerow([key, fr, ev, t, "; ".join(rs), g, a, "allowed", RULE_FOR.get((key, fr, ev), "")])
            for fr, ev, why in d.get("refused", []):
                w.writerow([key, fr, ev, "", "", why, "", "refused", RULE_FOR.get((key, fr, ev), "")])
    for key, d in DOCUMENTS.items():
        text, wd, ht = svg(d)
        p = os.path.join(sd, "diagrams", key + ".svg")
        io.open(p, "w", encoding="utf-8", newline="\n").write(text)
        print("  %-17s states %d . transitions %d . refused %d . %s" % (
            key, len(d["states"]), len(d["transitions"]), len(d.get("refused", [])),
            to_png(p, os.path.join(root, "docs", "img", "state-%s.png" % key), wd, ht)))
    print("rules %d . register rows %d . roles %d" % (len(RULES), len(REGISTER), len(ROLES)))
    print("[RESULT] ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
