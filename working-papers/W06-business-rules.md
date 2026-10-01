# W6. Business rules and a decision table

**Tanmark Industries is fictional.** Rules are kept apart from process: the maps say what happens next; the rules say what must always hold
and what a decision depends on.

## Structural rules (always true)

The ten rules R1 to R10 live in `state/state-model.md`, where each is enforced as a refused move. They are not repeated
here, so there is one place to change them.

## Operative rules (who may do what, when)

| ID | Rule | Owner | Enforced as |
|---|---|---|---|
| B1 | A request becomes an order only when sales confirms it | Sales lead | transition Request to Open |
| B2 | An order is fulfilled from stock when enough finished goods are free; otherwise a material request is raised | Logistics manager | the first decision on the after map |
| B3 | A purchase order is signed on paper by the logistics manager | Logistics manager | a paper control, outside the system (D9) |
| B4 | The warehouse issues a trip exactly its planned quantity | Logistics manager | refused move on the delivery trip |
| B5 | An invoice is corrected by a credit note, never by editing it | Chief accountant | refused move on the sales invoice |
| B6 | A posted voucher is corrected by a reversing voucher, with a reason | Chief accountant | transition Posted to Reversed |
| B7 | Each trip carries one invoice, raised after the goods are issued and before the trip leaves | Chief accountant | refused move on the delivery trip (R9, D16) |
| B8 | Payment terms and a credit limit are set per customer and contract: 30 days unless the contract says otherwise | Chief accountant, with sales | the due date on every invoice (R10, D17) |
| B9 | A contract over its credit limit or overdue gets no new order unless the chief accountant releases that order, with a reason | Chief accountant | refused move on the sales order (R10, D17) |
| B10 | A customer's transfer is allocated to its invoices, oldest due date first | Chief accountant | the allocation on the receipt voucher (D17) |
| B11 | Receivables are reconciled with every customer each quarter, on a statement the customer signs | Chief accountant | the quarterly statement and its signed copy (D17) |
| B12 | Stock is reconciled between the warehouse and accounting each month | Chief accountant, with the warehouse lead | the monthly stock reconciliation (D17) |

## Decision table: which combinations of the three sale statuses are legal (D8)

Each status can be none, part or all, so twenty-seven combinations are possible on paper. In this business they form
one sequence: a trip leaves only with its invoice (D16, R9), and customers pay on credit terms after delivery (D17,
R10). **So a sale is never more delivered than invoiced, and never more paid than delivered.** That leaves ten legal
combinations. Finance ruled them. **Hit policy: unique** (exactly one row applies to any sale).

| Invoiced | Delivered | Paid | Legal? | What it means | Ruled by |
|---|---|---|---|---|---|
| none | none | none | yes | a new sale | finance lead |
| part | none | none | yes | the first trip is invoiced and issued, not yet delivered | finance lead |
| part | part | none | yes | the first trip is delivered; its invoice runs on the contract's terms | finance lead |
| part | part | part | yes | the first trip's invoice is being paid | finance lead |
| all | none | none | yes | every trip is invoiced; all are still in transit | finance lead |
| all | part | none | yes | some trips delivered, none paid yet | finance lead |
| all | part | part | yes | some trips delivered, the earliest being paid | finance lead |
| all | all | none | yes | **the normal waiting state: delivered on credit, due within the terms** | finance lead |
| all | all | part | yes | being paid, often across several transfers | finance lead |
| all | all | all | yes | complete | finance lead |
| any combination where delivered is ahead of invoiced | | | **no: refused** | a trip cannot leave without its invoice (R9) | finance lead |
| any combination where paid is ahead of delivered | | | **no: flagged** | money for goods not yet delivered; held unallocated and flagged to finance | finance lead |

"Ahead" is checked on amounts, not on the words: the amount delivered may not exceed the amount invoiced, and the
amount allocated may not exceed the invoices of delivered trips. A receipt that would break the second is held as
unallocated cash, not refused, because the money has already arrived.

**Why this table matters.** D8 specified the statuses and left the legal combinations to finance. The first draft
treated the three as independent and listed prepayment and "delivered, invoice to follow" as legal; in this business
neither happens. Without the table, the build could reach "delivered, not invoiced" by a route nobody sanctioned, and
no one would notice until the quarter's statements went out.
