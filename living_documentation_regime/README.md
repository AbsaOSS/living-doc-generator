# Living Documentation Regime

- [Regime De/Activation](#regime-deactivation)
- [Adding Living Documentation Regime to the Workflow](#adding-living-documentation-regime-to-the-workflow)
- [Regime Inputs](#regime-inputs)
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
    - [Output Formats](#output-formats)

This regime is designed to data-mine GitHub repositories for [documentation tickets](#documentation-ticket-introduction) containing project documentation (e.g. tagged with feature-related labels). This tool automatically generates comprehensive living documentation in a format compatible with an [mdoc viewer](https://github.com/AbsaOSS/cps-mdoc-viewer), providing detailed feature overview pages and in-depth feature descriptions.

## Regime De/Activation

- **liv-doc-regime** (required)
  - **Description**: Enables or disables the Living Documentation regime.
  - **Usage**: Set to true to activate.
  - **Example**:
    ```yaml
    with:
      liv-doc-regime: true
    ```
    
---
## Adding Living Documentation Regime to the Workflow

See the default minimal Living Documentation regime action step definition:

```yaml
- name: Generate Living Documentation
  id: generate_living_doc
  uses: AbsaOSS/living-doc-generator@v0.4.0
  env:
    GITHUB-TOKEN: ${{ secrets.REPOSITORIES_ACCESS_TOKEN }}  
  with:
    liv-doc-regime: true                   # living documentation regime de/activation  
    liv-doc-repositories: |
        [
          {
            "organization-name": "fin-services",
            "repository-name": "investment-app"
          }
        ]
```

See the full example of Living Documentation regime step definition (in example are used non-default values):

```yaml
- name: Generate Living Documentation
  id: generate_living_doc
  uses: AbsaOSS/living-doc-generator@v0.4.0
  env:
    GITHUB-TOKEN: ${{ secrets.REPOSITORIES_ACCESS_TOKEN }}  
  with:
    liv-doc-regime: true                   # living documentation regime de/activation
    verbose-logging: true                  # project verbose (debug) logging feature de/activation
    report-page: true                      # report page generation feature de/activation

    liv-doc-repositories: |
        [
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
          }
        ]
    liv-doc-project-state-mining: true     # project state mining feature de/activation
    liv-doc-structured-output: true        # structured output feature de/activation
    liv-doc-group-output-by-topics: true   # group output by topics feature de/activation
    liv-doc-output-formats: "mdoc"         # output formats selection, supported: mdoc
```

---
## Regime Inputs

Configure the Living Documentation regime by customizing the following parameters:

| Input Name                       | Description                                                                                                                                                                                | Required | Default   | Usage                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `liv-doc-repositories`           | A JSON string defining the repositories to be included in the documentation generation.                                                                                                    | No       | `'[]'`    | Provide a list of repositories, including the organization name, repository name, query labels, and any attached projects you wish to filter.<br><br> The `query-labels` include parameter is optional. Only issues with the specified labels will be fetched. To fetch all issues (all labels), omit this parameter or leave the list empty. <br><br> The `projects-title-filter` include parameter is optional. Only issues linked to the specified projects will be fetched. To fetch all issues (all projects), either omit this parameter or leave the list empty. |
| `liv-doc-project-state-mining`   | Enables or disables the mining of project state data from [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects). | No       | `false` ` | Set to true to activate.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `liv-doc-structured-output`      | Enables or disables [structured output](#structured-output).                                                                                                                               | No       | `false`   | Set to true to activate.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `liv-doc-group-output-by-topics` | Enable or disable [grouping tickets by topics](#output-grouped-by-topics) in the summary index.md file.                                                                                    | No       | `false`   | Set to true to activate.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `liv-doc-output-formats`         | Selects the [output formats](#output-formats) for the Living Documentation Regime.                                                                                                                          | No       | `mdoc`    | Provide a comma-separated list of output formats.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

- **Example**

  ```yaml
  with:
    liv-doc-repositories: |
      [
        {
          "organization-name": "fin-services",
          "repository-name": "investment-app",
          "query-labels": ["feature", "enhancement"]
        },
        {
          "organization-name": "open-source-initiative",
          "repository-name": "community-driven-project",
          "projects-title-filter": ["Community Outreach Initiatives", "CDD Project"] 
        }
      ]
  
      liv-doc-project-state-mining: true 
      liv-doc-structured-output: true
      liv-doc-group-output-by-topics: true
      liv-doc-output-formats: "mdoc"
  ```

---
## Expected Output

The Living Documentation Generator in Living Documentation regime is designed to produce an Issue Summary page (index.md) along with multiple detailed single issue pages.
The structure of pages is designed to work with the AbsaOSS [mdoc viewer](https://github.com/AbsaOSS/cps-mdoc-viewer) solution.

The regime's root output directory is named `liv-doc-regime`.


### Index Page Example

```markdown
---
title: Features
toolbar_title: Features
description_title: Living Documentation
description: >
  This is a comprehensive list and brief overview of all mined features.
date: 2024-12-12
weight: 0
---

<h1>Feature Summary page</h1>

Our project is designed with a myriad of features to ensure seamless user experience, top-tier functionality, and efficient operations. Here, you'll find a summarized list of all these features, their brief descriptions, and links to their detailed documentation.

<h2>Feature Overview</h2>

<div class="cps-table sortable searchable filterableByColumns paginator">

| Organization name | Repository name            | Issue 'Number - Title'              | Linked to project  | Project Status | Issue URL                                   |
|-------------------|----------------------------|-------------------------------------|--------------------|----------------|---------------------------------------------|
| AbsaOSS           | living-doc-example-project | [#89 - Test issue 2](features#test-issue-2)         | 🔴 | ---            | <a href='#' target='_blank'>GitHub link</a> |
| AbsaOSS           | living-doc-example-project | [#88 - Test issue](features#test-issue.md)          | 🟢 | Todo           | <a href='#' target='_blank'>GitHub link</a> |
| AbsaOSS           | living-doc-example-project | [#41 - Initial commit.](features#initial-commit.md) | 🟢 | Done           | <a href='#' target='_blank'>GitHub link</a> |
| AbsaOSS           | living-doc-example-project | [#33 - Example bugfix](features#example-bugfix.md)  | 🔴 | ---            | <a href='#' target='_blank'>GitHub link</a> |

</div>
```

- **Project Status** can have various values depending on the project, such as: Todo, Done, Closed, In Progress, In Review, Blocked, etc. 
These values can vary from project to project.
- The `---` symbol is used to indicate that an issue has no required project data.

### Issue Page Example

```markdown
---
title: "Advanced Book Search"
date: 2024-12-12
weight: 1
---

| Attribute         | Content                                     |
|-------------------|---------------------------------------------|
| Organization name | AbsaOSS                                     |
| Repository name   | living-doc-example-project                  |
| Issue number      | 17                                          |
| Title             | Advanced Book Search                        |
| State             | open                                        |
| Issue URL         | <a href='#' target='_blank'>GitHub link</a> |
| Created at        | 2023-12-12 11:34:52                         |
| Updated at        | 2023-12-13 10:24:58                         |
| Closed at         | None                                        |
| Labels            | feature                                     |
| Project title     | Book Store Living Doc Example project       |
| Status            | Todo                                        |
| Priority          | P1                                          |
| Size              | S                                           |
| MoSCoW            | ---                                         |

<h3>Issue Content</h3>

Users often struggle to find specific books in a large catalog. An advanced search feature would streamline this process, enhancing user experience.

#### Background
...
```

---
## Documentation Ticket Introduction

A **Documentation Ticket** is a small piece of documentation realized as a GitHub Issue dedicated to project documentation. Unlike development-focused tickets, Documentation Ticket can remain in open state continuously, evolving as updates are needed, and can be reopened or revised indefinitely. They are not directly tied to Pull Requests (PRs) but can be referenced for context.

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
- **Streamlined Management:** This avoids cross-project conflicts, board exclusions and enables specialized templates solely for documentation purposes.- **Focused Access Control:** This allows a small team to manage and edit documentation without interference, maintaining high-quality content.
- **Optimized Data Mining:** Supports easier and more efficient data extraction for feedback and review cycles through Release Notes.
- **Implementation Reflection:** Mirrors elements from the implementation repositories, providing a high-level knowledge source that is valuable for both business and technical teams.
- **Release Notes Integration:** Documentation can evolve based on insights from release notes, serving as a dynamic feedback loop back to the documentation repository.

---
## Living Documentation Regime Features

### Data Mining from GitHub Repositories

This is a build-in feature, that allows you to define which repositories should be included in the living documentation process. This essential process can not be deactivated inside of regime scope. By specifying repositories, you can focus on the most relevant projects for your documentation needs.

- **Activation**: This is a built-in feature, so it is always activated.
- **Default Behavior**: By default, the action will include all repositories defined in the repositories input parameter. Each repository is defined with its organization name, repository name, and query labels.

### Data Mining from GitHub Projects

This feature allows you to define which projects should be included in the living documentation process. By specifying projects, you can focus on the most relevant projects for your documentation needs.

- **Activation**: To activate this feature, set the `liv-doc-project-state-mining` input to true.
- **Non-Activated Behavior**: By default, when the feature is inactive, the action will include all projects linked to the repositories. This information is provided by the GitHub API.
- **Activated Example**: Use available options to customize which projects are included in the documentation.
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

The current output implementation is designed to work with the AbsaOSS [mdoc viewer](https://github.com/AbsaOSS/cps-mdoc-viewer) solution.
The presence of multiple _index.md files is necessary for the current solution to correctly generate the documentation structure.

- **Activation**: This is a built-in feature, so it is always activated.
- **Default Behavior**: By default, the action generates a single table that lists all issues from the defined repositories.

#### Structured Output

This feature allows you to generate structured output for the living documentation and see a summary `index.md` page for each fetched repository.

- **Activation**: To activate this feature, set the `liv-doc-structured-output` input to true.
- **Non-Activated Behavior**: By default, when the feature is inactive, the action generates all the documentation in a single directory.
- **Activated Example**: Use the structured output feature to organize the generated documentation by organization and repository name.
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

#### Output Grouped by Topics

The feature allows you to generate output grouped by topics. This feature is useful when grouping tickets by specific topics or themes.

To gain a better understanding of the term "Topic", refer to the [Labels](#labels) section.

- **Activation**: To activate this feature, set the `liv-doc-group-output-by-topics` input to true.
- **Non-Activated Behavior**: By default, when the feature is inactive, the action generates all the documentation in a single directory.
- **Activated Example**: Use the grouped output feature to organize the generated documentation by topics.
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
    
#### Output Formats

The feature allows you to select the output formats for the Living Documentation Regime.

- **Activation**: To activate this feature, set the liv-doc-output-formats input to a comma-separated string of your desired formats (e.g., "mdoc, pdf").
- **Non-Activated Behavior**: By default, the **mdoc** output format is selected.

Living Documentation Regime supports following output formats:
- **mdoc**: compatible with [CPS Mdoc Viewer project](https://github.com/AbsaOSS/cps-mdoc-viewer) 
