# Decision log: Tanmark Industries back-office system

**Tanmark Industries is a fictional company.** These decisions show how a product owner reasons through a real
kind of change. The company, its people and every number are synthetic; the design patterns are real ones from
order-processing and accounting systems.

Format: one record per decision (context, decision, status, consequences), plus the option rejected and who decided. **Who decided** matters here: the product owner decides what the system
does and how it is rolled out; sales, purchasing, finance and the executive sponsor decide what is theirs. Each
lifecycle decision names the state rule it creates in `state/state-model.md`.

---

## D1. One data model for sales, purchasing, stock and accounting

* **Context.** Orders lived in email, stock in spreadsheets, vouchers in the accounting tool. An order could not be
  traced from the customer's request to the payment that closed it. Three departments wanted their own tools.
* **Decision.** One data model, shared by linked applications for sales and logistics, stock and production, and
  accounting. An order, its material requests, its trips, its invoice and its vouchers are one chain of records.
* **Option rejected.** Separate tools with nightly file exchange. Cheaper to start, but traceability would depend on
  exports no one owned.
* **Who decided.** Product owner, with the tech lead; signed off by the executive sponsor.
* **Status.** Accepted.
* **Consequences.** Slower first release; every later report reads one source.

## D2. A pilot group before full cutover

* **Context.** Ten departments, paper everywhere, and staff who had never used a shared system. A single go-live
  would put every process at risk on one day.
* **Decision.** Go live with a pilot group for two months, while open records migrate (D3). Widen to every
  department only when the go / no-go criteria in the cutover plan are met.
* **Option rejected.** One go-live date for all departments. Public-sector system changes show what happens when a
  pilot is cut and warnings do not travel up. The reference case is Canada's Phoenix pay system (Office of the
  Auditor General of Canada, 2018 spring reports, Report 1).
* **Who decided.** Product owner; the executive sponsor accepted the longer timeline.
* **Status.** Accepted.
* **Consequences.** A slower start. Most defects surfaced during the pilot, including the three decided-versus-built
  gaps that UAT found in pilot weeks 6 and 7 (D13).

## D3. Migrate what is open, by its state; archive what is closed

* **Context.** Years of paper orders and spreadsheets, of mixed quality.
* **Decision.** Migrate open orders, open purchase orders and current stock, each into the state it is really in
  (an order already in production loads as In production, never as Open). Closed records are scanned to a searchable
  archive. Posted accounting history is loaded as posted and is never re-opened.
* **Option rejected.** Migrating every open order as Open. Simpler, but it would let sales edit orders that were
  already in the workshop.
* **Who decided.** Product owner with the logistics, warehouse and finance leads.
* **Status.** Accepted.
* **Consequences.** A state has to be agreed for every migrated order, one by one, with its department. Migration ran
  batch by batch through the pilot and the parallel-run month, and finished before paper stopped.

## D4. Roles grant data; a transition table grants moves

* **Context.** In the old tools anyone with a file could change it. The first permission design listed create, read,
  update and delete per role, and said nothing about who may move a document from one state to the next.
* **Decision.** Two separate controls. Roles grant access to data. A transition table (`state/transitions.csv`)
  names, for every move, the role allowed to make it (rule R7).
* **Option rejected.** Folding moves into "update". Anyone who could edit an order could then complete it.
* **Who decided.** Product owner and the security engineer; roles agreed with each department head.
* **Status.** Accepted.
* **Consequences.** Every new move needs a row in the table, and the table is tested in UAT.

## D5. An order request becomes an order only when confirmed

* **Context.** Sales wanted to save half-finished orders while a customer decided, but the warehouse planned from
  anything it could see.
* **Decision.** Two-stage save. A request can be saved and changed freely; **confirm order** turns it into an Open
  order, and only an order can start fulfilment.
* **Option rejected.** One save that starts fulfilment. Every draft would have reached logistics.
* **Who decided.** Product owner with the sales lead.
* **Status.** Accepted.
* **Consequences.** A request has its own state and its own closure (Cancelled).

## D6. A forward-only order lifecycle with two ways to close

* **Context.** Orders were "cancelled" after materials had already gone to the workshop, and the stock records never
  recovered.
* **Decision.** The order moves forward only: Open, With logistics, In production, Receiving and shipping,
  Completed. **Cancelled** is allowed only before production. After production starts, the only closure is
  **Not completed**, where stock already received stays valid and open demand is dropped (rules R1, R3).
* **Option rejected.** Cancel at any stage. It would leave stock issued to an order that no longer existed.
* **Who decided.** The sales and logistics leads decided the closures; the product owner made them enforceable.
* **Status.** Accepted.
* **Consequences.** Two closure states to explain in training; a clean stock record.

## D7. The order locks for sales when it goes to logistics

* **Context.** Sales changed prices and quantities after logistics had planned production.
* **Decision.** After **send to logistics**, sales cannot edit the order. A quantity may be reduced at any stage; an
  increase is raised as a new order (rule R6).
* **Option rejected.** Edits allowed until production starts. Logistics would plan against a moving order.
* **Who decided.** Sales and logistics leads, together; the product owner recorded and built it.
* **Status.** Accepted.
* **Consequences.** More small follow-up orders; plans that hold.

## D8. The sale carries three statuses, and they move in one order

* **Context.** Finance asked for "three ways" to record a sale. Mapped against the documents, the three turned out to
  be three outcomes, not three routes: how much of the sale is invoiced, delivered and paid.
* **Decision.** Three status fields on the sales document, each rolled up from the trips and their invoices, each able
  to be partial (an order shipped on two trips is partly delivered after the first). Requirements are written against
  the statuses. Finance ruled the legal combinations, and in this business they form one sequence: a trip leaves only
  with its invoice (D16), and customers pay on credit terms after delivery (D17). A sale is never more delivered than
  invoiced, and never paid before it is delivered (working paper W6).
* **Option rejected.** One combined status (for example "Invoiced and paid"). It multiplies states, hides which step
  is missing, and cannot say "two of three trips delivered".
* **Who decided.** Product owner proposed the three fields; the finance lead ruled the legal combinations.
* **Status.** Accepted.
* **Consequences.** Reports can filter on any status; a combination outside the sequence is refused or flagged to
  finance.

## D9. Purchase approval stays outside the system

* **Context.** Purchase orders were signed on paper by the logistics manager. An in-app approval step was designed,
  and the buyers asked what it would add to a signature they already collected.
* **Decision.** No Approved state. A purchase order is Open when the buyer creates it; reaching **Received** counts as
  approved. The signature stays on paper.
* **Option rejected.** An in-app approval gate. It would duplicate the paper signature and hold orders when the
  manager was away.
* **Trade-off, stated.** The system cannot show who approved an order or stop an unsigned one. The control lives in
  the paper process and the receiving count.
* **Who decided.** Executive sponsor with the logistics manager. This is a business control decision, not the
  product owner's.
* **Status.** Accepted, to be reviewed after a year.
* **Consequences.** One fewer state; an audit of approvals needs the paper file.

## D10. Save is not post, and nothing is ever deleted

* **Context.** Accounting vouchers were edited and deleted after the fact, and the voucher numbers had gaps nobody
  could explain.
* **Decision.** Saving and posting are separate acts. A posted voucher is locked; a correction is a reversing voucher
  and the original stays. A saved voucher can be voided (amount set to zero, number kept). **No document is ever
  deleted, by any role** (rules R1, R2).
* **Option rejected.** Delete for the chief accountant only. Any delete breaks the number sequence an auditor checks.
* **Who decided.** Finance lead and chief accountant. This is an accounting policy; the product owner built it.
* **Status.** Accepted.
* **Consequences.** More vouchers on the ledger; a sequence with no gaps.

## D11. Acceptance is written before the build, and signed by the business

* **Context.** Earlier projects had been "done" when the developers said so.
* **Decision.** Every user story has Gherkin scenarios agreed before it is built, and every error path is a move the
  state model refuses. User acceptance testing runs those scenarios, and the department that owns the process signs.
* **Option rejected.** Testing by the development team alone.
* **Who decided.** Product owner; department heads agreed to sign off.
* **Status.** Accepted.
* **Consequences.** Slower sprints at first; fewer surprises at the pilot.

## D12. Paper is retired only after a clean parallel run

* **Context.** Staff trusted paper and would keep a copy "just in case".
* **Decision.** For one month after the pilot, every department runs paper and system side by side. Paper stops for a
  process when two weeks pass with no open discrepancy. After that the system is the record, and paper stays only
  where a decision keeps it: the signed purchase order (D9) and the customer-signed quarterly statement (D17).
* **Option rejected.** Stopping paper on go-live day.
* **Who decided.** Product owner with each department head.
* **Status.** Accepted.
* **Consequences.** Double work for a month; a clear moment when paper ends for each process.

## D13. Every decided rule is tested against the build

* **Context.** Several rules decided in meetings were missing from the first build, and nobody noticed until UAT.
* **Decision.** A decided-versus-built register (`state/state-model.md`) lists each rule, how it was tested, and
  what the build did. A gap is ticketed and becomes a go / no-go criterion for the phase it affects.
* **Option rejected.** Trusting the developers' reading of the meeting notes.
* **Who decided.** Product owner.
* **Status.** Accepted.
* **Consequences.** The register found three gaps before the parallel run (illustrative).

## D14. Physical facts guard the documents

* **Context.** Trips were edited after delivery to match what the invoice said, and trucks left with whatever was on the
  dock, so stock, delivery and invoice disagreed.
* **Decision.** A delivered trip is read-only, and a closed order freezes itself and all its trips (rule R4). The
  warehouse issues a trip exactly its planned quantity, and only then can logistics dispatch it; a shortfall means
  revising the plan first (rule R5).
* **Option rejected.** Letting the warehouse ship short and correct later. Quicker on the day, and the reason stock never
  matched.
* **Who decided.** The logistics lead, with the warehouse lead; the product owner made it enforceable.
* **Status.** Accepted.
* **Consequences.** One more step when stock is short (CR-4 in W9 asked to remove it and was refused); delivery records
  that match the stock.

## D15. The warehouse reviews the form before stock moves

* **Context.** Issuing and receiving stock cannot be undone: once stock has moved, nothing is cancelled (rule R3). The
  product owner designed the stock form to download after the warehouse keeper clicks Issue or Receive, so every
  form carried its official number.
* **Request.** Warehouse keepers asked to preview and download the form before that click, to check it against the
  goods before an action they cannot take back. It adds a step, and they accepted the friction (CR-5 in W9).
* **Decision.** Before the click, the form can be previewed and downloaded as a draft with no number. The official
  number is given only when the warehouse keeper clicks Issue or Receive, and the numbered form downloads then
  (rule R8). It applies to both issuing and receiving.
* **Option rejected.** The product owner's first design: no form until after the click. It kept the screens simple
  and left the warehouse no way to check before acting. Also rejected: a numbered form before the click, because
  it would put a numbered paper record on file for a movement that never happened.
* **Who decided.** The warehouse lead decided to review before acting; it is a warehouse control. The product owner
  decided how the system supports it, and kept the number tied to the movement.
* **Status.** Accepted.
* **Consequences.** One more step for each issue and receipt. No numbered stock form exists without the movement
  behind it.

## D16. The invoice travels with the goods: one invoice per trip

* **Context.** Goods may not leave the company without their invoice. On paper, the invoice was sometimes written
  after the truck had gone, and the sale then sat "delivered, not invoiced" until someone noticed.
* **Decision.** Each delivery trip has exactly one invoice. Accounting raises it once the warehouse has issued the
  goods to the trip, and logistics cannot dispatch the trip until it is raised (rule R9). A returned trip's invoice is
  credited in full by a credit note, never edited (R2).
* **Option rejected.** One invoice per order, raised when the order completes. It fits a business that invoices
  after delivery, and it would let goods leave without an invoice, which this business does not allow.
* **Who decided.** The chief accountant, with the logistics lead; the product owner made dispatch wait for it.
* **Status.** Accepted.
* **Consequences.** Accounting works to the warehouse's issue schedule, so trips cannot leave while accounting is
  closed; days from delivery to invoice fall to zero, because the invoice leaves first.

## D17. Sales are on credit terms, with a credit hold the chief accountant releases

* **Context.** Customers are businesses that buy on credit and pay later, so receivables are most of what
  finance manages. Terms were agreed per contract and kept in a binder; nobody could see who was overdue until the
  quarter-end statements went out.
* **Decision.** Payment terms and a credit limit live on each customer's contract: 30 days unless the contract says
  otherwise. Each invoice's due date is its invoice date plus those terms, and an ageing view groups open invoices by
  days overdue. A contract over its credit limit, or with an invoice past due, is on credit hold: a new order for it
  cannot be confirmed unless the chief accountant releases that order, with a reason (rule R10). A customer's
  transfer is allocated to its invoices, oldest due date first. Receivables are reconciled with every customer each
  quarter, on a statement the customer signs; stock is reconciled between the warehouse and accounting each month.
* **Option rejected.** A warning on the order screen that sales could click past. The hold only works if releasing it
  is a decision someone owns and signs.
* **Who decided.** The chief accountant set the hold and who releases it, with the director; the terms are agreed by
  sales and accounting per contract. The product owner built the hold, the ageing view and the allocation.
* **Status.** Accepted.
* **Consequences.** Some orders wait on a release; overdue balances are seen weekly instead of quarterly.
