# W13. Release roadmap and dependencies

**Tanmark Industries is fictional. Weeks and dates are illustrative.**

**The finding first.** The roadmap is ordered by dependencies, not by what each department asked for first. Finance
wanted its vouchers and receivables in the pilot, but the posting rules were not yet built or tested. So collection
joined in the parallel run, and overdue receivables did not move during the pilot (report, section 11). The one dependency that slipped after rollout was external and had
no date on it, and the fix was to give it one.

Weeks count from pilot go-live, as in the cutover plan; full go-live, when the system becomes the record, is week 13. Negative weeks are before it. The elicitation log (W3) counts
its discovery weeks from the start of discovery: discovery week 1 is week -17 here.

## The roadmap

| When | Release or milestone | What it carries | Gate |
|---|---|---|---|
| Weeks -17 to -13 | Discovery and the state model | elicitation E1 to E8 (W3); the transition table agreed line by line (E8) | the state diagrams signed by the owning leads |
| Weeks -12 to -1 | Build, six two-week sprints | the Must stories (W9), each with its Gherkin written before the sprint (D11) | each sprint review, with the sales and logistics leads |
| Week 1 | **Release 1: pilot go-live** | order lifecycle and lock on handoff; order closure; delivery trips, each with its invoice (D16); purchase orders and receipts | go / no-go criteria 1 to 6 (cutover plan) |
| Weeks 6 and 7 | UAT for the parallel run | the voucher, invoicing and D13 register tests; three gaps found (DB-1 to DB-3) | each owning department signs its stories |
| Week 8 | **Release 2** | the three register gaps fixed; save, post and reverse vouchers; draft stock forms (D15, from E10 in week 6) | UAT re-run on the fixed rules |
| Week 9 | **Release 3: the parallel run** (every department joins; paper alongside) | receivables: payment terms, ageing, allocation from bank statements and credit hold (D17); the three sale statuses (W6); several trips per order line (CR-3) | go / no-go for the parallel run |
| Week 13 | **Release 4: the system is the record** | order status views for the director's office (O1); the remaining access by role; paper kept only for the signed purchase order and the customer-signed statement | each department head, after two clean weeks (D12) |
| Week 52 | D9 review | whether an in-app purchase approval is needed after all (CR-2, A-2) | the director, with the logistics manager |

**Why the pilot carries these four stories.** They are one end-to-end path a single order team can run: sales to
logistics to the drum workshop to the warehouse to a trip. Everything after the pilot adds a department to a path that
already works, rather than starting a second path.

## Dependencies

Each dependency has a type. **Mandatory** means the work cannot be done in another order;
**discretionary** means the team chose the order. **Internal** means the project controls it; **external** means it
does not. All of them are also in the RAID log (W10), where they are reviewed every week.

| ID | This must be done | Before this | Type | Owner | Outcome |
|---|---|---|---|---|---|
| DP-4 | The transition table agreed (E8) | the first sprint that builds a state rule | discretionary, internal (D11) | product owner | done in discovery week 5 |
| DP-1 | Finance rules which status combinations are legal (W6) | the sale-statuses story, Release 3 | mandatory, internal | finance lead | ruled in week 5 |
| DP-5 | Vouchers can be posted, and the posted status works (DB-1 fixed) | finance joins, the parallel run | mandatory, internal | tech lead | Release 2, week 8 |
| DP-6 | UAT signed by the department that owns each story (D11) | each phase's go / no-go | discretionary, internal | department heads | signed for both phases |
| DP-2 | A full physical stock count | each phase's start | mandatory, internal | warehouse lead | done the weekend before each phase |
| DP-3 | The bank statement format | receipt allocation, Release 3 | mandatory, external | the bank | received in week 6 |
| DP-7 | A supplier's new price list loaded before its effective date | orders priced at the right price | mandatory, external | price control lead | **slipped two weeks in month 10** |

## The dependency that slipped (DP-7)

* **What happened.** A supplier sent a new price list. It was loaded two weeks after it took effect, so the orders
  placed in that window carried the old price and were re-keyed. Monthly rework rose before falling back (report,
  section 11).
* **Why the roadmap missed it.** Every other dependency had a date because it sat on the path to a release. Price lists
  arrive after rollout, on the supplier's schedule, so nothing had put this one on the weekly review.
* **What the product owner did.** Added it to the RAID log with an owner, the price control lead. Each new price list
  now gets a load date one week before it takes effect, and the weekly review checks that date. The re-keyed orders
  were corrected with credit notes and new invoices, not by editing invoices (R2).
* **The lesson.** A dependency that recurs after full go-live needs an owner and a lead time as much as one on the path to a
  release. The roadmap ends at week 13; the dependencies do not.

## Control: how the roadmap was kept

* **Weekly**, with the director: the release on the critical path, any dependency at risk, and the one decision needed
  that week (W12).
* **Every two weeks**, at sprint planning: stories re-ordered against the dependencies above, never against the loudest
  request (W9, change requests).
* **When a date moves**, the change is assessed the way a change request is: which release, which dependency, which
  phase's go / no-go. The director decides whether the phase moves; the product owner recommends.
