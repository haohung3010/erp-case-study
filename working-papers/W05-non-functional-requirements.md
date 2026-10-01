# W5. Non-functional requirements

**Tanmark Industries is fictional. Targets are illustrative.** Each requirement names how it is tested; one that cannot be tested is not a requirement.

| ID | Quality | Requirement | Tested by |
|---|---|---|---|
| N1 | Auditability | Every state change records the document, the from and to states, the role, the time and any reason | UAT: each story's final state is checked against the change record |
| N2 | Integrity | No document can be deleted by any role, through any screen or interface (R1) | the delete error path in the UAT script (voucher posting); an interface test that sends a delete |
| N3 | Integrity | A posted voucher's amounts cannot change; only a reversing voucher corrects it (R2) | UAT: voucher-posting error paths |
| N4 | Integrity | Voucher numbers form a sequence with no gaps, including voided vouchers | a monthly sequence check report |
| N5 | Security | Data access follows roles; moving a document follows the transition table; the two are checked separately (R7) | a test per role: may read, may not move |
| N6 | Security | Permission checks cannot be switched off without a logged change | the decided-versus-built register (DB-3) |
| N7 | Availability | The system is available during working hours on all shifts, including nights | monitored uptime during the pilot |
| N8 | Performance | An order's state and history open in under 2 seconds for a user on the warehouse network | timed on the warehouse floor during UAT |
| N9 | Usability | A locked document says why it is locked and what to do instead | the refusal messages in the stories |
| N10 | Data retention | Closed records stay searchable for seven years | archive search test after migration |
| N11 | Migration | Every migrated open record loads in its real state (D3) | reconciliation of states for each migration batch |
| N12 | Operability | Each department has a superuser, and a daily check-in for the first two weeks | cutover plan, training section; checked before each phase |
| N13 | Availability | Invoicing is staffed and available whenever the warehouse dispatches, because a trip cannot leave without its invoice (R9) | the dispatch schedule against accounting's hours, checked before each phase |

## Why the rules appear twice

N2, N3 and N5 restate rules from the state model as qualities of the whole system. The model says which move is
refused; the NFR says **no route** reaches it, including imports, interfaces and administrator screens. A rule enforced
on one screen and open on an interface is the most common way a decided rule goes missing in the build.
