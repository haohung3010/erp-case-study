# -*- coding: utf-8 -*-
"""build_maps.py -- the before and after order-to-cash and procure-to-pay maps, as BPMN 2.0 XML and as SVG, from one description.

PURPOSE
  One source for each map. The .bpmn file opens in bpmn.io (it carries diagram interchange, so it renders as laid
  out here); the .svg is the same layout drawn in the portfolio's diagrams design for the README and the report.

CONFIG
  Run: python process/build_maps.py . Writes process/before.bpmn, before.svg, after.bpmn, after.svg.
  Standard library only. Colours come from one small palette, defined below.

WORKFLOW
  1 each map = lanes (rows), nodes (kind, lane, column, label, changed flag), flows (from, to, label)
  2 layout: a node's x comes from its column, its y from its lane; flows run right-then-down or right-then-up
  3 write BPMN XML: collaboration, one participant, a lane set, the flow nodes, sequence flows, and DI shapes and edges
  4 write SVG: lanes as bands, tasks as rounded boxes, gateways as diamonds, events as circles, arrows with labels
  5 [CONTROL] parse each .bpmn back and check every flow's ends exist and every node sits in exactly one lane

Q&A
  Q: why generate rather than draw?   A: the maps change with the case study; one description keeps the XML, the
                                         picture and the traceability ids (T1, T2 ...) in step.

PITFALLS
  bpmn.io needs the DI section to render; without it a valid model opens as a blank canvas.

NOTES
  The company is fictional (company/profile.md).
"""
import html
import io
import os
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
C = {"ink": "#16232B", "paper": "#FFFFFF", "task": "#DCEBEE", "task_stroke": "#1D5C6B", "gateway": "#F5E9CC",
     "gateway_stroke": "#906915", "lane": "#F1F5F6", "changed": "#906915", "rule": "#D5DDE0", "muted": "#5B6B73"}
COL_W, LANE_H, LEFT, TOP, TASK_W, TASK_H = 150, 120, 150, 20, 120, 60

BEFORE = {
    "id": "before", "name": "Order to cash, before (paper, email and spreadsheets)",
    "lanes": ["Sales", "Logistics", "Purchasing", "Warehouse", "Production", "Accounting"],
    "nodes": [
        ("S", "start", 0, 0, "Customer phones or emails", False),
        ("T1", "task", 0, 1, "Write a paper order form", False),
        ("T2", "task", 1, 2, "Walk the shelves to check stock", False),
        ("G1", "gateway", 1, 3, "In stock?", False),
        ("T3", "task", 2, 4, "Email supplier; note it in a spreadsheet", False),
        ("T4", "task", 3, 5, "Receive materials; tick paper note", False),
        ("T5", "task", 4, 6, "Build from a paper job card", False),
        ("T6", "task", 3, 7, "Ship with a paper delivery note", False),
        ("T7", "task", 5, 8, "Key the invoice into the accounting tool", False),
        ("T8", "task", 5, 9, "Match payment to invoice by hand", False),
        ("T9", "task", 5, 10, "Find overdue customers at the quarter-end statement", False),
        ("E1", "end", 5, 11, "Paid", False),
    ],
    "flows": [("S", "T1", ""), ("T1", "T2", "form carried"), ("T2", "G1", ""), ("G1", "T3", "no"),
              ("G1", "T6", "yes"), ("T3", "T4", ""), ("T4", "T5", ""), ("T5", "T6", ""),
              ("T6", "T7", "paper copies"), ("T7", "T8", ""), ("T8", "T9", ""), ("T9", "E1", "")],
}

AFTER = {
    "id": "after", "name": "Order to cash and procure to pay, after (one system, one data model)",
    "lanes": ["Sales", "Logistics", "Purchasing", "Warehouse", "Production", "Accounting"],
    # the rules the state model implies (state/state-model.md), checked on the flow graph
    "rules": {"must_pass": [("T3", "S", "E1"), ("T10", "S", "E1"), ("T16", "S", "E1"), ("T11", "S", "E1"), ("T12", "S", "E3")]},
    # every task that moves a document names its move in state/transitions.csv: (document, from, event)
    "moves": {
        "T2": ("sales-order", "Request", "confirm order"),
        "T18": ("sales-order", "Request", "confirm with credit release"),
        "T3": ("sales-order", "Open", "send to logistics"),
        "T14": ("sales-order", "With logistics", "cancel"),
        "T4": ("sales-order", "With logistics", "request materials"),
        "T6": ("purchase-order", "Open", "receive into stock"),
        "T7": ("material-request", "Open", "issue first materials"),
        "T15": ("sales-order", "In production", "close as not completed"),
        "T9": ("sales-order", "In production", "receive finished goods"),
        "T16": ("delivery-trip", "Planned", "issue"),
        "T17": ("delivery-trip", "Issued", "dispatch"),
        "T11": ("sales-invoice", "Draft", "raise"),
        "T12": ("voucher", "Saved", "post"),
        "T13": ("voucher", "Saved", "post"),
    },
    "nodes": [
        ("S", "start", 0, 0, "Customer places an order", False),
        ("T1", "task", 0, 1, "Save order request", True),
        ("G5", "gateway", 0, 2, "Contract on credit hold?", True),
        ("T18", "task", 5, 2, "Chief accountant releases, with a reason", True),
        ("T2", "task", 0, 3, "Confirm order", True),
        ("T3", "task", 0, 4, "Send to logistics; sales editing locks", True),
        ("G0", "gateway", 0, 5, "Order withdrawn?", True),
        ("T14", "task", 0, 6, "Cancel the order (before production)", True),
        ("E4", "end", 0, 7, "Cancelled", True),
        ("G1", "gateway", 1, 6, "Finished goods in stock?", True),
        ("T4", "task", 1, 7, "Raise material request", True),
        ("G2", "gateway", 3, 8, "Materials in stock?", False),
        ("T5", "task", 2, 9, "Create purchase order (signed on paper)", True),
        ("T6", "task", 3, 10, "Receive into stock; order counts as approved", True),
        ("P1", "parallel", 3, 11, "", False),
        ("T7", "task", 3, 12, "Issue materials to the workshop", True),
        ("T13", "task", 5, 12, "Record supplier invoice; post payment", True),
        ("E2", "end", 5, 13, "Supplier paid", False),
        ("T8", "task", 4, 13, "Build and test the goods", False),
        ("G3", "gateway", 4, 14, "Order still wanted?", True),
        ("T15", "task", 0, 16, "Close as not completed; stock kept", True),
        ("E5", "end", 0, 17, "Not completed", True),
        ("T9", "task", 3, 15, "Receive finished goods", False),
        ("T10", "task", 1, 17, "Plan delivery trips", True),
        ("T16", "task", 3, 18, "Issue goods to the trip; form numbered", True),
        ("T11", "task", 5, 19, "Raise the trip's invoice", True),
        ("T17", "task", 1, 20, "Dispatch with the invoice; deliver", True),
        ("P2", "parallel", 1, 21, "", False),
        ("E1", "end", 1, 22, "Order Completed", True),
        ("T12", "task", 5, 22, "Collect on terms; post receipt voucher", True),
        ("E3", "end", 5, 23, "Paid", False),
    ],
    "flows": [("S", "T1", ""), ("T1", "G5", ""), ("G5", "T2", "no"), ("G5", "T18", "yes"), ("T18", "T3", ""),
              ("T2", "T3", ""), ("T3", "G0", ""),
              ("G0", "T14", "yes"), ("T14", "E4", ""), ("G0", "G1", "no", "down"),
              ("G1", "T4", "no"), ("G1", "T10", "yes", "top"), ("T4", "G2", ""),
              ("G2", "T7", "yes", "top"), ("G2", "T5", "no"), ("T5", "T6", ""), ("T6", "P1", ""),
              ("P1", "T7", ""), ("P1", "T13", ""), ("T13", "E2", ""), ("T7", "T8", ""), ("T8", "G3", ""),
              ("G3", "T9", "yes"), ("G3", "T15", "no"), ("T15", "E5", ""),
              ("T9", "T10", ""), ("T10", "T16", ""), ("T16", "T11", ""), ("T11", "T17", ""), ("T17", "P2", ""), ("P2", "E1", ""), ("P2", "T12", ""),
              ("T12", "E3", "")],
}

PERIODIC = {
    "id": "periodic", "name": "Periodic routines, after: ageing, reconciliations and price lists",
    "lanes": ["Sales", "Warehouse", "Price control", "Accounting"],
    "nodes": [
        ("S1", "start", 3, 0, "Each week", False),
        ("T1", "task", 3, 1, "Run the ageing view of open invoices", True),
        ("G1", "gateway", 3, 2, "Overdue or over the limit?", True),
        ("T2", "task", 0, 3, "Contract on credit hold; sales chases the customer", True),
        ("E1", "end", 0, 4, "Chased", False),
        ("E2", "end", 3, 3, "Nothing overdue", False),
        ("S2", "start", 1, 5, "Month end", False),
        ("T3", "task", 1, 6, "Count stock", False),
        ("T4", "task", 3, 7, "Reconcile the count with the books", True),
        ("G2", "gateway", 3, 8, "Any difference?", True),
        ("E3", "end", 3, 9, "Reconciled", False),
        ("T5", "task", 1, 9, "Find the step that skipped the system; sign off the difference", True),
        ("E4", "end", 1, 10, "Signed off", False),
        ("S3", "start", 3, 11, "Quarter end", False),
        ("T6", "task", 3, 12, "Send each customer its statement of open invoices", True),
        ("T7", "task", 0, 13, "Customer signs, or disputes a line", False),
        ("G3", "gateway", 0, 14, "Signed?", False),
        ("E5", "end", 0, 15, "Reconciled", False),
        ("T8", "task", 3, 15, "Resolve the dispute; credit note if owed", True),
        ("E6", "end", 3, 16, "Resolved", False),
        ("S4", "start", 2, 17, "Supplier sends a new price list", False),
        ("T9", "task", 2, 18, "Load it one week before it takes effect", True),
        ("E7", "end", 2, 19, "Loaded on time", False),
    ],
    "flows": [("S1", "T1", ""), ("T1", "G1", ""), ("G1", "T2", "yes"), ("G1", "E2", "no"), ("T2", "E1", ""),
              ("S2", "T3", ""), ("T3", "T4", ""), ("T4", "G2", ""), ("G2", "E3", "no"), ("G2", "T5", "yes"),
              ("T5", "E4", ""),
              ("S3", "T6", ""), ("T6", "T7", ""), ("T7", "G3", ""), ("G3", "E5", "yes"), ("G3", "T8", "no"),
              ("T8", "E6", ""),
              ("S4", "T9", ""), ("T9", "E7", "")],
}


def box(kind, lane, col):
    cx = LEFT + col * COL_W + COL_W / 2
    cy = TOP + lane * LANE_H + LANE_H / 2
    w, h = {"task": (TASK_W, TASK_H), "gateway": (50, 50), "parallel": (50, 50)}.get(kind, (36, 36))
    return cx - w / 2, cy - h / 2, w, h


def route(a, b, mode=""):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    acx, bcx = ax + aw / 2, bx + bw / 2
    if mode == "down":  # out of the source's bottom, straight down, then along into the target's side
        return [(acx, ay + ah), (acx, by + bh / 2), (bx, by + bh / 2)]
    if mode == "top":  # up out of the source, along above the row, down into the target: skips what lies between
        high = min(ay, by) - 24
        return [(acx, ay), (acx, high), (bcx, high), (bcx, by)]
    if mode == "bottom":  # along the source's row, then up into the target's underside
        return [(ax + aw, ay + ah / 2), (bcx, ay + ah / 2), (bcx, by + bh)]
    if abs(acx - bcx) < 1 and ay != by:  # same column: straight down or up
        return [(acx, ay + ah), (bcx, by)] if by > ay else [(acx, ay), (bcx, by + bh)]
    if bx <= ax:  # a loop back: go down, left, up
        low = max(ay + ah, by + bh) + 18
        return [(acx, ay + ah), (acx, low), (bcx, low), (bcx, by + bh)]
    sx, sy = ax + aw, ay + ah / 2
    ex, ey = bx, by + bh / 2
    if abs(sy - ey) < 1:
        return [(sx, sy), (ex, ey)]
    mx = ex - 15  # run along the source lane, turn next to the target
    return [(sx, sy), (mx, sy), (mx, ey), (ex, ey)]


def label_at(pts):
    """Where a flow's label goes: the loop's bottom run, a vertical's side, a short first run's turn, else its middle."""
    if len(pts) == 4 and pts[1][1] == pts[2][1] and pts[0][0] == pts[1][0]:
        (x1, y1), (x2, y2) = pts[1], pts[2]
        return (x1 + x2) / 2, y1 + 12
    (x1, y1), (x2, y2) = pts[0], pts[1]
    if x1 == x2:
        return x1 + 5, (y1 + y2) / 2
    if abs(x2 - x1) < 90 and len(pts) > 2:  # too short to hold a word: label the vertical that follows
        return x2 + 5, (y2 + pts[2][1]) / 2
    return (x1 + x2) / 2 - 8, y1 - 5


def bpmn(m):
    B = "http://www.omg.org/spec/BPMN/20100524/MODEL"
    DI = "http://www.omg.org/spec/BPMN/20100524/DI"
    DC = "http://www.omg.org/spec/DD/20100524/DC"
    DDI = "http://www.omg.org/spec/DD/20100524/DI"
    tag = {"task": "task", "gateway": "exclusiveGateway", "parallel": "parallelGateway", "start": "startEvent",
           "end": "endEvent"}
    nodes = {n[0]: n for n in m["nodes"]}
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<bpmn:definitions xmlns:bpmn="%s" xmlns:bpmndi="%s" xmlns:dc="%s" xmlns:di="%s" '
           'id="defs_%s" targetNamespace="https://example.org/tanmark">' % (B, DI, DC, DDI, m["id"]),
           '  <bpmn:collaboration id="collab_%s"><bpmn:participant id="pool_%s" name="Tanmark Industries (fictional)" '
           'processRef="proc_%s"/></bpmn:collaboration>' % (m["id"], m["id"], m["id"]),
           '  <bpmn:process id="proc_%s" name="%s" isExecutable="false">' % (m["id"], html.escape(m["name"])),
           '    <bpmn:laneSet id="lanes_%s">' % m["id"]]
    for i, lane in enumerate(m["lanes"]):
        out.append('      <bpmn:lane id="lane_%s_%d" name="%s">' % (m["id"], i, html.escape(lane)))
        out += ['        <bpmn:flowNodeRef>%s</bpmn:flowNodeRef>' % n[0] for n in m["nodes"] if n[2] == i]
        out.append('      </bpmn:lane>')
    out.append('    </bpmn:laneSet>')
    for nid, kind, lane, col, label, changed in m["nodes"]:
        out.append('    <bpmn:%s id="%s" name="%s"/>' % (tag[kind], nid, html.escape(label)))
    for i, (a, b, label, *mode) in enumerate(m["flows"]):
        out.append('    <bpmn:sequenceFlow id="F%d" sourceRef="%s" targetRef="%s"%s/>'
                   % (i + 1, a, b, (' name="%s"' % html.escape(label)) if label else ""))
    out.append('  </bpmn:process>')
    width = LEFT + (max(n[3] for n in m["nodes"]) + 1) * COL_W + 20
    height = len(m["lanes"]) * LANE_H
    out.append('  <bpmndi:BPMNDiagram id="dia_%s"><bpmndi:BPMNPlane id="plane_%s" bpmnElement="collab_%s">'
               % (m["id"], m["id"], m["id"]))
    out.append('    <bpmndi:BPMNShape id="pool_%s_di" bpmnElement="pool_%s" isHorizontal="true"><dc:Bounds x="0" y="%d" '
               'width="%d" height="%d"/></bpmndi:BPMNShape>' % (m["id"], m["id"], TOP, width, height))
    for i in range(len(m["lanes"])):
        out.append('    <bpmndi:BPMNShape id="lane_%s_%d_di" bpmnElement="lane_%s_%d" isHorizontal="true">'
                   '<dc:Bounds x="30" y="%d" width="%d" height="%d"/></bpmndi:BPMNShape>'
                   % (m["id"], i, m["id"], i, TOP + i * LANE_H, width - 30, LANE_H))
    for nid, kind, lane, col, label, changed in m["nodes"]:
        x, y, w, h = box(kind, lane, col)
        out.append('    <bpmndi:BPMNShape id="%s_di" bpmnElement="%s"><dc:Bounds x="%d" y="%d" width="%d" height="%d"/>'
                   '</bpmndi:BPMNShape>' % (nid, nid, x, y, w, h))
    for i, (a, b, label, *mode) in enumerate(m["flows"]):
        pts = route(box(*nodes[a][1:4]), box(*nodes[b][1:4]), *mode)
        wp = "".join('<di:waypoint x="%d" y="%d"/>' % p for p in pts)
        out.append('    <bpmndi:BPMNEdge id="F%d_di" bpmnElement="F%d">%s</bpmndi:BPMNEdge>' % (i + 1, i + 1, wp))
    out.append('  </bpmndi:BPMNPlane></bpmndi:BPMNDiagram>')
    out.append('</bpmn:definitions>')
    return "\n".join(out) + "\n"


def wrap(text, n=18):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]


def svg(m):
    nodes = {n[0]: n for n in m["nodes"]}
    width = LEFT + (max(n[3] for n in m["nodes"]) + 1) * COL_W + 20
    height = TOP + len(m["lanes"]) * LANE_H + 60
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'font-family="IBM Plex Sans, Segoe UI, Arial, sans-serif" font-size="11">' % (width, height, width, height),
         '<rect width="100%%" height="100%%" fill="%s"/>' % C["paper"],
         '<defs><marker id="arr" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
         '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker></defs>' % C["ink"]]
    for i, lane in enumerate(m["lanes"]):
        y = TOP + i * LANE_H
        s.append('<rect x="0" y="%d" width="%d" height="%d" fill="%s" stroke="%s"/>'
                 % (y, width, LANE_H, C["lane"] if i % 2 == 0 else C["paper"], C["rule"]))
        s.append('<text x="12" y="%d" font-weight="600" fill="%s">%s</text>' % (y + 20, C["ink"], html.escape(lane)))
    for a, b, label, *mode in m["flows"]:
        pts = route(box(*nodes[a][1:4]), box(*nodes[b][1:4]), *mode)
        s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2" marker-end="url(#arr)"/>'
                 % (" ".join("%d,%d" % p for p in pts), C["ink"]))
        if label:
            lx, ly = label_at(pts)
            s.append('<text x="%d" y="%d" fill="%s" font-size="10">%s</text>' % (lx, ly, C["muted"], html.escape(label)))
    for nid, kind, lane, col, label, changed in m["nodes"]:
        x, y, w, h = box(kind, lane, col)
        cx, cy = x + w / 2, y + h / 2
        stroke = C["changed"] if changed else (C["gateway_stroke"] if kind in ("gateway", "parallel") else C["task_stroke"])
        sw = 2.2 if changed else 1.2
        if kind == "task":
            s.append('<rect x="%d" y="%d" width="%d" height="%d" rx="3" fill="%s" stroke="%s" stroke-width="%s"/>'
                     % (x, y, w, h, C["task"], stroke, sw))
            lines = wrap(label)
            for j, ln in enumerate(lines):
                s.append('<text x="%d" y="%d" text-anchor="middle" fill="%s">%s</text>'
                         % (cx, cy - (len(lines) - 1) * 6.5 + j * 13 + 4, C["ink"], html.escape(ln)))
            s.append('<text x="%d" y="%d" fill="%s" font-size="9">%s</text>' % (x + 4, y + 11, C["muted"], nid))
        elif kind in ("gateway", "parallel"):
            s.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="%s"/>'
                     % (cx, y, x + w, cy, cx, y + h, x, cy, C["gateway"], stroke, sw))
            if kind == "parallel":  # BPMN's parallel gateway: a plus inside the diamond
                s.append('<text x="%d" y="%d" text-anchor="middle" font-size="26" fill="%s">+</text>'
                         % (cx, cy + 9, C["ink"]))
            glines = wrap(label, 20)
            for j, ln in enumerate(glines):
                s.append('<text x="%d" y="%d" text-anchor="end" fill="%s" font-size="10">%s</text>'
                         % (cx - 8, y - 4 - (len(glines) - 1 - j) * 11, C["ink"], html.escape(ln)))
        else:
            s.append('<circle cx="%d" cy="%d" r="18" fill="%s" stroke="%s" stroke-width="%s"/>'
                     % (cx, cy, C["paper"], stroke, 3.5 if kind == "end" else 1.5))
            for j, ln in enumerate(wrap(label, 16)):
                s.append('<text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="10">%s</text>'
                         % (cx, y + h + 12 + j * 11, C["ink"], html.escape(ln)))
    key = " Bold ochre outline: a step added or changed by the new system." if any(n[5] for n in m["nodes"]) else ""
    s.append('<text x="12" y="%d" fill="%s" font-size="10">%s. Tanmark Industries is fictional.%s</text>'
             % (height - 12, C["muted"], html.escape(m["name"]), key))
    s.append('</svg>')
    return "\n".join(s) + "\n"


def check(path, m):
    root = ET.parse(path).getroot()
    ns = {"b": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
    ids = {e.get("id") for e in root.iter() if e.get("id")}
    flows = root.findall(".//b:sequenceFlow", ns)
    bad = [f.get("id") for f in flows if f.get("sourceRef") not in ids or f.get("targetRef") not in ids]
    refs = [r.text for r in root.findall(".//b:flowNodeRef", ns)]
    one_lane = all(refs.count(n[0]) == 1 for n in m["nodes"]) and len(refs) == len(m["nodes"])
    return bad, one_lane


def rules(m):
    """The business rules the stories imply, checked on the flow graph. Returns a list of problems."""
    nodes = {n[0]: n for n in m["nodes"]}
    out = {}
    for a, b, *_ in m["flows"]:
        out.setdefault(a, []).append(b)
    problems = [g for g in nodes if nodes[g][1] in ("gateway", "parallel") and len(out.get(g, [])) < 2]
    problems = ["gateway %s has fewer than two exits" % g for g in problems]
    rule = m.get("rules", {})

    def paths(src, dst, avoid, seen=()):
        if src == dst:
            return True
        return any(paths(n, dst, avoid, seen + (src,)) for n in out.get(src, [])
                   if n not in seen and n != avoid)
    must = rule.get("must_pass", [])
    for via, start, end in ([must] if must and isinstance(must, tuple) else must):
        if paths(start, end, via):
            problems.append("a path from %s to %s skips %s" % (start, end, via))
    if "must_refuse" in rule:
        task, pay_end = rule["must_refuse"]
        ends = [n for n in nodes if nodes[n][1] == "end" and n != pay_end]
        if not any(paths(task, e, None) for e in ends):
            problems.append("%s has no way to end without payment" % task)
    # the map and the state model are one truth: each task that moves a document names a move the model allows
    allowed = model_moves()
    for tid, move in m.get("moves", {}).items():
        if tid not in nodes:
            problems.append("move declared for %s, which is not on the map" % tid)
        elif allowed is not None and tuple(move) not in allowed:
            problems.append("%s claims %s, which the state model does not allow" % (tid, " | ".join(move)))
    return problems


def model_moves():
    """The allowed moves in state/transitions.csv, or None when the model has not been built."""
    import csv
    path = os.path.join(HERE, "..", "state", "transitions.csv")
    if not os.path.exists(path):
        return None
    return {(r["document"], r["from"], r["event"]) for r in csv.DictReader(io.open(path, encoding="utf-8"))
            if r["kind"] == "allowed"}


def main():
    # [CONTROL] v2-shaped defects on a copy of the after map: a shortcut to completion that skips delivery, and a task
    # claiming a move the state model does not have. Both must be refused before the real maps are judged.
    bad = dict(AFTER, flows=AFTER["flows"] + [("G1", "P2", "shortcut")],
               moves=dict(AFTER["moves"], T8=("sales-order", "In production", "skip ahead")))
    caught = rules(bad)
    print("[CONTROL] a planted shortcut and a planted move are refused: %s" % caught)
    if not (any("skips T10" in c for c in caught) and any("skip ahead" in c for c in caught)):
        raise SystemExit(3)
    for m in (BEFORE, AFTER, PERIODIC):
        for ext, fn in (("bpmn", bpmn), ("svg", svg)):
            p = os.path.join(HERE, "%s.%s" % (m["id"], ext))
            io.open(p, "w", encoding="utf-8", newline="\n").write(fn(m))
        bad, one_lane = check(os.path.join(HERE, m["id"] + ".bpmn"), m)
        print("%-6s nodes %2d flows %2d . [CONTROL] dangling flows %s . every node in one lane %s"
              % (m["id"], len(m["nodes"]), len(m["flows"]), bad or "none", one_lane))
        problems = rules(m)
        print("       [RULES] %s" % ("; ".join(problems) if problems else "every gateway has two exits; every declared rule holds"))
        if problems:
            raise SystemExit(3)
        png = to_png(os.path.join(HERE, m["id"] + ".svg"),
                     os.path.join(HERE, "..", "docs", "img", "process-%s.png" % m["id"]))
        print("       png for the report: %s" % png)


def to_png(svg_path, png_path):
    """Render the SVG at 2x with headless Edge, for documents that cannot embed SVG. Skipped if Edge is absent."""
    import re
    import subprocess
    edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge):
        return "skipped, Edge not found"
    w, h = re.search(r'width="(\d+)" height="(\d+)"', io.open(svg_path, encoding="utf-8").read(400)).groups()
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    subprocess.run([edge, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=%s,%s" % (w, h), "--screenshot=%s" % os.path.abspath(png_path),
                    "file:///" + os.path.abspath(svg_path).replace(os.sep, "/")], capture_output=True)
    return "%s (%d bytes)" % (os.path.basename(png_path), os.path.getsize(png_path)) if os.path.exists(png_path) else "FAILED"


if __name__ == "__main__":
    main()
