# Tanmark Industries is fictional. Quantities are illustrative.
# Document: sales-order. Decision: D6, D10.
# Map: after.bpmn, G0, T14, G3, T15.

Feature: Close an order the right way for how far it got
  As a sales manager
  I want to cancel an order before production, and close it as not completed after
  So that stock already issued or received is never orphaned

  # Transition: sales-order | Open | cancel
  Scenario: An open order can be cancelled
    Given order "SO-2040" is "Open"
    When the sales manager cancels it
    Then it shows the state "Cancelled"
    And order "SO-2040" can still be found and read

  # Transition: sales-order | In production | close as not completed
  Scenario: An order in production closes as not completed
    Given order "SO-2041" is "In production"
    And 4 of its 10 tank bodies have been received into stock
    When the sales manager closes it as not completed
    Then it shows the state "Not completed"
    And the 4 received assemblies stay in stock
    And the 6 not yet made drop out of open demand

  # State: sales-order | Cancelled | R1
  Scenario: Nothing is removed when an order closes
    Given order "SO-2040" is "Cancelled"
    When anyone searches for order "SO-2040"
    Then the order is found with its history

  # Error path: sales-order | In production | cancel
  Scenario: An order in production cannot be cancelled
    Given order "SO-2041" is "In production"
    When the sales manager tries to cancel it
    Then the cancellation is refused
    And the sales manager sees "Production has started. Close the order as Not completed instead."
    And order "SO-2041" still shows the state "In production"

  # Transition: sales-order | Receiving and shipping | close as not completed
  Scenario: An order with goods already received closes as not completed
    Given order "SO-2043" is "Receiving and shipping"
    And 6 of its 10 containers have been received and 2 have been delivered
    When the sales manager closes it as not completed
    Then it shows the state "Not completed"
    And the 4 received containers not yet delivered stay in stock
    And the 4 not yet made drop out of open demand

  # Error path: sales-order | Receiving and shipping | cancel
  Scenario: An order with goods already received cannot be cancelled
    Given order "SO-2043" is "Receiving and shipping"
    When the sales manager tries to cancel it
    Then the cancellation is refused
    And the sales manager sees "Goods exist. Close the order as Not completed instead."
    And order "SO-2043" still shows the state "Receiving and shipping"

  # Error path: sales-order | Completed | edit
  Scenario: A completed order cannot be edited
    Given order "SO-2044" is "Completed"
    When the sales manager tries to change the quantity on its first line
    Then the change is refused
    And the sales manager sees "A completed order is frozen."
