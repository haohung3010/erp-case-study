# -*- coding: utf-8 -*-
"""figures.py -- every number and every figure the case study quotes, computed from the synthetic dataset.

PURPOSE
  The README, the report, the cutover plan and the deck quote numbers. They read them from docs/numbers.json, which
  this script writes, so the four can never disagree and every number traces to data/*.csv.

CONFIG
  argv[1]  the repository root. Needs pandas and matplotlib. Style: docs/portfolio.mplstyle (the portfolio's charts
           design, copied here so the repository stands alone).

WORKFLOW
  1 read data/*.csv (first line is the illustrative-data comment)
  2 compute the numbers; write docs/numbers.json (values already formatted as they are quoted)
  3 draw four figures to docs/img/: cycle-time.png, receivables.png, rework.png, pilot-adoption.png; each title states the finding and
    each carries a source line naming the synthetic dataset
  4 [CONTROL] recompute the lead-time median and the overdue share from the raw rows without pandas; every figure file
    is non-empty
  rc 0 ok . 2 usage . 3 a control failed

NOTES
  Tanmark Industries is fictional; every number here is illustrative.
"""
import csv
import io
import json
import os
import statistics
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SOURCE = "Source: synthetic dataset, data/generate_dataset.py (seed 20260929). Illustrative, not measured."
TEAL, OCHRE, CONTEXT = "#1D5C6B", "#906915", "#5B6B73"


def load(root, name):
    return pd.read_csv(os.path.join(root, "data", name), comment="#")


def numbers(root):
    c = load(root, "cycle_time.csv")
    r = load(root, "rework.csv")
    a = load(root, "pilot_adoption.csv")
    q = load(root, "orders_by_month.csv")
    k = load(root, "receivables.csv")
    med = c.groupby("period").days_order_to_delivery.median()
    od = k.groupby("period").overdue_share.mean()
    dso = k.groupby("period").dso_days.mean()
    rw = r.groupby("period")[["rework_rate", "order_error_rate"]].mean()
    full = a[a.weekly_active_users >= a.pilot_group_size].pilot_week.min()
    runs_ = []  # the longest run of equal weekly counts below the full group: (count, first week, last week)
    for u, grp in a[a.weekly_active_users < a.pilot_group_size].groupby("weekly_active_users"):
        if len(grp) > 1 and grp.pilot_week.diff().fillna(1).eq(1).all():
            runs_.append((len(grp), u, grp.pilot_week.min(), grp.pilot_week.max()))
    plateau = max(runs_)[1:] if runs_ else (0, 0, 0)
    per_month = q.groupby("period").orders.sum() / q.groupby("period").month_from_golive.nunique()
    n = {
        "lead_before_days": "%.1f" % med["before"],
        "lead_after_days": "%.1f" % med["after"],
        "lead_pilot_days": "%.1f" % med["pilot"],
        "lead_change_pct": "%d" % round(100 * (med["before"] - med["after"]) / med["before"]),
        "invoice_lag_before_days": "%.1f" % c[c.period == "before"].days_delivery_to_invoice.median(),
        "invoice_lag_after_days": "%.1f" % c[c.period != "before"].days_delivery_to_invoice.max(),
        "overdue_before_pct": "%d" % round(100 * od["before"]),
        "overdue_pilot_pct": "%d" % round(100 * od["pilot"]),
        "overdue_after_pct": "%d" % round(100 * od["after"]),
        "dso_before_days": "%d" % round(dso["before"]),
        "dso_after_days": "%d" % round(dso["after"]),
        "orders_before_n": "%d" % (c.period == "before").sum(),
        "orders_after_n": "%d" % (c.period == "after").sum(),
        "orders_pilot_n": "%d" % (c.period == "pilot").sum(),
        "rework_before_pct": "%.1f" % (100 * rw.loc["before", "rework_rate"]),
        "rework_after_pct": "%.1f" % (100 * rw.loc["after", "rework_rate"]),
        "errors_before_pct": "%.1f" % (100 * rw.loc["before", "order_error_rate"]),
        "errors_after_pct": "%.1f" % (100 * rw.loc["after", "order_error_rate"]),
        "pilot_size": "%d" % a.pilot_group_size.iloc[0],
        "pilot_weeks": "%d" % a.pilot_week.max(),
        "pilot_full_week": "%d" % full,
        "pilot_week4_active": "%d" % a.loc[a.pilot_week == 4, "weekly_active_users"].iloc[0],
        "orders_per_month": "%d" % round(per_month.mean(), -1),
        "departments": "%d" % q.department.nunique(),
        "rework_golive_pct": "%.1f" % (100 * r.loc[r.month_from_golive == 0, "rework_rate"].iloc[0]),
        "rework_late_peak_pct": "%.1f" % (100 * r[r.month_from_golive >= 3].rework_rate.max()),
        "rework_late_peak_month": "%d" % r.loc[r[r.month_from_golive >= 3].rework_rate.idxmax(), "month_from_golive"],
        "pilot_plateau_active": "%d" % plateau[0],
        "pilot_plateau_from": "%d" % plateau[1],
        "pilot_plateau_to": "%d" % plateau[2],
        "months_before": "%d" % (q[q.period == "before"].month_from_golive.nunique()),
        "months_after": "%d" % (q[q.period != "before"].month_from_golive.nunique()),
    }
    return n, c, r, a, k


def fig_cycle(c, n, path):
    fig, ax = plt.subplots(figsize=(6, 3.2))
    order = ["before", "pilot", "after"]
    data = [c[c.period == p].days_order_to_delivery for p in order]
    bp = ax.boxplot(data, vert=False, widths=0.55, patch_artist=True, showfliers=False,
                    medianprops={"color": "#16232B", "linewidth": 1.6})
    for patch, col in zip(bp["boxes"], [CONTEXT, CONTEXT, TEAL]):
        patch.set_facecolor(col)
        patch.set_alpha(0.35 if col == CONTEXT else 0.6)
        patch.set_edgecolor(col)
    ax.set_yticks([1, 2, 3], ["Before\n(paper)", "Pilot\n(%s weeks)" % n["pilot_weeks"], "After\n(one system)"])
    for i, p in enumerate(order, 1):
        m = c[c.period == p].days_order_to_delivery.median()
        ax.annotate("median %.1f" % m, (m, i + 0.36), ha="center", fontsize=8, color="#16232B")
    ax.set_xlabel("Days from order to delivery")
    ax.grid(axis="x", color="#E3E9EB")
    ax.grid(axis="y", visible=False)
    ax.set_title("Orders reached customers in %s days, down from %s (median)" % (n["lead_after_days"], n["lead_before_days"]))
    fig.text(0.01, 0.01, SOURCE + " Denominator: %s, %s and %s orders." % (
        n["orders_before_n"], n["orders_pilot_n"], n["orders_after_n"]), fontsize=6.5, color=CONTEXT)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def fig_receivables(k, n, path):
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.plot(k.month_from_golive, 100 * k.overdue_share, color=TEAL, linewidth=1.8)
    ax.axvspan(2, 3, color=CONTEXT, alpha=0.12, linewidth=0)  # the parallel-run month
    ax.annotate("parallel run", (2.5, 46), ha="center", fontsize=8, color=CONTEXT)
    for x, label in [(0, "pilot"), (3, "the system is the record")]:
        ax.axvline(x, color=CONTEXT, linestyle="--", linewidth=1)
        ax.annotate(label, (x, 2), xytext=(4, 0), textcoords="offset points", fontsize=8, color=CONTEXT)
    ax.set_ylim(0, 50)
    ax.set_xlim(k.month_from_golive.min(), k.month_from_golive.max() + 1)
    ax.set_xlabel("Months from pilot go-live")
    ax.set_ylabel("% of receivables past due")
    ax.set_title("Overdue receivables fell to %s%% of the balance, from %s%%" % (n["overdue_after_pct"], n["overdue_before_pct"]))
    fig.text(0.01, 0.01, SOURCE + " Denominator: open receivables at each month end.", fontsize=6.5, color=CONTEXT)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def fig_rework(r, n, path):
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.plot(r.month_from_golive, 100 * r.rework_rate, color=TEAL, linewidth=1.8)
    ax.plot(r.month_from_golive, 100 * r.order_error_rate, color=OCHRE, linewidth=1.8)
    last = r.iloc[-1]
    ax.annotate("rework", (last.month_from_golive, 100 * last.rework_rate), xytext=(5, 0),
                textcoords="offset points", color=TEAL, fontsize=8, va="center")
    ax.annotate("order errors", (last.month_from_golive, 100 * last.order_error_rate), xytext=(5, 0),
                textcoords="offset points", color=OCHRE, fontsize=8, va="center")
    ax.axvline(0, color=CONTEXT, linestyle="--", linewidth=1)
    ax.annotate("pilot go-live", (0, ax.get_ylim()[1]), xytext=(4, -10), textcoords="offset points", fontsize=8,
                color=CONTEXT)
    ax.set_ylim(bottom=0)
    ax.set_xlim(r.month_from_golive.min(), r.month_from_golive.max() + 3)
    ax.set_xlabel("Months from pilot go-live")
    ax.set_ylabel("% of orders")
    ax.set_title("Monthly rework averaged %s%% after pilot go-live, down from %s%%" % (n["rework_after_pct"], n["rework_before_pct"]))
    fig.text(0.01, 0.01, SOURCE + " Denominator: orders raised each month.", fontsize=6.5, color=CONTEXT)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def fig_adoption(a, n, path):
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.bar(a.pilot_week, a.weekly_active_users, color=[TEAL if u >= s else CONTEXT for u, s in
                                                       zip(a.weekly_active_users, a.pilot_group_size)], width=0.7)
    ax.set_axisbelow(True)
    ax.axhline(int(n["pilot_size"]), color=OCHRE, linestyle="--", linewidth=1)
    ax.annotate("pilot group, %s people" % n["pilot_size"], (0.6, int(n["pilot_size"])), xytext=(0, 4),
                textcoords="offset points", color=OCHRE, fontsize=8)
    ax.set_ylim(0, int(n["pilot_size"]) + 5)
    ax.set_xticks(a.pilot_week)
    ax.set_xlabel("Pilot week")
    ax.set_ylabel("People active that week")
    ax.set_title("The whole pilot group was using it by week %s" % n["pilot_full_week"])
    fig.text(0.01, 0.01, SOURCE + " Denominator: the %s-person pilot group." % n["pilot_size"], fontsize=6.5,
             color=CONTEXT)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = argv[1]
    plt.style.use(os.path.join(root, "docs", "portfolio.mplstyle"))
    plt.rcParams["font.sans-serif"] = ["IBM Plex Sans", "Calibri", "Segoe UI", "Arial"]
    n, c, r, a, k = numbers(root)
    with io.open(os.path.join(root, "docs", "numbers.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(n, f, indent=1)
        f.write("\n")
    img = os.path.join(root, "docs", "img")
    os.makedirs(img, exist_ok=True)
    fig_cycle(c, n, os.path.join(img, "cycle-time.png"))
    fig_receivables(k, n, os.path.join(img, "receivables.png"))
    fig_rework(r, n, os.path.join(img, "rework.png"))
    fig_adoption(a, n, os.path.join(img, "pilot-adoption.png"))
    # [CONTROL] the median, recomputed from the raw rows with the standard library
    rows = [x for x in csv.reader(io.open(os.path.join(root, "data", "cycle_time.csv"), encoding="utf-8"))
            if x and not x[0].startswith("#")][1:]
    raw = "%.1f" % statistics.median(float(x[2]) for x in rows if x[1] == "before")
    ok = raw == n["lead_before_days"]
    print("[CONTROL] before lead-time median, pandas %s . stdlib %s -> %s" % (n["lead_before_days"], raw, "agree" if ok else "DIFFER"))
    rec = [x for x in csv.reader(io.open(os.path.join(root, "data", "receivables.csv"), encoding="utf-8"))
           if x and not x[0].startswith("#")][1:]
    raw_od = "%d" % round(100 * statistics.mean(float(x[2]) for x in rec if x[1] == "after"))
    ok = ok and raw_od == n["overdue_after_pct"]
    print("[CONTROL] after overdue share, pandas %s . stdlib %s -> %s" % (n["overdue_after_pct"], raw_od, "agree" if raw_od == n["overdue_after_pct"] else "DIFFER"))
    sizes = {f: os.path.getsize(os.path.join(img, f)) for f in sorted(os.listdir(img))}
    print("figures", sizes)
    ok = ok and all(v > 10_000 for v in sizes.values())
    print("numbers", json.dumps(n))
    print("[RESULT] %s" % ("ok" if ok else "REFUSED"))
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
