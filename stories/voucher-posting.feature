# Tanmark Industries is fictional. Amounts are illustrative.
# Document: voucher. Decision: D10.
# Map: after.bpmn, T12, T13.

Feature: Save, post and correct accounting vouchers without ever deleting one
  As an accountant
  I want saving and posting to be separate, and corrections to be reversing vouchers
  So that the ledger and the voucher sequence can always be audited

  # State: voucher | Saved | R2
  Scenario: A saved voucher does not reach the ledger
    Given the accountant saves receipt voucher "RV-0907" for 12,400.00 from customer "C-104"
    When the ledger for customer "C-104" is read
    Then receipt voucher "RV-0907" is not on it

  # Transition: voucher | Saved | post
  Scenario: Posting locks the voucher and updates the ledger
    Given receipt voucher "RV-0907" is "Saved" and its entries balance
    When the accountant posts it
    Then it shows the state "Posted"
    And the ledger for customer "C-104" shows 12,400.00 received

  # Transition: voucher | Posted | reverse
  Scenario: A posted voucher is corrected by a reversal
    Given receipt voucher "RV-0907" is "Posted"
    When the chief accountant reverses it with the reason "Wrong customer"
    Then receipt voucher "RV-0907" shows the state "Reversed"
    And a reversing voucher for 12,400.00 is posted
    And both vouchers stay in the sequence

  # Error path: voucher | Posted | edit
  Scenario: A posted voucher cannot be edited
    Given receipt voucher "RV-0907" is "Posted"
    When the accountant tries to change its amount to 12,000.00
    Then the change is refused
    And the accountant sees "A posted voucher is locked. Reverse it instead."

  # Error path: voucher | Saved | delete
  Scenario: A saved voucher cannot be deleted
    Given receipt voucher "RV-0911" is "Saved"
    When the accountant tries to delete it
    Then the deletion is refused
    And the accountant sees "Nothing is ever deleted. Void it instead."
