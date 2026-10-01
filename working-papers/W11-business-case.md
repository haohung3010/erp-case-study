# W11. Business case

**Tanmark Industries is fictional. Every number here is illustrative.** Benefits come from the synthetic dataset in
`data/`; costs are stated assumptions.

## The need

Orders took a median of 24.0 days from order to delivery, 34% of receivables were past
due, and 17.5% of orders needed rework each month. Nobody could see where an order was, and the ledger could not be audited: vouchers were edited and
deleted after the fact.

## Options considered

| Option | For | Against | Decision |
|---|---|---|---|
| A. Keep paper, add a shared spreadsheet | cheapest; no training | the same re-keying; no states, no audit trail | rejected |
| B. Separate tools per department, linked by nightly files | each department picks its tool | traceability depends on exports no one owns (D1) | rejected |
| C. One system, one data model, piloted before cutover | traceable, auditable, one source for reports | slower first release; training for every role | **chosen** |

## Benefits, measured against the objectives (illustrative, from the synthetic dataset)

| Objective | Before | After | Source |
|---|---|---|---|
| O3 Orders are delivered faster (median days, order to delivery) | 24.0 | 17.8 | `data/cycle_time.csv` |
| O3 Receivables collected on their terms (share past due) | 34% | 18% | `data/receivables.csv` |
| O3 Days sales outstanding, against 30-day terms | 57 | 41 | `data/receivables.csv` |
| O1 and O2, less rework (share of orders, monthly average) | 17.5% | 9.8% | `data/rework.csv` |
| O2 Fewer order errors (share of orders, monthly average) | 9.7% | 4.9% | `data/rework.csv` |
| O4 The ledger can be audited | edits and deletes | posted vouchers locked; no deletes | the state model (R1, R2) |

## Costs (illustrative assumptions, not from the dataset)

| Item | Assumption |
|---|---|
| Build | a product owner and a team of six developers for one year |
| Rollout | a two-month pilot, then one month of parallel running in every department (D12); a superuser in each of ten departments |
| Training | one hour per role before each department joins, plus shift sessions |
| Run | hosting, support and one developer's time after go-live |

## Benefits that are not in the numbers

* **Audit readiness.** A voucher sequence with no gaps (N4) and an audit trail of every state change (N1).
* **Fewer arguments.** A document's state answers "where is it?" without a phone call (O1).
* **A foundation for reporting.** One data model means every later report reads one source (D1).

## Recommendation

Option C, with a pilot group first (D2) and go / no-go criteria before each phase. Review the benefits after twelve months,
against the same measures.
