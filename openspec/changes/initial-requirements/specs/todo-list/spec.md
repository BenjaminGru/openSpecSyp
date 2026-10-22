# Spec Delta

## Purpose

Gives a single user a private ToDo list whose items can be viewed, created, edited, completed, and deleted through a REST API, with items persisted so they survive application restarts.

## ADDED Requirements

### Requirement: ToDo items expose a defined set of fields
Every ToDo item SHALL contain a title, a description, a completion status, and a creation date, and the system SHALL return these fields when it returns an item.

#### Scenario: Item shape in responses
- **WHEN** the system returns a ToDo item
- **THEN** the item includes an identifier, a title, a description, a completion status, and a creation date
- **AND** the completion status is a boolean
- **AND** the creation date is an ISO 8601 timestamp

#### Scenario: Description may be empty
- **WHEN** a ToDo item is stored without a description
- **THEN** the item is still valid and its description is returned as an empty value

### Requirement: User can view all ToDo items
The system SHALL provide a way to list all ToDo items.

#### Scenario: List with existing items
- **WHEN** the user opens the ToDo List page
- **THEN** the frontend requests the list of ToDo items from the REST API
- **AND** every stored item is displayed with its title, description, completion status, and creation date

#### Scenario: Empty list
- **WHEN** the user opens the ToDo List page and no items are stored
- **THEN** the page shows an empty-state message instead of an error
- **AND** the API returns an empty collection with a success status

#### Scenario: Completed items are distinguishable
- **WHEN** the list contains both completed and uncompleted items
- **THEN** completed items are visually distinguishable from uncompleted ones

### Requirement: User can create a ToDo item
The system SHALL let the user create a ToDo item with a title and an optional description.

#### Scenario: Create with title and description
- **WHEN** the user submits a new item with a non-empty title and a description
- **THEN** the backend stores the item with the given values and completion status uncompleted
- **AND** the creation date is set by the backend at creation time
- **AND** the new item appears in the list without a page reload

#### Scenario: Create with title only
- **WHEN** the user submits a new item with a non-empty title and no description
- **THEN** the item is created with an empty description

#### Scenario: Reject an empty title
- **WHEN** the user submits a new item whose title is empty or only whitespace
- **THEN** the backend rejects the request with a client error status
- **AND** no item is stored
- **AND** the frontend shows the validation error and keeps the entered values

#### Scenario: Title length limit
- **WHEN** the user submits a title longer than the documented maximum length
- **THEN** the backend rejects the request with a client error status

### Requirement: User can edit a ToDo item
The system SHALL let the user change the title and description of an existing ToDo item.

#### Scenario: Edit an existing item
- **WHEN** the user edits an item's title or description and saves
- **THEN** the backend updates the stored item with the new values
- **AND** the item's identifier and creation date are unchanged
- **AND** the updated values are shown in the list

#### Scenario: Edit with invalid title
- **WHEN** the user saves an edit whose title is empty or only whitespace
- **THEN** the backend rejects the request with a client error status
- **AND** the stored item keeps its previous values

#### Scenario: Edit a missing item
- **WHEN** a request tries to update an item that does not exist
- **THEN** the backend responds with a not-found status

### Requirement: User can mark a ToDo item as completed
The system SHALL let the user change an item's completion status between completed and uncompleted.

#### Scenario: Mark as completed
- **WHEN** the user marks an uncompleted item as completed
- **THEN** the backend stores the item as completed
- **AND** the list reflects the new status

#### Scenario: Mark as uncompleted again
- **WHEN** the user marks a completed item as uncompleted
- **THEN** the backend stores the item as uncompleted
- **AND** the list reflects the new status

#### Scenario: Completing keeps other fields
- **WHEN** an item's completion status changes
- **THEN** its title, description, and creation date remain unchanged

### Requirement: User can delete a ToDo item
The system SHALL let the user delete a ToDo item.

#### Scenario: Delete an existing item
- **WHEN** the user deletes an item and confirms the deletion
- **THEN** the backend removes the item permanently
- **AND** the item disappears from the list without a page reload

#### Scenario: Deletion needs confirmation
- **WHEN** the user requests deletion of an item
- **THEN** the frontend asks for confirmation before calling the API

#### Scenario: Delete a missing item
- **WHEN** a request tries to delete an item that does not exist
- **THEN** the backend responds with a not-found status

### Requirement: ToDo items persist across restarts
ToDo items SHALL be stored durably so that they remain available after the application restarts.

#### Scenario: Data survives a restart
- **WHEN** the user creates or edits items and the application is stopped and started again
- **THEN** the list returns the same items with the same titles, descriptions, completion statuses, and creation dates

#### Scenario: Storage is server-side
- **WHEN** the frontend reads or writes ToDo items
- **THEN** it does so only through the REST API
- **AND** it holds no authoritative copy of the items outside the current view

### Requirement: ToDo list is private and single-user
The ToDo list SHALL be a single-user list available without user registration, sign-in, or roles.

#### Scenario: No sign-in required
- **WHEN** the user opens the ToDo List page
- **THEN** the list is usable immediately without creating an account or signing in

#### Scenario: ToDo page is not linked from the public site
- **WHEN** a visitor browses the public pages
- **THEN** the public navigation does not advertise the ToDo List
- **AND** the ToDo List remains reachable at its own page path

### Requirement: ToDo list uses a REST/JSON API
The system SHALL expose ToDo operations through a REST API that accepts and returns JSON.

#### Scenario: List endpoint
- **WHEN** a client sends a `GET` request for the ToDo collection
- **THEN** the backend responds with a JSON array of items

#### Scenario: Create endpoint
- **WHEN** a client sends a `POST` request with a JSON body to the ToDo collection
- **THEN** the backend responds with the created item as JSON and a success status

#### Scenario: Update endpoint
- **WHEN** a client sends a `PATCH` or `PUT` request with a JSON body for a single item
- **THEN** the backend responds with the updated item as JSON

#### Scenario: Delete endpoint
- **WHEN** a client sends a `DELETE` request for a single item
- **THEN** the backend removes the item and responds with a success status and no item body

#### Scenario: API failures are reported
- **WHEN** a request fails validation or targets a missing item
- **THEN** the backend responds with an appropriate 4xx status and a JSON error message
- **AND** the frontend shows the error to the user instead of silently failing
