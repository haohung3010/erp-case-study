# W12. Communications plan and lessons learned

**Tanmark Industries is fictional.**

## Communications plan

| Audience | What | How | How often | From |
|---|---|---|---|---|
| Executive sponsor | priorities, risks, go / no-go | a one-page status and a 30-minute review | weekly | product owner |
| Department heads | stories to review, UAT to sign, what changes for their team | a working session per story | per sprint | product owner |
| Development team | backlog, acceptance criteria, the transition table | sprint planning and refinement | every two weeks | product owner |
| Pilot group | what changes this week, where to get help | a notice at the start of shift, and the superuser | weekly during the pilot | superusers |
| All staff | the phase plan and training dates | email and a notice in each department | before each phase | product owner |
| Customers | from week 9 a new order is held when the contract is over its credit limit or has an invoice past due, until the chief accountant releases it (D17); terms stay as in each contract | a letter from their sales contact; a call the week before to each customer the hold list names (RK-6) | once, four weeks before the parallel run | sales lead, with the chief accountant |
| Finance | decided-versus-built findings that touch the ledger | a short written note, the same day | as found | product owner |

## Lessons learned register

| # | Lesson | What happened | What changes next time |
|---|---|---|---|
| L1 | A pilot that stops at the invoice tests most of the process and none of its end | collection stayed on paper in the pilot; overdue receivables did not move until the parallel run | put collection in the pilot |
| L2 | Train by shift as well as by role | two night-shift receivers never logged in | schedule training on every shift |
| L3 | Ask what each document may still change, and who may change it | most rules came from that question (W3) | start discovery with the state model, not the screens |
| L4 | A business request can name the wrong shape | "three ways to record a sale" were three outcomes, not three routes (D8) | map each request to the documents before specifying it |
| L5 | A decided rule is not a built rule | three decided rules were missing from the build (D13) | test every decided rule in UAT, as its own row |
| L6 | The approval a system adds is not always one the business needs | in-app purchase approval would have duplicated a signature (D9) | ask what an approval step adds before designing it |
