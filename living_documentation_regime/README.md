# Living Documentation Regime

- [Regime De/Activation](#regime-deactivation)
- [Adding LivDoc Regime to the Workflow](#adding-livdoc-regime-to-the-workflow)
- [Regime Configuration](#regime-configuration)
  - [Inputs](#inputs)
  - [Features De/Activation](#features-deactivation)
- [Expected Output](#expected-output)
  - [Index Page Example](#index-page-example)
  - [Issue Page Example](#issue-page-example)
- [Documentation Ticket Introduction](#documentation-ticket-introduction)
  - [Labels](#labels)
  - [Hosting Documentation Tickets in a Solo Repository](#hosting-documentation-tickets-in-a-solo-repository)
- [Living Documentation Regime Features](#living-documentation-regime-features)
  - [Data Mining from GitHub Repositories](#data-mining-from-github-repositories)
  - [Data Mining from GitHub Projects](#data-mining-from-github-projects)
  - [Living Documentation Page Generation](#living-documentation-page-generation)
  - [Structured Output](#structured-output)
  - [Output Grouped by Topics](#output-grouped-by-topics)

This regime is designed to data-mine GitHub repositories for [documentation tickets](#documentation-ticket-introduction) containing project documentation (e.g. tagged with feature-related labels). This tool automatically generates comprehensive living documentation in Markdown format, providing detailed feature overview pages and in-depth feature descriptions.

## Regime De/Activation

- **liv-doc-regime** (required)
  - **Description**: Enables or disables Living Documentation regime.
  - **Usage**: Set to true to activate.
  - **Example**:
    ```yaml
    with:
      liv-doc-regime: true
    ```
    
---
## Adding LivDoc Regime to the Workflow

See the default Living Documentation regime action step definition:

```yaml
- name: Generate Living Documentation
  id: generate_living_doc
  uses: AbsaOSS/living-doc-generator@v0.3.0
  env:
    GITHUB-TOKEN: ${{ secrets.LIV_DOC_GENERATOR_ACCESS_TOKEN }}  
  with:
    # living documentation regime de/activation
    liv-doc-regime: true
    
    # input repositories + feature to filter projects
    liv-doc-repositories: '[
      {
        "organization-name": "fin-services",
        "repository-name": "investment-app",
        "query-labels": ["feature", "enhancement"],
        "projects-title-filter": []
      },
      {
        "organization-name": "health-analytics",
        "repository-name": "patient-data-analysis",
        "query-labels": ["functionality"],
        "projects-title-filter": ["Health Data Analysis Project"]
      },
      {
        "organization-name": "open-source-initiative",
        "repository-name": "community-driven-project",
        "query-labels": ["improvement"],
        "projects-title-filter": ["Community Outreach Initiatives", "CDD Project"]
      }
    ]'
```

See the full example of LivDoc regime step definition (in example are used non-default values):

```yaml
- name: Generate Living Documentation
  id: generate_living_doc
  uses: AbsaOSS/living-doc-generator@v0.3.0
  env:
    GITHUB-TOKEN: ${{ secrets.LIV_DOC_GENERATOR_ACCESS_TOKEN }}  
  with:
    # living documentation regime de/activation
    liv-doc-regime: true
    
    # project verbose (debug) logging feature de/activation
    verbose-logging: true
    
    # output directory path for generated documentation
    output-path: "/output/directory/path"
    
    # input repositories + feature to filter projects
    liv-doc-repositories: '[
      {
        "organization-name": "fin-services",
        "repository-name": "investment-app",
        "query-labels": ["feature", "enhancement"],
        "projects-title-filter": []
      },
      {
        "organization-name": "health-analytics",
        "repository-name": "patient-data-analysis",
        "query-labels": ["functionality"],
        "projects-title-filter": ["Health Data Analysis Project"]
      },
      {
        "organization-name": "open-source-initiative",
        "repository-name": "community-driven-project",
        "query-labels": ["improvement"],
        "projects-title-filter": ["Community Outreach Initiatives", "CDD Project"] 
      }
    ]'

    # project state mining feature de/activation
    liv-doc-project-state-mining: true

    # structured output feature de/activation
    liv-doc-structured-output: true
    
    # group output by topics feature de/activation
    liv-doc-group-output-by-topics: true
```

---
## Regime Configuration

Configure the LivDoc regime by customizing the following parameters based on your needs:

### Inputs
-**liv-doc-repositories** (optional, `default: '[]'`)
  - **Description**: A JSON string defining the repositories to be included in the documentation generation.
  - **Usage**: List each repository with its organization name, repository name, query labels and attached projects you want to filter if any. Only projects with these titles will be considered. For no filtering projects, leave the list empty.
  - **Example**:
    ```yaml
    with:
      liv-doc-repositories: '[
      {
        "organization-name": "fin-services",
        "repository-name": "investment-app",
        "query-labels": ["feature", "enhancement"],
        "projects-title-filter": []
      },
      {
        "organization-name": "health-analytics",
        "repository-name": "patient-data-analysis",
        "query-labels": ["functionality"],
        "projects-title-filter": ["Health Data Analysis Project"]
      },
      {
        "organization-name": "open-source-initiative",
        "repository-name": "community-driven-project",
        "query-labels": ["improvement"],
        "projects-title-filter": ["Community Outreach Initiatives", "CDD Project"] 
      }
    ]'
    ```

### Features De/Activation

- **liv-doc-project-state-mining** (optional, `default: false`)
  - **Description**: Enables or disables the mining of project state data from [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects).
  - **Usage**: Set to true to activate.
  - **Example**:
    ```yaml
    with:
      liv-doc-project-state-mining: true
    ```
    
- **liv-doc-structured-output** (optional, `default: false`)
  - **Description**: Enables or disables structured output.
  - **Usage**: Set to true to activate.
  - **Example**:
    ```yaml
    with:
      liv-doc-structured-output: true
    ```

- **liv-doc-group-output-by-topics** (optional, `default: false`)
  - **Description**: Enable or disable grouping tickets by topics in the summary index.md file.
  - **Usage**: Set to true to activate.
  - **Example**:
    ```yaml
    with:
      liv-doc-group-output-by-topics: true
    ```

---
## Expected Output

The Living Documentation Generator in LivDoc regime is designed to produce an Issue Summary page (index.md) along with multiple detailed single issue pages.

### Index Page Example

```markdown
# Issue Summary page

Our project is designed with a myriad of issues to ensure seamless user experience, top-tier functionality, and efficient operations.
Here, you'll find a summarized list of all these issues, their brief descriptions, and links to their detailed documentation.

## Issue Overview

| Organization name| Repository name            | Issue 'Number - Title'         | Linked to project | Project Status | Issue URL  |
|------------------|----------------------------|--------------------------------|-------------------|----------------|------------|
| AbsaOSS          | living-doc-example-project | [#89 - Test issue 2](89_test_issue_2.md)      | 🔴 | ---            |[GitHub](#) |
| AbsaOSS          | living-doc-example-project | [#88 - Test issue](88_test_issue.md)          | 🟢 | Todo           |[GitHub](#) |
| AbsaOSS          | living-doc-example-project | [#41 - Initial commit.](41_initial_commit.md) | 🟢 | Done           |[GitHub](#) |
| AbsaOSS          | living-doc-example-project | [#33 - Example bugfix](33_example_bugfix.md)  | 🔴 | ---            |[GitHub](#) |
```

- **Project Status** can have various values depending on the project, such as: Todo, Done, Closed, In Progress, In Review, Blocked, etc. 
These values can vary from project to project.
- The `---` symbol is used to indicate that an issue has no required project data.

### Issue Page Example

```markdown
# FEAT: Advanced Book Search
| Attribute         | Content                               |
|-------------------|---------------------------------------|
| Organization name | AbsaOSS                               |
| Repository name   | living-doc-example-project            |
| Issue number      | 17                                    |
| State             | open                                  |
| Issue URL         | [GitHub link](#)                      |
| Created at        | 2023-12-12 11:34:52                   |
| Updated at        | 2023-12-13 10:24:58                   |
| Closed at         | None                                  |
| Labels            | feature                               |
| Project title     | Book Store Living Doc Example project |
| Status            | Todo                                  |
| Priority          | P1                                    |
| Size              | S                                     |
| MoSCoW            | N/A                                   |

## Issue Content
Users often struggle to find specific books in a large catalog. An advanced search feature would streamline this process, enhancing user experience.

### Background
...
```

---
## Documentation Ticket Introduction

A **Documentation Ticket** is a small piece of documentation realised as GitHub Issue dedicated to project documentation. Unlike development-focused tickets, Documentation Ticket remain open continuously, evolving as updates are needed, and can be reopened or revised indefinitely. They are not directly tied to Pull Requests (PRs) but can be referenced for context.

- **Content Rules**:
  - **Non-technical Focus:** 
    - Keep the documentation body free of technical solution specifics.
    - Technical insights should be accessible through linked PRs or Tickets within the development repository.
  - **Independent Documentation:** 
    - Ensure the content remains independent of implementation details to allow a clear, high-level view of the feature or user story's purpose and functionality.

### Labels

To enhance clarity, the following label groups define and categorize each Documentation Issue:
- **Topic**:
  - **{Name}Topic:** Designates the main focus area or theme relevant to the ticket, assigned by the editor for consistency across related documentation.
    - Examples: `ReportingTopic`, `UserManagementTopic`, `SecurityTopic`.
  - **NoTopic:** Indicates that the ticket does not align with a specific topic, based on the editor's discretion.
- **Type**:
  - **DocumentedUserStory:** Describes a user-centric functionality or process, highlighting its purpose and value.
    - Encompasses multiple features, capturing the broader goal from a user perspective.
  - **DocumentedFeature:** Details a specific feature, providing a breakdown of its components and intended outcomes.
    - Built from various requirements and can relate to multiple User Stories, offering an in-depth look at functionality.
  - **DocumentedRequirement:** Outlines individual requirements or enhancements tied to the feature or user story.
- **Issue States**:
  - **Upcoming:** The feature, story, or requirement is planned but not yet implemented.
  - **Implemented:** The feature or requirement has been completed and is in active use.
  - **Deprecated:** The feature or requirement has been phased out or replaced and is no longer supported.

**DocumentedUserStory** and **DocumentedFeature** serve as **Epics**, whereas **DocumentedRequirement** represents specific items similar to feature enhancements or individual requirements.

### Hosting Documentation Tickets in a Solo Repository

Using a dedicated repository solely for documentation tickets provides multiple advantages:
- **Streamlined Management:** This avoids cross-project conflicts and board exclusions and enables specialized templates solely for documentation purposes.
- **Focused Access Control:** This allows a small team to manage and edit documentation without interference, maintaining high-quality content.
- **Optimized Data Mining:** Supports easier and more efficient data extraction for feedback and review cycles through Release Notes.
- **Implementation Reflection:** Mirrors elements from the implementation repositories, providing a high-level knowledge source that is valuable for both business and technical teams.
- **Release Notes Integration:** Documentation can evolve based on insights from release notes, serving as a dynamic feedback loop back to the documentation repository.

---
## Living Documentation Regime Features

### Data Mining from GitHub Repositories

This feature allows you to define which repositories should be included in the living documentation process. By specifying repositories, you can focus on the most relevant projects for your documentation needs.

- **Default Behavior**: By default, the action will include all repositories defined in the repositories input parameter. Each repository is defined with its organization name, repository name, and query labels.

### Data Mining from GitHub Projects

This feature allows you to define which projects should be included in the living documentation process. By specifying projects, you can focus on the most relevant projects for your documentation needs.

- **Default Behavior**: By default, the action will include all projects defined in the repositories. This information is provided by the GitHub API.
- **Non-default Example**: Use available options to customize which projects are included in the documentation.
  - `project-state-mining: false` deactivates the mining of project state data from GitHub Projects. If set to **false**, project state data will not be included in the generated documentation and project related configuration options will be ignored. 
  - `projects-title-filter: []` filters the repository attached projects by titles, if list is empty all projects are used.
      ```json
        {
          "organization-name": "absa-group",
          "repository-name": "living-doc-example-project",
          "query-labels": ["feature", "bug"],
          "projects-title-filter": ["Community Outreach Initiatives", "Health Data Analysis"]
         }
      ```

### Living Documentation Page Generation

The goal is to provide a straightforward view of all issues in a single table, making it easy to see the overall status and details of issues across repositories.

- **Default Behavior**: By default, the action generates a single table that lists all issues from the defined repositories.

### Structured Output

This feature allows you to generate structured output for the living documentation and see a summary `index.md` page for each fetched repository.

- **Default Behavior**: By default, the action generates all the documentation in a single directory.
- **Non-default Example**: Use the structured output feature to organize the generated documentation by organization and repository name.
  - `structured-output: true` activates the structured output feature.
    ```
    output
    |- org 1
      |--repo 1
         |-- issue md page 1
         |-- issue md page 2
         |-- _index.md
      |-- _index.md
    |- org 2
      |--repo 1
         |-- issue md page 1
         |-- _index.md
      |--repo 2
          ...
      |-- _index.md
    |- _index.md
    ```

### Output Grouped by Topics

The feature allows you to generate grouped output by topics. This feature is useful when you want to group tickets by specific topics or themes.

To gain a better understanding of the term "Topic", refer to the [Labels](#labels) section.

- **Default Behavior**: By default, the action generates all the documentation in a single directory.
- **Non-default Example**: Use the grouped output feature to organize the generated documentation by topics.
  - `group-output-by-topics: true` activates the grouped output feature.
    ```
    output
    |- topic 1
      |-- issue md page 1
      |-- issue md page 2
      |-- _index.md
    |- topic 2
      |-- issue md page 1
      |-- _index.md
    |- _index.md
    ```
    