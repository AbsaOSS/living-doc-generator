# Living Documentation Generator

- [Motivation](#motivation)
- [Usage](#usage)
    - [Prerequisites](#prerequisites)
    - [Adding the Action to Your Workflow](#adding-the-action-to-your-workflow)
- [Action Configuration](#action-configuration)
    - [Environment Variables](#environment-variables)
    - [Inputs](#inputs)
- [Action Outputs](#action-outputs)
- [Features](#features)
    - [Report Page](#report-page)
- [Contribution Guidelines](#contribution-guidelines)
  - [License Information](#license-information)
  - [Contact or Support Information](#contact-or-support-information)

## Motivation

This action addresses the need for continuously updated documentation accessible to all team members and stakeholders. It achieves this by transforming raw data into an MDoc viewer-capable formatted output.
The raw data can be obtained from the action [liv-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) or a similar source.

---
## Usage

### Prerequisites

Before we begin, ensure you have the following prerequisites:
- GitHub Token with permission to fetch repository data such as Issues and Pull Requests,
- Python version 3.12 or higher.

### Adding the Action to Your Workflow

See the default action step definition:

```yaml
- name: Generate Living Documentation MDOC
  id: living_doc-generator-mdoc
  uses: AbsaOSS/living-doc-generator-mdoc@v0.1.0
  env:
    GITHUB-TOKEN: ${{ secrets.GITHUB_TOKEN }}  
  with:
    source: "TODO - path to the raw input file"  # Path to the raw input file containing the data to be processed.
    
    release: false                          # Enable release mode filtering. [NOT SUPPORTED YET]
    liv-doc-structured-output: true         # Enable structured output generation.
    report-page: true                       # Optional: enable report page generation.
    verbose-logging: true                   # Optional: project verbose (debug) logging feature de/activation
```

---
## Action Configuration

This section outlines the essential parameters common to all regimes that a user can define.

Configure the action by customizing the following parameters based on your needs:

### Environment Variables

| Variable Name  | Description             | Required | Usage                                                                                                                 |
|----------------|-------------------------|----------|-----------------------------------------------------------------------------------------------------------------------|
| `GITHUB_TOKEN` | GitHub token, that TODO | Yes      | Store it in the GitHub repository secrets and reference it in the workflow file using  `${{ secrets.GITHUB_TOKEN }}`. |

# TODO - je potreba pro generovani token? | pokud ano, je nutne ho brat z secrets? mam dojem, ze neni

### Inputs

| Input Name          | Description                                              | Required | Default | Usage                     | 
|---------------------|----------------------------------------------------------|----------|---------|---------------------------|
| `source`            | Path to the source file containing the data to be processed. | Yes      | N/A     | Specify the path to the raw input file. |
| `release`           | Enables or disables release filtering.                   | No       | `false` | Set to true to activate.  |
| `structured-output` | Enables or disables structured output generation. | No       | `false` | Set to true to activate.  |
| `report-page`       | Enables or disables the generation of [report pages](#report-page). | No       | `false` | Set to true to activate.  |
| `verbose-logging`   | Enables or disables verbose (debug) logging.             | No       | `false` | Set to true to activate.  |

---
## Action Outputs

The Living Documentation Generator MDOC action provides a main output path allowing users to locate and access the generated documentation easily. 
This output can be utilized in various ways within your CI/CD pipeline to ensure the documentation is effectively distributed and accessible.

- `output-path`
  - **Description**: The root output path to the directory where all generated living documentation files are stored.
  - **Usage**: 
   ``` yaml
    - name: Generate Living Documentation
      id: generate_mdoc
      ... rest of the action definition ...
      
    - name: Output Documentation Path
      run: echo "Generated documentation path: ${{ steps.generate_mdoc.outputs.output-path }}"            
    ```

---
## Features

### Report Page

The report page summarizes the errors found during the generation of living documents.

- **Activation**: Set the `report-page` input to true to activate this feature.
- **Non-Activated Behavior**: By default, when the feature is inactive, the errors are not listed in the output but are present in the log output.
- **Activated Example**: The report page is generated only, when some error are found during the generation of living documents.
  - `report-page: true` activates the generation of report page.
    ```markdown
    <h3>Report page</h3>
    
    This page summarizes the errors found during the generation of living documents.
    
    <h4>Living Documentation Regime</h4>
    
    | Error Type     | Issue                                     | Message                                  |
    | -------------- | ----------------------------------------- | ---------------------------------------- |
    | LabelError     | organization/example-project#19           | More than one Documentation label found. |
    ```

---
## Developer Guide

See this [Developer Guide](DEVELOPER.md) for more technical development-related information.

---
## Contribution Guidelines

We welcome contributions to the Living Documentation Generator, whether you're fixing bugs, improving documentation, or proposing new features.

#### How to Contribute

Before contributing, please review our [contribution guidelines](https://github.com/AbsaOSS/living-doc-generator/blob/master/CONTRIBUTING.md) for more detailed information.

### License Information

This project is licensed under the Apache License 2.0. This liberal license allows you great freedom in using, modifying, and distributing this software while also providing an express grant of patent rights from contributors to users.

For more details, see the [LICENSE](https://github.com/AbsaOSS/living-doc-generator/blob/master/LICENSE) file in the repository.

### Contact or Support Information

If you need help with using or contributing to Living Documentation Generator Action, or if you have any questions or feedback, don't hesitate to reach out:

- **Issue Tracker**: For technical issues or feature requests, use the [GitHub Issues page](https://github.com/AbsaOSS/living-doc-generator/issues).
- **Discussion Forum**: For general questions and discussions, join our [GitHub Discussions forum](https://github.com/AbsaOSS/living-doc-generator/discussions).
