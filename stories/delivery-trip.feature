# Tanmark Industries is fictional. Quantities are illustrative.
# Document: delivery-trip. Decision: D14, D15, D16.
# Map: after.bpmn, T10, T16, T11, T17.

Feature: Ship exactly what was planned, and freeze what was delivered
  As a logistics coordinator
  I want each trip to carry exactly its planned quantity and to lock once delivered
  So that stock, delivery and invoicing agree

  Background:
    Given order "SO-2050" is "Receiving and shipping"
    And trip "TR-118" is planned to deliver 5 of "Container C-20" for it

  # Transition: delivery-trip | Planned | issue
  Scenario: The warehouse issues exactly the planned quantity
    When the warehouse keeper issues 5 of "Container C-20" to trip "TR-118"
    Then trip "TR-118" shows the state "Issued"
    And stock of "Container C-20" falls by 5
    And the issue form downloads with its form number

  # Transition: delivery-trip | Issued | dispatch
  Scenario: The trip leaves once it is issued
    Given trip "TR-118" is "Issued"
    And its invoice "INV-390" is "Raised"
    When the logistics coordinator dispatches the trip with a departure time
    Then trip "TR-118" shows the state "In transit"

  # Transition: delivery-trip | In transit | confirm delivery
  Scenario: A delivered trip is read-only
    Given trip "TR-118" is "In transit"
    When the logistics coordinator confirms delivery with an arrival time
    Then trip "TR-118" shows the state "Delivered"
    And its times and quantities can no longer be changed

  # Error path: delivery-trip | Planned | issue a different quantity
  Scenario: The warehouse cannot issue a different quantity
    When the warehouse keeper tries to issue 4 of "Container C-20" to trip "TR-118"
    Then the issue is refused
    And the warehouse keeper sees "Issue exactly the plan, or revise the plan first."

  # Error path: delivery-trip | Planned | download numbered form
  Scenario: A numbered issue form cannot exist before the goods are issued
    Given trip "TR-118" is "Planned"
    When the warehouse keeper tries to download the numbered issue form
    Then the download is refused
    And the warehouse keeper sees "No stock has moved yet. Preview the draft form; its number is given when the goods are issued."

  # Error path: delivery-trip | Issued | dispatch without an invoice
  Scenario: A trip cannot leave without its invoice
    Given trip "TR-118" is "Issued"
    And no invoice has been raised for it
    When the logistics coordinator tries to dispatch the trip
    Then the dispatch is refused
    And the coordinator sees "Goods leave only with their invoice. Raise the trip's invoice first."
