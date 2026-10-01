# W10. RAID log: risks, assumptions, issues, dependencies

**Tanmark Industries is fictional. Entries and dates are illustrative.** A RAID log is one working list a project manager reviews every week;
each entry has an owner and a next action.

## Risks

| ID | Risk | Likelihood | Impact | Response | Owner |
|---|---|---|---|---|---|
| RK-1 | Staff keep working on paper after the parallel run | medium | high | superusers follow up the same day; weekly report to department heads | product owner |
| RK-2 | Migrated orders load in the wrong state (D3) | medium | high | each open order's state agreed with its department before load; reconciled per migration batch | logistics lead |
| RK-3 | A rule decided in a meeting is missing from the build | high | high | the decided-versus-built register, tested in UAT (D13) | product owner |
| RK-4 | Finance is not ready to post in the system by the parallel run | medium | medium | voucher posting moved to Must for the parallel run (W9) | chief accountant |
| RK-5 | Adoption stalls on the night shift | medium | medium | training by shift; weekly active users watched | product owner |
| RK-6 | Migrated overdue invoices put key customers on credit hold on day one (D17) | high | high | the hold list run the week before receivables go live; each held customer released or on an agreed payment plan before go-live | chief accountant |
| RK-7 | Trucks wait for invoices, since a trip cannot leave without its invoice (D16) | medium | high | accounting covers every dispatch hour (N13); an issued trip waiting over an hour is escalated | chief accountant |

RK-6 and RK-7 are also the cutover plan's risks for the phases; the two lists name the same risks with the same responses.

## Assumptions

| ID | Assumption | If it proves false |
|---|---|---|
| A-1 | The paper purchase-order signature stays in place (D9) | reopen D9; CR-2 becomes a Must |
| A-2 | An auditor accepts the paper file as the approval record | an in-app approval (CR-2) is needed |
| A-3 | Finished goods can be counted before each phase | the phase slips a week |

## Issues (found and open)

| ID | Issue | Found | Status |
|---|---|---|---|
| I-1 | Vouchers have no posted status; saved and posted look the same (DB-1) | UAT, week 7 | fixed before the parallel run; go / no-go criterion for finance |
| I-2 | Sales can still edit an order with logistics (DB-2) | UAT, week 6 | fixed before the parallel run |
| I-3 | Chart-of-accounts permission checks switched off during the build (DB-3) | UAT, week 7 | switched on before the parallel run |
| I-4 | Two night-shift receivers never logged in | pilot, week 5 | closed: trained on shift, week 7 |
| I-5 | A supplier price list was loaded two weeks late; orders in the window were re-keyed (DP-7) | month 10 | closed: price lists get a load date one week before they take effect |

## Dependencies

| ID | Dependency | On | Needed by |
|---|---|---|---|
| DP-1 | Finance ruling on legal status combinations (W6) | finance lead | the sale-statuses story |
| DP-2 | A full physical stock count | warehouse lead | the pilot and the parallel run |
| DP-3 | The bank statement format | the bank | receipt allocation, the parallel run |
| DP-4 | The transition table agreed (E8) | product owner | the first sprint that builds a state rule |
| DP-5 | Vouchers can be posted (DB-1 fixed) | tech lead | finance joins, the parallel run |
| DP-6 | UAT signed by each story's owning department | department heads | each phase's go / no-go |
| DP-7 | A supplier's new price list loaded one week before it takes effect | price control lead | orders priced correctly; recurring after full go-live |

Each dependency's type (mandatory or discretionary, internal or external) and its place on the timeline are in the
release roadmap, W13.
