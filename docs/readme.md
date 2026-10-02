# How does a ten-department manufacturer move order to cash, purchasing and accounting from paper onto one system?

**TL;DR.** A product owner case study of Tanmark Industries, a **fictional** maker of truck-mounted tanks, drums and containers, built on real design patterns from order-processing and accounting systems. Every order, purchase and voucher got a lifecycle with named states and moves the system refuses. Customers buy on 30-day credit terms, so the case covers receivables too. In the synthetic data, the median order reached its customer in {{lead_after_days}} days, down from {{lead_before_days}}, and overdue receivables fell from {{overdue_before_pct}}% of the balance to {{overdue_after_pct}}%.

![State diagram of the sales order: a request becomes an order when confirmed, moves forward only, can be cancelled only before production, and after that closes as Not completed.](docs/img/state-sales-order.png)

## The question, and who asks it

A BA, implementation or product-owner panel asks how a candidate would take a business off paper without stopping it, and what they would do about the rules nobody wrote down. This repository answers with one system, from discovery to sign-off.

**The company is fictional, and every timing and rate here is illustrative.** One outcome is real. The system this case study is modelled on is used by 50 to 100 people. It replaced hand record keeping, manual warehouse checks and manual order processing.

## The problem

Orders arrived by phone and email and were written on paper. Stock was checked by walking the shelves. Purchases went out by email, and invoices were keyed and matched by hand, sometimes after the truck had gone. Overdue customers were found only at the quarter-end statements. Orders were "cancelled" after materials had gone to the workshop, and vouchers were edited and deleted after posting. Nobody could see where an order was.

## What changed

| Before | After |
|---|---|
| A paper order form | An order request, confirmed into an order that moves forward through named states |
| Changes at any time, by anyone | Sales locked out at the handoff to logistics; a transition table says who may move each document |
| "Cancelled" at any stage | Cancelled only before production; Not completed after, with received stock kept |
| Vouchers edited or deleted | Saved, then posted and locked; corrections are reversing vouchers; nothing is deleted |
| Invoices keyed after delivery | One invoice per trip, raised before the trip may leave |
| Payment terms in a binder | Terms and a credit limit on each contract; an ageing view; a credit hold the chief accountant releases |

Three of the seventeen decisions in the [decision log](decisions/decision-log.md):

* **D17, a credit hold someone owns.** A customer over its limit or overdue gets no new order unless the chief accountant releases it, with a reason. A warning sales could click past was rejected.
* **D9, purchase approval stays on paper.** An in-app approval would have duplicated a signature the buyers already had. The trade-off is stated.
* **D10, save is not post.** A posted voucher never changes, and no document is ever deleted, by any role.

The role had a boundary: buyers, finance and the sales and logistics leads made the business's decisions, and the product owner made them enforceable. The [RACI](raci/raci.xlsx) checks it row by row.

## What is in the repository

| Deliverable | File |
|---|---|
| Case-study report | [docs/case-study-report.pdf](docs/case-study-report.pdf) |
| **Software requirements specification**: 79 requirements, each with a statement, rationale, acceptance criteria and verification method | [srs/srs.md](srs/srs.md) |
| **State model**: diagrams, transitions, refused moves, rules | [state/state-model.md](state/state-model.md) |
| Decision log, seventeen decisions | [decisions/decision-log.md](decisions/decision-log.md) |
| Process maps, before and after, and the periodic routines (BPMN 2.0) | [process/before.bpmn](process/before.bpmn), [process/after.bpmn](process/after.bpmn), [process/periodic.bpmn](process/periodic.bpmn) |
| Eight user stories, 54 Gherkin scenarios | [stories/](stories/) |
| UAT script with traceability and business sign-off | [uat/uat-script.xlsx](uat/uat-script.xlsx) |
| Readiness and cutover plan, one page | [docs/cutover-plan.pdf](docs/cutover-plan.pdf) |
| RACI across ten departments | [raci/raci.xlsx](raci/raci.xlsx) |
| Ten-minute interview deck | [deck/interview-deck.pptx](deck/interview-deck.pptx) |
| **Thirteen BA and PM working papers** | [working-papers/](working-papers/README.md) |

## Data

| File | What it holds | Rows |
|---|---|---|
| `data/cycle_time.csv` | Days from order to delivery, and from delivery to invoice, per order | {{orders_before_n}} before, {{orders_pilot_n}} pilot, {{orders_after_n}} after |
| `data/rework.csv` | Monthly rework and order error rates | {{months_before}} months before, {{months_after}} after |
| `data/pilot_adoption.csv` | Weekly active users in the pilot group | {{pilot_weeks}} weeks |
| `data/receivables.csv` | Monthly share of receivables overdue, and days sales outstanding | {{months_before}} months before, {{months_after}} after |
| `data/orders_by_month.csv` | Orders per department per month | 24 months, {{departments}} departments |

All five are synthetic, generated by `data/generate_dataset.py` with a fixed seed.

## How it was built

Discovery first, then the state model, then everything that depends on it. Every error path in the stories is a move the model refuses, and the build checks that. Tools: Python (pandas, matplotlib, openpyxl, python-docx, python-pptx), Cucumber's Gherkin parser, BPMN 2.0, Mermaid, ONLYOFFICE for PDF.

## How to reproduce

```
python data/generate_dataset.py
python state/model.py .
python process/build_maps.py
python uat/build_uat.py .
python raci/build_raci.py .
python working-papers/build_rtm.py .
python srs/build_srs.py .
python docs/figures.py .
python scripts/build_docs.py .
python deck/build_deck.py .
```

Each script runs its own checks and refuses to write when one fails.

## Limits

* The company, its people and every number are synthetic. The design patterns are real; no client, product, code or data appears here.
* One outcome is real: 50 to 100 users of the system this is modelled on. No real before-and-after timings exist, so none are claimed.
* The maps were drawn by `process/build_maps.py`, not by a BPMN editor. The files are standard BPMN 2.0 and open in bpmn.io.
