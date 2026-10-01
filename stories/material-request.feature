# Tanmark Industries is fictional. Materials and quantities are illustrative.
# Document: material-request. Decision: D6, D15.
# Map: after.bpmn, T4, T7.

Feature: Issue materials to the workshop, and never cancel what has left the warehouse
  As a factory manager
  I want each material request issued in as many deliveries as the workshop needs, with a numbered form for each
  So that every kilogram on the workshop floor traces to a request and a form, and stock matches the shelves

  Background:
    Given order "SO-2070" for 300 steel drums is "In production"
    And material request "MR-310" for it asks for 400 kg of "Steel sheet 1.2 mm"
    And the factory manager is assigned to "MR-310"

  # Error path: material-request | Open | download numbered form
  Scenario: A numbered issue form cannot exist before the materials are issued
    Given material request "MR-310" is "Open"
    When the warehouse keeper tries to download the numbered issue form
    Then the download is refused
    And the warehouse keeper sees "No stock has moved yet. Preview the draft form; its number is given when the materials are issued."

  # Transition: material-request | Open | issue first materials
  Scenario: The first issue starts the request
    Given material request "MR-310" is "Open"
    When the warehouse keeper issues 250 kg to the drum workshop
    Then "MR-310" shows the state "Issuing"
    And stock of "Steel sheet 1.2 mm" falls by 250 kg
    And the issue form downloads with its form number

  # Transition: material-request | Issuing | issue more materials
  Scenario: A second issue gets its own form
    Given material request "MR-310" is "Issuing" with 150 kg still open
    When the warehouse keeper issues 100 kg to the drum workshop
    Then "MR-310" still shows the state "Issuing"
    And a new issue form downloads with its own form number

  # Transition: material-request | Issuing | issue last materials
  Scenario: The last issue completes the request
    Given material request "MR-310" is "Issuing" with 50 kg still open
    When the warehouse keeper issues the last 50 kg
    Then "MR-310" shows the state "Completed"

  # Error path: material-request | Issuing | cancel
  Scenario: A request that has issued materials cannot be cancelled
    Given material request "MR-310" is "Issuing"
    When the factory manager tries to cancel it
    Then the cancellation is refused
    And the factory manager sees "Materials have left the warehouse. Complete the request, or close the order as Not completed."

  # Transition: material-request | Open | cancel
  Scenario: A request with nothing issued can be cancelled, and is kept
    Given material request "MR-311" is "Open" and nothing has been issued against it
    When the factory manager cancels it
    Then "MR-311" shows the state "Cancelled"
    And it keeps its number
