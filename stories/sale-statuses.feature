# Tanmark Industries is fictional. Customers, dates and amounts are illustrative.
# Document: sale-statuses. Decision: D8, D16, D17.
# Map: after.bpmn, T11, T17, T12.

Feature: See how far a sale has got: invoiced, delivered, paid
  As a finance lead
  I want each sale to show how much is invoiced, delivered and paid, rolled up from its trips and invoices
  So that I can see which step a sale is waiting on without decoding a combined status

  Background:
    Given order "SO-2060" for 8,000.00 ships on two trips
    And trip "TR-131" carries 5,000.00 of it and trip "TR-132" carries 3,000.00
    And customer "C-104" buys under contract "K-104-2" with 30-day payment terms

  # State: sale-statuses | Not invoiced, Not delivered, Unpaid
  Scenario: A new sale starts with all three statuses open
    When order "SO-2060" is confirmed
    Then its statuses are "Not invoiced", "Not delivered" and "Unpaid"

  # Transition: sale-statuses | Not invoiced | first trip invoiced
  Scenario: The first trip's invoice makes the sale partly invoiced
    When the invoice for trip "TR-131" is raised
    Then its statuses are "Partly invoiced", "Not delivered" and "Unpaid"

  # Transition: sale-statuses | Not delivered | first trip delivered
  Scenario: Delivery never runs ahead of invoicing
    Given the invoice for trip "TR-131" is raised and the trip has left with it
    When trip "TR-131" is confirmed delivered
    Then its statuses are "Partly invoiced", "Partly delivered" and "Unpaid"

  # State: sale-statuses | Invoiced, Delivered, Unpaid | R10
  Scenario: A delivered sale waits on its credit terms
    Given the invoices for trips "TR-131" and "TR-132" were raised on 2 March and 5 March
    And both trips are confirmed delivered
    Then its statuses are "Invoiced", "Delivered" and "Unpaid"
    And its invoices fall due on 1 April and 4 April

  # Transition: sale-statuses | Partly delivered | last trip delivered
  Scenario: A returned trip does not leave the sale waiting
    Given trip "TR-131" is confirmed delivered
    And trip "TR-132" is returned, and its invoice is credited in full
    When the return is recorded
    Then its delivery status is "Delivered"
    And order "SO-2060" can complete

  # Error path: sale-statuses | Not invoiced | deliver before invoicing
  Scenario: A sale cannot be delivered before it is invoiced
    Given no invoice has been raised for order "SO-2060"
    When a delivery is recorded for trip "TR-131"
    Then the delivery is refused
    And the coordinator sees "A trip leaves only with its invoice. Raise the trip's invoice first."
    And its statuses are still "Not invoiced", "Not delivered" and "Unpaid"
