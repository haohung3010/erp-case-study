# W9. Prioritised backlog and change requests

**Tanmark Industries is fictional. Items and sizes are illustrative.**

## Backlog at the start of the pilot (MoSCoW)

The product owner ordered the backlog (RACI S2) and reviewed the roadmap with the executive sponsor each week. **Must** means the pilot cannot start without it.

| Epic | Stories | Priority | Why |
|---|---|---|---|
| Order lifecycle and lock on handoff | order-lifecycle | Must | the pilot's first process; D5, D7 |
| Order closure | order-closure | Must | without it, stock is orphaned (D6) |
| Delivery trips | delivery-trip | Must | shipping is half the pilot |
| Invoice per trip | receivables (raise) | Must | a trip cannot leave without its invoice (R9) |
| Purchase orders and receipts | purchase-order | Must | the workshop needs materials |
| Material requests and issues | material-request | Must | the workshop builds from issued materials (R3, R8) |
| Save, post and reverse vouchers | voucher-posting | Should for the pilot, **Must for the parallel run** | finance joins in the parallel run (the report's section 9) |
| Receivables: terms, ageing, allocation, credit hold | receivables | Should for the pilot, **Must for the parallel run** | collection stays on paper in the pilot; finance owns it from the parallel run (D17) |
| Three sale statuses | sale-statuses | Should | reports need it; they roll up from trips and invoices |
| Supplier invoice matching | not written yet | Could | a manual check works at pilot volume |
| Customer portal | none | Won't, this release | out of scope (W1) |

## Change requests, each assessed before a decision

| CR | Asked by | Request | Assessment | Decision |
|---|---|---|---|---|
| CR-1 | Sales lead | Let sales edit the price after handoff | Breaks R6 and D7: logistics would plan against a moving order. The need behind it is a late discount, which a credit note already covers | **Rejected**, with the alternative written into the sales training |
| CR-2 | Chief accountant | Add an in-app approval to purchase orders | Reopens D9. Duplicates the paper signature; would hold orders when the manager is away | **Deferred** to D9's one-year review; the audit need is logged as a RAID assumption (A-2, W10) |
| CR-3 | Logistics manager | Allow several trips per order line | Fits the model: trip lines already roll up to the trip (delivery-trip notes). No rule changes | **Accepted** for the parallel run; it will add one scenario to the delivery-trip story |
| CR-4 | Warehouse lead | Allow a trip to leave with less than planned when stock is short | Breaks R5. The need is real; the model's answer is "revise the plan first", which takes one step | **Rejected**; the plan-revision step is made faster instead |
| CR-5 | Warehouse lead | Let warehouse keepers preview and download the stock form before clicking Issue or Receive | A warehouse control, so the warehouse decides. Adds one step. A numbered form before the click would record a movement that has not happened, so the preview must be a draft with no number | **Accepted with a condition**: the preview is a draft; the number comes with the movement (D15, R8) |

## How a change is assessed

1. Which state rule, decision or story does it touch? (The traceability matrix, W8, answers this in one lookup.)
2. Is the need behind the request already met another way?
3. What does it cost, and which phase does it affect?
4. Who owns the decision? A business policy goes back to its owner (D9 to the sponsor, D10 to the chief accountant); the
   product owner decides only what the system does.
