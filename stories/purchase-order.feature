# Tanmark Industries is fictional. Suppliers and quantities are illustrative.
# Document: purchase-order. Decision: D9, D15.
# Map: after.bpmn, T5, T6.

Feature: Buy materials without an approval step inside the system
  As a buyer
  I want a purchase order to be live when I create it and approved when its goods are received
  So that orders move without waiting on a second, duplicate approval

  # State: purchase-order | Open
  Scenario: A new purchase order is open at once
    Given the buyer holds a signed paper request for 200 kg of "Stainless bar S-40"
    When the buyer creates purchase order "PO-5110" with supplier "V-07"
    Then it shows the state "Open"
    And no approval task is created

  # State: purchase-order | Open | R8
  Scenario: The warehouse keeper reviews a draft receipt form before receiving
    Given purchase order "PO-5110" is "Open"
    When the warehouse keeper previews the receipt form
    Then the form downloads marked "Draft" with no form number
    And purchase order "PO-5110" still shows the state "Open"

  # Error path: purchase-order | Open | download numbered form
  Scenario: A numbered receipt form cannot exist before the goods are received
    Given purchase order "PO-5110" is "Open"
    When the warehouse keeper tries to download the numbered receipt form
    Then the download is refused
    And the warehouse keeper sees "No stock has moved yet. Preview the draft form; its number is given when the goods are received."

  # Transition: purchase-order | Open | receive into stock
  Scenario: Receiving the goods counts as approval
    Given purchase order "PO-5110" is "Open"
    When the warehouse keeper receives 200 kg into stock against it
    Then it shows the state "Received"
    And stock of "Stainless bar S-40" rises by 200 kg
    And the receipt form downloads with its form number

  # Transition: purchase-order | Received | receive more
  Scenario: A second delivery gets its own receipt form
    Given purchase order "PO-5120" for 300 kg of "Stainless bar S-40" has received 200 kg
    When the warehouse keeper receives the remaining 100 kg against it
    Then it still shows the state "Received"
    And a new receipt form downloads with its own form number

  # Transition: purchase-order | Received | close
  Scenario: The order closes when every line is received and invoiced
    Given purchase order "PO-5110" is "Received"
    And the supplier's invoice for it is recorded
    When the buyer closes it
    Then it shows the state "Completed"

  # Error path: purchase-order | Received | cancel
  Scenario: A received purchase order cannot be cancelled
    Given purchase order "PO-5110" is "Received"
    When the buyer tries to cancel it
    Then the cancellation is refused
    And the buyer sees "Goods are in stock. Return them to the supplier instead."
