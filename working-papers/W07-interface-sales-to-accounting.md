# W7. Interface specification: sales to accounting

**Tanmark Industries is fictional.** The one place where a number
computed in one application becomes a document in another, and so the place where a rule is most easily applied twice.

## What crosses the boundary

| Item | Sent by | Received by | When |
|---|---|---|---|
| order total, before tax | sales and logistics | accounting | when the order is confirmed, and again on any change |
| the trip's issued lines and prices | sales and logistics | accounting | when the warehouse issues a trip; accounting raises the trip's invoice from them |
| invoice raised, with its number and due date | accounting | sales and logistics | before the trip may be dispatched (R9) |
| tax amount and rate | sales and logistics | accounting | with the total |
| discount | **not sent** | | already applied in the total |
| delivery status | sales and logistics | accounting | when each trip is Delivered |
| payment status and credit hold | accounting | sales and logistics | when a receipt is allocated, and when a contract goes on or off credit hold (R10) |

## Rules at the boundary

1. **The discount is applied once, on the sales side.** Tax is computed on the price after discount. Accounting receives
   the net total and never re-applies or re-derives a discount. *A discount applied on both sides is the classic
   interface defect: every number is right on its own screen and the ledger is wrong.*
2. **Accounting never writes an order's lifecycle state, with one deliberate exception.** It writes the payment
   status and the credit hold. The exception is the chief accountant's release of an order on credit hold, which moves
   the order from Request to Open with a logged reason (R10, D17). Sales and logistics never
   write a voucher.
3. **A change to a confirmed order resends the total.** If the invoice is already raised, the change arrives as a credit
   note request, never as an edit to the invoice (B5).
4. **Every message is idempotent.** Resending the same trip twice leaves one invoice, not two.
5. **A failed message is visible.** It waits in a queue that the finance lead can see, with the order number and the
   reason; it is never dropped.

## Error handling

| Failure | What the system does | Who acts |
|---|---|---|
| accounting is unavailable | messages queue and send in order when it returns; **issued trips cannot be dispatched until their invoices are raised** | the logistics lead is alerted; trucks wait (N13) |
| a total arrives for an order accounting has not seen | held, with a flag to finance | accountant |
| a second total arrives after the invoice | turned into a credit note request | accountant |
| amounts disagree between the two sides | a daily reconciliation report lists them | finance lead |

## Tested by

UAT for receivables, sale statuses and voucher posting, plus an interface test that resends one trip three times and
checks for exactly one invoice.
