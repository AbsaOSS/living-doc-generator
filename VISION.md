# Living Documentation Generator

- [Purpose of this Page](#purpose-of-this-page)
- [Regimes and Their Usage](#regimes-and-their-usage)
  - [DocumentedUserStories](#documenteduserstories)
  - [DocumentedFeatures](#documentedfeatures)
  - [DocumentedRequirements](#documentedrequirements)
  - [Coverage matrix](#coverage-matrix)
  - [Repositor(y/ies) YML Files](#repository-yml-files)
  - [Incidents](#incidents)
  - [Release Notes](#release-notes)
  - [User Guide](#user-guide)
- [Rationale for an Isolated GitHub Repository](#rationale-for-an-isolated-github-repository)
- [Proposed Issue Content Examples](#proposed-issue-content-examples)
- [Content Formatting for Documentation Types (US, Features, Req)](#content-formatting-for-documentation-types-us-features-req)
- [Examples](#examples)
  - [DocumentedUserStory GH Issue](#documenteduserstory-gh-issue)
  - [DocumentedFeature GH Issue](#documentedfeature-gh-issue)
  - [DocumentedRequirement GH Issue](#documentedrequirement-gh-issue)

## Purpose of this Page
The goals of this document are to:
- Outline features yet to be implemented.
- Expand upon the content provided in README.md.

## Regimes and Their Usage
Outlined below are the various regimes, their intended purposes, and the specific inputs and outputs associated with each.
### DocumentedUserStories
Produces documentation centered on user-oriented stories that outline workflows or features from the user’s perspective.
- Build on expectation that User Stories are one of the minimum unit of documentation to be created.
- When enabled with DocumentedFeatures regime and relation between User Stories and Features is established, both outputs can be connected by the links.
 
### DocumentedFeatures
Produces documentation specifically for project features.
- Build on expectation that Features are one of the minimum unit of documentation to be created.
- **Default** in current implementation.

### DocumentedRequirements
Produces documentation for granular requirements tied to specific features.
- Can be operated only with DocumentedFeatures regime enabled.

### Coverage matrix
Provides an overview of the test coverage for User Stories, Features, and Requirements, enabling teams to track documentation alignment with test validation. This feature visualizes test completeness by listing covered items across unit, integration, and E2E tests, helping to identify any gaps in the test suite for crucial documentation items.

### Repositor(y/ies) YML Files
Generates an organized summary of all .yml files within specified repositories, capturing key details such as events, jobs, and workflows. This overview can serve as a quick reference for repository configurations, supporting consistent CI/CD practices across projects.

### Incidents
Documents historical and active incidents related to the project, capturing details such as incident type, affected features or requirements, severity level, and resolution status. This feature enhances transparency and helps trace incident tickets back to related documentation for streamlined troubleshooting and future prevention.

### Release Notes
Generates consolidated release notes summarizing feature deployments, updates, and deprecations. Links back to related documentation tickets, features, and requirements provide context, enabling easy navigation from release highlights to detailed documentation. This feature supports alignment across development, testing, and business stakeholders by providing a clear view of project progress.

### User Guide
Uses **DocumentedUserStories** as the foundational data source to build a User Guide.
- **Content:**
  - Each User Story should define a required input for User Guide generation. 
  - Each User Story should ideally include one end-to-end (E2E) test, with a preference for automation to ensure repeatable validation.
  - E2E test should generate screenshots for User Guide inclusion.
- **Structure:**
  - **Body:** Organizes content into well-defined, categorized chapters.
  - **Steps:** Includes descriptive steps with illustrative images for better clarity and user comprehension.

## Rationale for an Isolated GitHub Repository
Hosting documentation tickets in a dedicated GitHub repository offers several key benefits:
- **Process Clarity and Separation:** Maintains a clear boundary between documentation tickets and active project tickets, reducing clutter and ensuring documentation is easily accessible without interference from active development.
- **Pilot Platform:** Serves as an initial testing ground for the documentation approach, enabling iterative improvements based on early feedback.
- **Controlled Access:** Limits editing permissions to a core group, ensuring content accuracy and consistency, while allowing broader read-only access for stakeholders and team members.

## Proposed Issue Content Examples 
Here are structural suggestions for key documentation types, using examples to clarify content organization:
- **User Stories (US):** Outlines overarching user needs and goals, providing context for related features.
- **Features:** Describes specific aspects or components supporting the User Story, broken down into clear, actionable tasks.
- **Requirements (Req)**: Lists individual requirements essential for completing a feature, enhancing detail and traceability.

**Using Task Lists:** Leverage task lists in both User Stories and Features to improve clarity and progress tracking.

## Content Formatting for Documentation Types (US, Features, Req)
A consistent structure helps standardize documentation across different types:
- **Open Format:**
  - **Information Collection:** Use an initial section to gather relevant information at the start.
  - **Description:** Separate sections for high-level descriptions to serve both documentation and User Guide purposes (in case of US).
- **Body (Markdown):**
  - **Topic:**
    - Requirements do not need a topic.
    - For Features, each issue should focus on a single topic (as a label). 
    - User Stories are broader in scope.
  - **Versioning:**
    - **Expected:** Specifies the target version for initial release.
    - **Available:** Indicates the actual version released.
    - **Deprecated from:** States the version from which the feature or requirement is no longer supported.
    - Note: Version can link to Release Notes.
  - **Dependencies:**
    - No direct linkage to development tickets or PRs is required.
    
This structure is intended to ensure consistency, clarity, and easy navigation across documentation types, fostering a cohesive understanding of project features and requirements.

## Examples
Mined information, not needed to repeat in body of the issue:
- **Unique-ID**: AbsaOSS/any-project-docs/4
- **Type:** DocumentedUserStory, DocumentedFeature, DocumentedRequirement (from label)
- **Topic:** SearchingTopic (from label)
- **State:** Upcoming, Implemented, Deprecated (from label)

### DocumentedUserStory GH Issue
````markdown
# User Story
- Title: Advanced Search Functionality
- Version:
  - Expected: v1.2
  - Available: v1.2.1
  - Deprecated from: v5.3 

## Description  
As a user, I want to be able to perform advanced searches within the application, so I can quickly locate specific content based on multiple filters and criteria.

## Acceptance Criteria
- The user can apply multiple filters simultaneously (e.g., date range, category).
- The search results update dynamically based on selected filters.
- The search results display within 2 seconds.

```[tasklist]
## Related Features
- [ ] #5
- [ ] #6
- [ ] #34
```

## User Guide
### Description
This user story covers the advanced search functionality, enabling users to locate specific information efficiently by setting filters. Each step of the search experience is tailored for usability and speed.

### End-to-End Test to Guide Steps
- Automated: True
- Prerequisite:
  - Ensure at least one searchable object is in the database and that the user has access to the advanced search page. 
- Steps:
  - Step 1: Open the search page.
  - Step 2: Define the search criteria. (screenshot: step-2.png)
  - Step 3: Apply multiple filters.
  - Step 4: Verify the search results update correctly. (screenshot: step-4.png)
  - Step 5: Verify the search results display within 2 seconds.

## Change Log
| Version | Date       | Comment                          |
|---------|------------|----------------------------------|
| v1      | 2024-10-30 | Initial version of the User Story |
````

### DocumentedFeature GH Issue
````markdown
# Feature
- Title: Date Filter for Search
- Version:
  - Expected: v1.2
  - Available: v1.2.1
  - Deprecated from: -  

## Description
The Date Filter allows users to narrow down search results by selecting a specific start and end date. It enhances search precision, especially for time-sensitive data.

```[tasklist]
## Related User Stories
- [ ] #2
```

```[tasklist]
## Related Requirements
- [ ] #45
- [ ] #46
```

## Change Log

| Version | Date       | Comment                          |
|---------|------------|----------------------------------|
| v1      | 2024-10-30 | Initial version of the Feature   |

````

### DocumentedRequirement GH Issue
````markdown
# Requirement
- Title: Filter Search Results by Date Range
- Priority: High
- Version:
  - Expected: v1.1
  - Available: v1.1.5

## Description (What User does)
The user selects a start and end date to limit search results to items within that date range.

## Rationale (What User may want)
The user may want to focus on specific periods to find relevant information faster or analyze data from a particular timeframe.

```[tasklist]
## Associated Feature
- [ ] #2
```

## Change Log

| Version | Date       | Comment                          |
|---------|------------|----------------------------------|
| v1      | 2024-10-30 | Initial version of the Requirement |

````
