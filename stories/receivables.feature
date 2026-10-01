# Tanmark Industries is fictional. Customers, contracts, dates and amounts are illustrative.
# Document: sales-invoice. Decision: D16, D17.
# Map: after.bpmn, T11, T12.

Feature: Invoice every trip, and collect each invoice on its contract's terms
  As an accountant
  I want every trip invoiced before it leaves, and every invoice collected on the terms of its contract
  So that what each customer owes is known, aged and reconciled

  Background:
    Given customer "C-104" buys under contract "K-104-2" with 30-day payment terms
    And trip "TR-131" for order "SO-2060" is "Issued"

  # Transition: sales-invoice | Draft | raise
  Scenario: The invoice is raised for the issued trip, with its due date from the contract
    When the accountant raises the invoice for trip "TR-131" on 2 March for 5,000.00
    Then invoice "INV-401" shows the state "Raised"
    And its due date is 1 April

  # Error path: sales-invoice | Draft | raise before the trip is issued
  Scenario: A trip that has not been issued cannot be invoiced
    Given trip "TR-132" for order "SO-2060" is "Planned"
    When the accountant tries to raise the invoice for trip "TR-132"
    Then the invoice is refused
    And the accountant sees "Raise the invoice for goods the warehouse has issued to the trip."

  # Transition: sales-invoice | Raised | record part payment
  Scenario: One transfer pays the oldest invoice first
    Given invoice "INV-401" for 5,000.00 due 1 April is "Raised"
    And invoice "INV-402" for 3,000.00 due 4 April is "Raised"
    And the trips for both invoices are confirmed delivered
    When customer "C-104" transfers 6,000.00 and the receipt is allocated
    Then invoice "INV-401" shows the state "Paid"
    And invoice "INV-402" shows the state "Partly paid" with 2,000.00 still due

  # Transition: sales-invoice | Partly paid | record final payment
  Scenario: The last payment clears the invoice
    Given invoice "INV-402" is "Partly paid" with 2,000.00 still due
    When customer "C-104" transfers 2,000.00 and the receipt is allocated
    Then invoice "INV-402" shows the state "Paid"

  # State: sales-invoice | Raised | R10
  Scenario: An invoice past its due date shows in the ageing view and holds the contract
    Given invoice "INV-405" for 4,000.00 due 1 April is "Raised"
    When the ageing view is run on 20 April
    Then invoice "INV-405" shows 19 days overdue, in the 1 to 30 days column
    And contract "K-104-2" shows "On credit hold"

  # Transition: sales-invoice | Raised | credit in part
  Scenario: A price correction is a part credit note, not an edit
    Given invoice "INV-401" for 5,000.00 is "Raised"
    When the chief accountant issues a credit note for 300.00 against it, with the reason "agreed price correction"
    Then invoice "INV-401" still shows the state "Raised"
    And its balance due is 4,700.00
    And the original amount of 5,000.00 is unchanged

  # Error path: sales-invoice | Raised | edit amount
  Scenario: An invoice amount cannot be edited
    Given invoice "INV-401" for 5,000.00 is "Raised"
    When the accountant tries to change its amount to 4,500.00
    Then the change is refused
    And the accountant sees "Correct an invoice with a credit note, never by editing it."
