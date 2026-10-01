# W3. Elicitation log

**Tanmark Industries is fictional. Sessions and weeks are illustrative.**

Weeks 1 to 5 count from the start of discovery; E9 and E10 took place in week 6 of the pilot (the roadmap, W13,
puts both on one timeline). Each session records the question it set out to answer, what was heard, and how it was confirmed. An unconfirmed result
is not a requirement.

| # | Week | Technique | With | Question | Heard | Confirmed by | Led to |
|---|---|---|---|---|---|---|---|
| E1 | 1 | Document analysis | paper forms, spreadsheets | What does an order carry today? | 14 fields, 4 of them re-keyed by logistics | field list reviewed with the sales lead | data dictionary (W4) |
| E2 | 1 | Observation | warehouse | How is stock checked? | walking the shelves against a paper ledger | a timed walk of one order | O2, D3 |
| E3 | 2 | Interviews | sales lead, logistics manager | When may an order still change? | sales edits after logistics has planned | a workshop on the order lifecycle (E5) | D7 |
| E4 | 2 | Interviews | buyers, logistics manager | What does approval of a purchase order add? | the paper signature is already collected | the logistics manager, in writing | D9 |
| E5 | 3 | Workshop | sales, logistics, warehouse, factory | How may an order close? | "cancelled" used after materials were issued | the state diagram, signed by both leads | D6, sales-order model |
| E6 | 3 | Interviews | chief accountant | What makes the ledger auditable? | deletes leave gaps in the voucher numbers | the posting policy, in writing | D10 |
| E7 | 4 | Document analysis | finance's "three ways to record a sale" | Are these three inputs or three outputs? | three outcomes: invoiced, paid, delivered | the finance lead, against the status list | D8, W6 |
| E11 | 4 | Interviews | chief accountant, logistics lead | When is a sale invoiced, and how is it collected? | goods leave only with their invoice; customers pay on their contract's credit terms; overdue balances surface only in the quarter-end statements | the chief accountant, in writing; the legal combinations table (W6) | D16, D17, D8 |
| E8 | 5 | Workshop | all department heads | Who may move each document? | "whoever can edit it" | the transition table, reviewed line by line | D4, R7 |
| E9 | pilot 6 | Prototype review | pilot group | Does the order screen show the state? | the lock after handoff was not visible | a banner on locked orders, retested | DB-2 fix |
| E10 | pilot 6 | Prototype review | warehouse keepers | Can the issue and receipt screens be used as built? | they want to check the form before clicking an action they cannot undo | the warehouse lead, in writing; a draft form retested in the pilot | D15, R8, CR-5 |

## What the log shows

Most rules came from asking **when a document may still change, and who may change it**. Two of them (D8 and D9)
changed what the business had first asked for, and one (D15) changed what the product owner had first designed. A requirement taken at face value in week 1 would have built three
input routes for a sale, and an approval step nobody needed.
