# Tanmark Industries is fictional. Customers, items and quantities are illustrative.
# Document: sales-order. Decision: D5, D7, D17.
# Map: after.bpmn, T1, T2, T3.

Feature: Take a sales order from request to logistics
  As a salesperson
  I want to save a request while the customer decides, and hand a confirmed order to logistics
  So that logistics only ever plans against orders that will not move under them

  Background:
    Given customer "C-104" is on file
    And "Steel drum D-200" is a product Tanmark sells

  # State: sales-order | Request
  Scenario: A saved request does not start fulfilment
    Given Sam saves an order request for 6 of "Steel drum D-200" for customer "C-104"
    When logistics opens its work list
    Then the request is not on it
    And the request shows the state "Request"

  # Transition: sales-order | Request | confirm order
  Scenario: Confirming the request makes it an order
    Given Sam's request for 6 of "Steel drum D-200" is complete
    When Sam confirms the order
    Then it shows the state "Open"
    And it has an order number

  # Error path: sales-order | Request | confirm on credit hold
  Scenario: A customer on credit hold gets no new order
    Given contract "K-104-2" of customer "C-104" is on credit hold
    And Sam's request for 6 of "Steel drum D-200" is complete
    When Sam tries to confirm the order
    Then the confirmation is refused
    And Sam sees "The customer is over its credit limit or overdue. The chief accountant must release the order."
    And the request still shows the state "Request"

  # Transition: sales-order | Request | confirm with credit release
  Scenario: The chief accountant releases one order, with a reason
    Given contract "K-104-2" of customer "C-104" is on credit hold
    And Sam's request for 6 of "Steel drum D-200" is complete
    When the chief accountant releases the order with the reason "Overdue invoice paid today; transfer confirmed"
    Then it shows the state "Open"
    And the release is logged with the chief accountant's name and the reason

  # Transition: sales-order | Open | send to logistics
  Scenario: Sending the order to logistics locks it for sales
    Given order "SO-2031" is "Open" with a salesperson assigned
    When Sam sends it to logistics
    Then it shows the state "With logistics"
    And the logistics coordinator sees it on the work list

  # Error path: sales-order | With logistics | sales edit
  Scenario: Sales cannot edit an order that logistics has
    Given order "SO-2031" is "With logistics"
    When Sam tries to change its quantity from 6 to 8
    Then the change is refused
    And Sam sees "After handoff, sales cannot edit the order. Raise a new order for an increase."
    And order "SO-2031" still shows a quantity of 6
