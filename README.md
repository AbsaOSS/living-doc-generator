# Living Documentation Generator

- [Motivation](#motivation)
- [Mining Regimes](#mining-regimes)
- [Usage](#usage)
    - [Prerequisites](#prerequisites)
    - [Adding the Action to Your Workflow](#adding-the-action-to-your-workflow)
- [Action Configuration](#action-configuration)
    - [Environment Variables](#environment-variables)
    - [Inputs](#inputs)
      - [Base Inputs](#base-inputs)
      - [Regime Inputs](#regime-inputs)
- [Action Outputs](#action-outputs)
- [Living Documentation Generator Features](#living-documentation-generator-features)
    - [Report Page](#report-page)
- [How-to](#how-to)
  - [How to Create a Token with Required Scope](#how-to-create-a-token-with-required-scope)
  - [How to Store Token as a Secret](#how-to-store-token-as-a-secret)
- [Contribution Guidelines](#contribution-guidelines)
  - [License Information](#license-information)
  - [Contact or Support Information](#contact-or-support-information)

## Planning

| Task                      | Description                                                             | Status      | Due Date |
|---------------------------|-------------------------------------------------------------------------|-------------|----------|
| Released v0.1.0 PoC       | Initial proof of concept release                                       | Done        | 10/2024  |
| Report page               | Introduce report page, No Topic chapter, filtering, and detection code | Done        | 01/2025  |
| Output generators         | Make the solution more general and support easy format switching       | In progress | 03/2025  |
| User Story mining         | Mining of User Stories and integrating as a new output type            | Planned     | 2025     |
| Requirements mining       | Mining of Requirements and integrating as a new output type            | Planned     | 2025     |
| Support of test headers mining | Define test header formats, mine data, and enhance coverage matrix | Planned     | TBD      |
| Support of coverage matrix | Connect test headers with documented types and integrate as output    | Planned     | TBD      |
| Release notes mining      | Mine repositories release information and integrate as output type     | Planned     | TBD      |
| CI jobs mining            | Mine GH workflow files, analyze, and integrate as output type         | Planned     | TBD      |
| Incidents mining          | Mine registered incidents and integrate as a new output type          | Planned     | TBD      |
| User Guide generation     | Generate a User Guide based on User Stories and integrate as output   | Planned     | TBD      |

## Motivation

Addresses the need for continuously updated documentation accessible to all team members and stakeholders. Achieves this by extracting information directly from GitHub issues and integrating this functionality to deliver real-time, mdoc viewer capable formatted output. Ensures everyone has the most current project details, fostering better communication and efficiency throughout development.

---
## Mining Regimes

This Generator supports multiple mining regimes, each with its own unique functionality. Read more about the regimes at their respective links:
- [Living documentation regime documentation](living_documentation_regime/README.md)

---
## Usage

### Prerequisites

Before we begin, ensure you have a following prerequisites:
- GitHub Token with permission to fetch repository data such as Issues and Pull Requests,
- Python version 3.12 or higher.

### Adding the Action to Your Workflow

See the default action step definition:

```yaml
- name: Generate Living Documentation
  id: generate_living_doc
  uses: AbsaOSS/living-doc-generator@v0.4.0
  env:
    GITHUB-TOKEN: ${{ secrets.REPOSITORIES_ACCESS_TOKEN }}  
  with:
    report-page: true
    
    # regimes de/activation
    liv-doc-regime: false
```

> **Report page**: The report page is a summary of the errors found during the generation of living documents.

See the default action step definitions for each regime:

- [Living documentation regime default step definition](living_documentation_regime/README.md#adding-livdoc-regime-to-the-workflow)

#### Full Example of Action Step Definition

See the full example of action step definition (in example are used non-default values):

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
    
    # LivDoc Regime configuration
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
          },
          {
            "organization-name": "open-source-initiative",
            "repository-name": "community-driven-project",
            "query-labels": ["improvement"],
            "projects-title-filter": ["Community Outreach Initiatives", "CDD Project"] 
          }
        ]
    liv-doc-project-state-mining: true     # project state mining feature de/activation
    liv-doc-structured-output: true        # structured output feature de/activation
    liv-doc-group-output-by-topics: true   # group output by topics feature de/activation
    liv-doc-output-formats: "mdoc"         # output formats selection, supported: mdoc
```

---
## Action Configuration

This section outlines the essential parameters that are common to all regimes a user can define.

Configure the action by customizing the following parameters based on your needs:

### Environment Variables

| Variable Name                | Description                                                                                                | Required | Usage                                                                                                                              |
|------------------------------|------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------------------------|
| `REPOSITORIES_ACCESS_TOKEN`  | GitHub access token for authentication, that has permission to access all defined repositories / projects. | Yes      | Store it in the GitHub repository secrets and reference it in the workflow file using  `${{ secrets.REPOSITORIES_ACCESS_TOKEN }}`. |

- **Example**:
  ```yaml
  env:
    GITHUB-TOKEN: ${{ secrets.REPOSITORIES_ACCESS_TOKEN }}
  ```

The way how to generate and store a token into the GitHub repository secrets is described in the [support chapter](#how-to-create-a-token-with-required-scope).

### Inputs

In this GitHub action, there are two types of user inputs:
- **[Base Inputs](#base-inputs)**: Inputs that are common to all regimes.
- **[Regime Inputs](#regime-inputs)**: Inputs that are specific to a particular regime.

#### Base Inputs

| Input Name        | Description                                      | Required | Default | Usage                     | 
|-------------------|--------------------------------------------------|----------|---------|---------------------------|
| `liv-doc-regime`  | Enables or disables Living Documentation regime. | Yes      | N/A     | Set to true to activate.  |
| `verbose-logging` | Enables or disables verbose (debug) logging.     | No       | `false`   | Set to true to activate.  |
| `report-page`     | Enables or disables the report page generation.  | No       | `true`    | Set to true to activate.  |

- **Examples**
```yaml
with:
  liv-doc-regime: true      # Activation of Living Documentation regime
  
  verbose-logging: true     # Activation of verbose (debug) logging
  report-page: true         # Allowing creation of report page - each regime can fill it with errors.
```

#### Regime Inputs

Regime-specific inputs and outputs are detailed in the respective regime's documentation:

- [Living documentation regime specific inputs](living_documentation_regime/README.md#regime-configuration)
    
---
## Action Outputs

The Living Documentation Generator action provides a main output path that allows users to locate and access the generated documentation easily. 
This output can be utilized in various ways within your CI/CD pipeline to ensure the documentation is effectively distributed and accessible.

- `output-path`
  - **Description**: The root output path to the directory where all generated living documentation files are stored.
  - **Usage**: 
   ``` yaml
    - name: Generate Living Documentation
      id: generate_doc
      ... rest of the action definition ...
      
    - name: Output Documentation Path
      run: echo "Generated documentation path: ${{ steps.generate_doc.outputs.output-path }}"            
    ```

---
## Living Documentation Generator Features

### Report Page

The report page is a summary of the errors found during the generation of living documents.

- **Activation**: To activate this feature, set the `report-page` input to true.
- **Non-Activated Behavior**: By default, when the feature is inactive, the errors are not listed in the output.
- **Activated Example**: The report page is generated only, when some error are found during the generation of living documents.
  - `report-page: true` activates the generation of report page.
    ```markdown
    <h3>Report page</h3>
    
    This page contains a summary of the errors found during the generation of living documents.
    
    <h4>Living Documentation Regime</h4>
    
    | Error Type     | Issue                                     | Message                          |
    | -------------- | ----------------------------------------- | -------------------------------- |
    | TopicError     | absa-group/living-doc-example-project#89  | No Topic label found.            |
    | TopicError     | absa-group/living-doc-example-project#19  | More than one Topic label found. |
    ```

---
## How-to

This section aims to help the user walk through different processes, such as:
- [Generating and storing a token as a secret](#how-to-create-a-token-with-required-scope)

### How to Create a Token with Required Scope

1. Go to your GitHub account settings.
2. Click on the `Developer settings` tab in the left sidebar.
3. In the left sidebar, click on `Personal access tokens` and choose `Tokens (classic)`.
4. Click on the `Generate new token` button and choose `Generate new token (classic)`.
5. Optional - Add a note, what is token for and choose token expiration.
6. Select ONLY bold scope options below:
   - **workflow**
   - write:packages
     - **read:packages**
   - admin:org
     - **read:org**
     - **manage_runners:org**
   - admin:public_key
     - **read:public_key**
   - admin:repo_hook
     - **read:repo_hook**
   - admin:enterprise
     - **manage_runners:enterprise**
     - **read:enterprise**
   - audit_log
     - **read:audit_log**
   - project
     - **read:project**
7. Copy the token value somewhere, because you won't be able to see it again.
8. Authorize new token to organization you want to fetch from.

### How to Store Token as a Secret

1. Go to the GitHub repository, from which you want to run the GitHub Action.
2. Click on the `Settings` tab in the top bar.
3. In the left sidebar, click on `Secrets and variables` > `Actions`.
4. Click on the `New repository secret` button.
5. Name the token `REPOSITORIES_ACCESS_TOKEN` and paste the token value.

---
## Contribution Guidelines

We welcome contributions to the Living Documentation Generator! Whether you're fixing bugs, improving documentation, or proposing new features, your help is appreciated.

#### How to Contribute

Before contributing, please review our [contribution guidelines](https://github.com/AbsaOSS/living-doc-generator/blob/master/CONTRIBUTING.md) for more detailed information.

### License Information

This project is licensed under the Apache License 2.0. It is a liberal license that allows you great freedom in using, modifying, and distributing this software, while also providing an express grant of patent rights from contributors to users.

For more details, see the [LICENSE](https://github.com/AbsaOSS/living-doc-generator/blob/master/LICENSE) file in the repository.

### Contact or Support Information

If you need help with using or contributing to Living Documentation Generator Action, or if you have any questions or feedback, don't hesitate to reach out:

- **Issue Tracker**: For technical issues or feature requests, use the [GitHub Issues page](https://github.com/AbsaOSS/living-doc-generator/issues).
- **Discussion Forum**: For general questions and discussions, join our [GitHub Discussions forum](https://github.com/AbsaOSS/living-doc-generator/discussions).
