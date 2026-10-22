# Spec Delta

## Purpose

Presents the student publicly through a small set of static pages that introduce them, describe their background and skills, showcase their projects, and provide contact details.

## ADDED Requirements

### Requirement: Homepage introduces the student
The homepage SHALL show a short introduction to the student and an overview of the website's sections.

#### Scenario: Visitor opens the homepage
- **WHEN** a visitor requests the site root
- **THEN** the server responds with the homepage containing the student's short introduction
- **AND** the page names the About, Portfolio, and Contact sections with links to them

#### Scenario: Introduction length
- **WHEN** the homepage is rendered
- **THEN** the introduction is a brief summary of a few sentences, not the full biography

### Requirement: About page describes the student's background
The About page SHALL contain the student's biography, education, skills, and interests.

#### Scenario: Visitor opens the About page
- **WHEN** a visitor requests the About page
- **THEN** the server responds with a page that has a biography section, an education section, a skills section, and an interests section
- **AND** none of these sections is empty

#### Scenario: Skills are readable as a list
- **WHEN** the About page displays skills
- **THEN** the skills appear as an enumerable list of individual skills rather than free-form prose

### Requirement: Portfolio lists student projects
The Portfolio page SHALL list the student's projects, and each project SHALL show a title, a description, and the technologies used, plus optionally a link to the project or its source code.

#### Scenario: Visitor opens the Portfolio page
- **WHEN** a visitor requests the Portfolio page
- **THEN** the server responds with a page listing every project the student has published
- **AND** each listed project shows its title, description, and technologies used

#### Scenario: Project without a link
- **WHEN** a listed project has no project or source-code link
- **THEN** the project is still listed with its title, description, and technologies
- **AND** no broken or empty link is rendered for it

#### Scenario: Project with a link
- **WHEN** a listed project has a project or source-code link
- **THEN** that link is rendered as an actionable link from the project entry

#### Scenario: No projects yet
- **WHEN** the portfolio contains no projects
- **THEN** the Portfolio page renders successfully with a message stating that no projects are listed yet

### Requirement: Contact page provides contact details
The Contact page SHALL display the student's contact information, and it SHALL NOT require or provide a contact form.

#### Scenario: Visitor opens the Contact page
- **WHEN** a visitor requests the Contact page
- **THEN** the server responds with a page showing at least one way to contact the student, such as an email address
- **AND** the page contains no form for submitting a message

#### Scenario: Email address is usable
- **WHEN** the Contact page displays an email address
- **THEN** it is rendered as a `mailto:` link

### Requirement: Every page is reachable from the navigation
All public pages SHALL be reachable through a navigation element that is present on every page.

#### Scenario: Navigate between pages
- **WHEN** a visitor is on any public page
- **THEN** the navigation offers links to Homepage, About, Portfolio, and Contact
- **AND** following each link loads that page successfully

#### Scenario: Current page is indicated
- **WHEN** a visitor views a page
- **THEN** the navigation visually marks the entry for the current page

### Requirement: Public pages are served as static frontend assets
The public pages SHALL be delivered as HTML, CSS, and JavaScript assets, and the frontend SHALL NOT contain application business logic or access the database.

#### Scenario: Plain page delivery
- **WHEN** a visitor requests any public page
- **THEN** the server returns an HTML document that loads the site's CSS and JavaScript files
- **AND** the page becomes fully readable with JavaScript disabled

#### Scenario: Unknown page
- **WHEN** a visitor requests a public path that does not exist
- **THEN** the server responds with a not-found page and an HTTP 404 status
