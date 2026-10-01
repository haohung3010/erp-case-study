% Readiness and cutover plan: order to cash, procure to pay and accounting
% Tanmark Industries (fictional)
% Product owner
% Version 3

**Tanmark Industries is a fictional company. Dates are weeks from pilot go-live; people and thresholds are illustrative.** The plan moves {{departments}} departments from paper to one system in three phases; each starts only when its go / no-go criteria are met.

# Phases

| Phase | Week | Who | What runs |
|---|---|---|---|
| 1, pilot | 1 to {{pilot_weeks}} | {{pilot_size}} people: product sales (one team), logistics and purchasing, the warehouse, the drum workshop | the system for the pilot's orders; open records migrate batch by batch, each in its real state |
| 2, parallel run | 9 to 12 | all ten departments | system and paper side by side; migration finishes; receivables move into the system |
| 3, the system is the record | from 13 | all ten departments | paper only where a decision keeps it: the signed purchase order (D9) and the customer-signed quarterly statement (D17) |

# Data migration, by state (decision D3)

* **Open orders** load in the state they are really in, agreed with their department one by one. An order already in production loads as In production, never as Open.
* **Open purchase orders** load as Open or Received, against a count of what has arrived.
* **Stock:** a full physical count on the weekend before the pilot, and again before the parallel run. The loaded count must equal the count on every line, or the difference is signed by the warehouse lead.
* **Receivables:** each contract loads with its terms and credit limit; each open invoice with its due date and what is paid. A customer's opening balance must equal its last signed quarterly statement.
* **Posted accounting history** loads as posted and is never reopened. Closed records are scanned to a searchable archive.

# Training

* One **superuser per department**, trained two weeks before it joins. **One-hour role sessions** on every shift, in a practice copy loaded with the UAT scenarios.
* A **one-page card per role**: what each locked state means and what to do instead.

# Parallel run (decision D12)

Paper stops for a process when two weeks pass with no open discrepancy.

# Go / no-go criteria, checked before each phase

| # | Criterion | Evidence | Owner |
|---|---|---|---|
| 1 | Every UAT scenario for the phase's stories passes, error paths included | UAT workbook, sign-off sheet | Owning department |
| 2 | No open severity 1 defect; each severity 2 has a workaround | UAT Defects sheet | Tech lead |
| 3 | Every migrated record is in its agreed state; stock equals the count; each opening receivable equals its signed statement | Reconciliation sheet | Department lead |
| 4 | The transition table and roles are set for the phase's documents | Transition table, access list | Product owner |
| 5 | No open gap in the decided-versus-built register for the phase | The register (D13) | Product owner |
| 6 | Every user has a login with the right role and has been trained | Access list, attendance | Department head |

# Risks watched during each phase

| Risk | Early sign | Response |
|---|---|---|
| Staff keep working on paper after the parallel run | Orders arrive by email once paper has stopped | Superuser follows up the same day |
| A migrated order is in the wrong state | Sales can edit an order the workshop has started | Correct its state with its department; recheck the batch it came in |
| Stock drifts from the system count | Cycle-count differences on the weekly sample | Recount the bay; find the step that skipped the system |
| Finance is not ready to post by the parallel run | Vouchers saved but not posted at month end | Finance practises posting in the copy during the pilot's last two weeks |
| Adoption stalls below the whole group | Weekly active users flat for two weeks | Ask the people who are not using it why; often a shift or a missing role |
| Migrated overdue invoices put key customers on credit hold on day one | The hold list, run the week before receivables go live | The chief accountant releases, or agrees a payment plan, before go-live |
| Trucks wait for invoices | An issued trip waits over an hour for its invoice | Accounting covers every dispatch hour (N13) |

**Who decides.** The product owner recommends; the executive sponsor decides. A no-go names the failed criterion and its re-check date.

**Rollback.** In the parallel run, stop system entry and reconcile back to paper. After it, fix forward: a correction document, never an edit.
