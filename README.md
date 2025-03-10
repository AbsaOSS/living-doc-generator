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
- [Project Setup](#project-setup)
- [Run Scripts Locally](#run-scripts-locally)
- [Run Pylint Check Locally](#run-pylint-check-locally)
- [Run Black Tool Locally](#run-black-tool-locally)
- [Run Unit Test](#run-unit-test)
- [Code Coverage](#code-coverage)
- [Releasing](#releasing)
- [Support](#support)
    - [How to Create a Token with Required Scope](#how-to-create-a-token-with-required-scope)
    - [How to Store Token as a Secret](#how-to-store-token-as-a-secret)
- [Contribution Guidelines](#contribution-guidelines)
  - [License Information](#license-information)
  - [Contact or Support Information](#contact-or-support-information)

![vision.jpg](img/vision.jpg)

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
    # regimes de/activation
    liv-doc-regime: false
```

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
    liv-doc-output-formats: "mdoc, pdf"    # output formats selection for the Living Documentation Regime
```

---
## Action Configuration

This section outlines the essential parameters that are common to all regimes a user can define.

Configure the action by customizing the following parameters based on your needs:

### Environment Variables

- **REPOSITORIES_ACCESS_TOKEN**:
  - **Description**: GitHub access token for authentication, that has a permission to access all defined repositories / projects.
  - **Usage**: Store it in the GitHub repository secrets and reference it in the workflow file using  `${{ secrets.REPOSITORIES_ACCESS_TOKEN }}`.
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
- **liv-doc-regime** (required)
  - **Description**: Enables or disables Living Documentation regime.
  - **Usage**: Set to true to activate.
  - **Example**:
    ```yaml
    with:
      liv-doc-regime: true
    ```

- **verbose-logging** (optional, `default: false`)
  - **Description**: Enables or disables verbose (debug) logging.
  - **Usage**: Set to true to activate.
  - **Example**:
    ```yaml
    with:
      verbose-logging: true
    ```
    
- **report-page** (optional, `default: true`)
  - **Description**: Enables or disables the report page generation.
  - **Usage**: Set to true to activate.
  - **Example**:
    ```yaml
    with:
      report-page: true
    ```
    
#### Regime Inputs

Regime-specific inputs are detailed in the respective regime's documentation:
- [Living documentation regime specific inputs](living_documentation_regime/README.md#regime-configuration)
    
---
## Action Outputs

The Living Documentation Generator action provides a key output that allows users to locate and access the generated documentation easily. This output can be utilized in various ways within your CI/CD pipeline to ensure the documentation is effectively distributed and accessible.
The output-path can not be an empty string. It can not aim to the root and other project directories as well.

- **output-path**
  - **Description**: This output provides the path to the directory where the generated living documentation files are stored.
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
## Project Setup

If you need to build the action locally, follow these steps for project setup:

### Prepare the Environment

```shell
python3 --version
```

### Set Up Python Environment

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---
## Run Scripts Locally

If you need to run the scripts locally, follow these steps:

### Create the Shell Script

Create the shell file in the root directory. We will use `run_script.sh`.
```shell
touch run_script.sh
```
Add the shebang line at the top of the sh script file.
```
#!/bin/sh
```

### Set the Environment Variables

Set the configuration environment variables in the shell script following the structure below.
The generator supports mining in multiple regimes, so you can use just the environment variables you need.
Also make sure that the INPUT_GITHUB_TOKEN is configured in your environment variables.
```
# Essential environment variables for GitHub Action functionality
export INPUT_GITHUB_TOKEN=$(printenv GITHUB_TOKEN)
export INPUT_LIV_DOC_REGIME=true
export INPUT_VERBOSE_LOGGING=true
export INPUT_REPORT_PAGE=true

# Environment variables for LivDoc regime functionality
export INPUT_LIV_DOC_REPOSITORIES='[
            {
              "organization-name": "Organization Name",
              "repository-name": "example-project",
              "query-labels": ["feature", "bug"],
              "projects-title-filter": ["Project Title 1"]
            }
          ]'
export INPUT_LIV_DOC_PROJECT_STATE_MINING=true
export INPUT_LIV_DOC_STRUCTURED_OUTPUT=true
export INPUT_LIV_DOC_GROUP_OUTPUT_BY_TOPICS=true
export INPUT_LIV_DOC_OUTPUT_FORMATS="mdoc"
```

### Running the script locally

For running the GitHub action incorporate these commands into the shell script and save it.
```
python3 main.py
```
The whole script should look like this example:
```
#!/bin/sh

# Essential environment variables for GitHub Action functionality
export INPUT_GITHUB_TOKEN=$(printenv GITHUB_TOKEN)
export INPUT_LIV_DOC_REGIME=true
export INPUT_VERBOSE_LOGGING=true
export INPUT_REPORT_PAGE=true

# Environment variables for LivDoc regime functionality
export INPUT_LIV_DOC_REPOSITORIES='[
            {
              "organization-name": "Organization Name",
              "repository-name": "example-project",
              "query-labels": ["feature", "bug"],
              "projects-title-filter": ["Project Title 1"]
            }
          ]'
export INPUT_LIV_DOC_PROJECT_STATE_MINING=true
export INPUT_LIV_DOC_STRUCTURED_OUTPUT=true
export INPUT_LIV_DOC_GROUP_OUTPUT_BY_TOPICS=true

python3 main.py
```

### Make the Script Executable

From the terminal that is in the root of this project, make the script executable:
```shell
chmod +x run_script.sh
```

### Run the Script

```shell
./run_script.sh
```

---
## Run Pylint Check Locally

This project uses [Pylint](https://pypi.org/project/pylint/) tool for static code analysis.
Pylint analyses your code without actually running it.
It checks for errors, enforces, coding standards, looks for code smells etc.
We do exclude the `tests/` file from the pylint check.

Pylint displays a global evaluation score for the code, rated out of a maximum score of 10.0.
We are aiming to keep our code quality high above the score 9.5.

Follow these steps to run Pylint check locally:

### Set Up Python Environment

From terminal in the root of the project, run the following command:

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This command will also install a Pylint tool, since it is listed in the project requirements.

### Run Pylint

Run Pylint on all files that are currently tracked by Git in the project.
```shell
pylint $(git ls-files '*.py')
```

To run Pylint on a specific file, follow the pattern `pylint <path_to_file>/<name_of_file>.py`.

Example:
```shell
pylint living_documentation_regime/living_documentation_regime.py
``` 

### Expected Output

This is the console expected output example after running the tool:
```
************* Module main
main.py:30:0: C0116: Missing function or method docstring (missing-function-docstring)

------------------------------------------------------------------
Your code has been rated at 9.41/10 (previous run: 8.82/10, +0.59)
```

---
## Run Black Tool Locally

This project uses the [Black](https://github.com/psf/black) tool for code formatting.
Black aims for consistency, generality, readability and reducing git diffs.
The coding style used can be viewed as a strict subset of PEP 8.

The project root file `pyproject.toml` defines the Black tool configuration.
In this project we are accepting the line length of 120 characters.
We also do exclude the `tests/` file from the black formatting.

Follow these steps to format your code with Black locally:

### Set Up Python Environment

From terminal in the root of the project, run the following command:

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This command will also install a Black tool, since it is listed in the project requirements.

### Run Black

Run Black on all files that are currently tracked by Git in the project.
```shell
black $(git ls-files '*.py')
```

To run Black on a specific file, follow the pattern `black <path_to_file>/<name_of_file>.py`.

Example:
```shell
black living_documentation_regime/living_documentation_regime.py
``` 

### Expected Output

This is the console expected output example after running the tool:
```
All done! ✨ 🍰 ✨
1 file reformatted.
```

---
## Run Unit Test

Unit tests are written using Pytest framework. To run alle the tests, use the following command:
```shell
pytest --ignore=tests/integration tests/
```

You can modify the directory to control the level of detail or granularity as per your needs.

To run specific test, write the command following the pattern below:
```shell
pytest tests/utils/test_utils.py::test_make_issue_key
```

---
## Code Coverage

This project uses [pytest-cov](https://pypi.org/project/pytest-cov/) plugin to generate test coverage reports.
The objective of the project is to achieve a minimal score of 80 %. We do exclude the `tests/` file from the coverage report.

To generate the coverage report, run the following command:
```shell
pytest --ignore=tests/integration --cov=. tests/ --cov-fail-under=80 --cov-report=html
```

See the coverage report on the path:

```shell
open htmlcov/index.html
```

---
## Releasing

This project uses GitHub Actions for deployment draft creation. The deployment process is semi-automated by a workflow defined in `.github/workflows/release_draft.yml`.

- **Trigger the workflow**: The `release_draft.yml` workflow is triggered on workflow_dispatch.
- **Create a new draft release**: The workflow creates a new draft release in the repository.
- **Finalize the release draft**: Edit the draft release to add a title, description, and any other necessary details related to GitHub Action.
- **Publish the release**: Once the draft is ready, publish the release to make it available to the public.

---
## Support

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
