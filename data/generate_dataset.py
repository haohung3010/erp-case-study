# -*- coding: utf-8 -*-
"""generate_dataset.py -- the illustrative dataset for the Tanmark Industries case study.

PURPOSE
  Every number in the case study comes from here, so a reader can regenerate it and see it is illustrative.
  Nothing here is measured data.

CONFIG
  Run from anywhere: python data/generate_dataset.py . Writes CSVs beside this script. Standard library only.
  SEED fixes the output; change it and every file changes together.

WORKFLOW
  1 orders_by_month.csv    orders per department per month, 12 months before and 12 after pilot go-live
  2 cycle_time.csv         order-to-delivery days per order, before, pilot, after; and days from delivery to invoice
  3 rework.csv             monthly rework and error rates in the manual process and after
  4 pilot_adoption.csv     weekly active users in the pilot group, 8 weeks (a two-month pilot)
  5 receivables.csv        monthly share of receivables overdue and days sales outstanding, 12 months before and 12 after
  6 read back each file and print its row count

Q&A
  Q: why modest effects?   A: a case study with miracle numbers reads as a toy. Lead time falls about a quarter,
                              with variance, a slow pilot month and a few bad weeks.
  Q: why a second random stream?   A: the order-to-delivery rows draw exactly as many numbers as the earlier
                              order-to-payment rows did, so rework.csv and pilot_adoption.csv are unchanged. The new
                              columns and receivables.csv draw from SEED + 1.

PITFALLS
  The first line of every CSV is a comment saying the data is illustrative; readers must skip it (comment="#").

NOTES
  Illustrative, from the synthetic dataset; not measured data.
"""
import csv
import io
import os
import random

SEED = 20260929
HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = "# Illustrative, from the synthetic dataset of a fictional company; not measured data."
DEPTS = ["Director's office", "Product sales", "Technical management", "Production",
         "Warehouse", "Logistics and purchasing", "Price control", "Service sales", "Accounting",
         "Human resources"]
BASE = [4, 18, 22, 60, 35, 12, 9, 30, 6, 5]


def write(name, header, rows):
    path = os.path.join(HERE, name)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(NOTE + "\n")
        w = csv.writer(f, lineterminator=chr(10))
        w.writerow(header)
        w.writerows(rows)
    n = sum(1 for line in io.open(path, encoding="utf-8")) - 2
    assert n == len(rows), (name, n, len(rows))
    print("%-22s %4d rows" % (name, n))


def main():
    rnd = random.Random(SEED)
    rows = []
    for m in range(-12, 12):
        period = "before" if m < 0 else "after"
        for d, b in zip(DEPTS, BASE):
            rows.append([m, period, d, max(0, round(rnd.gauss(b, b * 0.15)))])
    write("orders_by_month.csv", ["month_from_golive", "period", "department", "orders"], rows)

    rnd2 = random.Random(SEED + 1)  # the new columns and files; rnd keeps its old sequence (see Q&A)
    rows = []
    for i in range(300):  # before: invoices were keyed after the truck had gone
        rows.append([i + 1, "before", round(max(8, rnd.gauss(24, 6)), 1), round(max(0.5, rnd2.gauss(4, 2.5)), 1)])
    for i in range(80):  # pilot and after: the invoice leaves with the goods (D16), so the gap is zero
        rows.append([i + 301, "pilot", round(max(7, rnd.gauss(21.5, 6.5)), 1), 0.0])
    for i in range(300):
        slow = rnd.random() < 0.08
        rows.append([i + 381, "after", round(max(6, rnd.gauss(23 if slow else 17.5, 4)), 1), 0.0])
    write("cycle_time.csv", ["order_id", "period", "days_order_to_delivery", "days_delivery_to_invoice"], rows)

    rows = []
    for m in range(-12, 12):
        if m < 0:
            rework, errors = rnd.gauss(0.17, 0.03), rnd.gauss(0.09, 0.02)
        elif m < 3:
            rework, errors = rnd.gauss(0.14, 0.03), rnd.gauss(0.08, 0.02)
        else:
            rework, errors = rnd.gauss(0.08, 0.02), rnd.gauss(0.04, 0.01)
        rows.append([m, "before" if m < 0 else "after", round(max(0, rework), 3), round(max(0, errors), 3)])
    write("rework.csv", ["month_from_golive", "period", "rework_rate", "order_error_rate"], rows)

    rows, users = [], 0
    for wk in range(1, 9):  # a two-month pilot; the two night-shift receivers join after their shift session
        target = 22 if wk < 7 else 24
        users = min(target, users + max(0, round(rnd.gauss(5, 1.5))))
        if wk == 3:
            users = max(0, users - 3)
        rows.append([wk, users, 24])
    write("pilot_adoption.csv", ["pilot_week", "weekly_active_users", "pilot_group_size"], rows)

    rows = []  # open receivables at month end: share past due, and days sales outstanding (terms are 30 days)
    for m in range(-12, 12):
        if m < 3:  # before, the pilot and the parallel-run month: collection only just moving off paper
            overdue, dso = rnd2.gauss(0.34, 0.03), rnd2.gauss(57, 4)
        else:  # from the end of the parallel run: ageing, allocation and the credit hold (D17)
            overdue, dso = rnd2.gauss(0.17, 0.03), rnd2.gauss(41, 3)
        period = "before" if m < 0 else ("pilot" if m < 2 else ("parallel" if m < 3 else "after"))
        rows.append([m, period, round(max(0.02, overdue), 3), round(max(30, dso), 1)])
    write("receivables.csv", ["month_from_golive", "period", "overdue_share", "dso_days"], rows)


if __name__ == "__main__":
    main()
