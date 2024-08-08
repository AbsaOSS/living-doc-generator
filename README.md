# Living Documentation Generator

- [Motivation](#motivation)
- [Usage](#usage)
    - [Prerequisites](#prerequisites)
    - [Adding the Action to Your Workflow](#adding-the-action-to-your-workflow)
- [Action Configuration](#action-configuration)
    - [Environment Variables](#environment-variables)
    - [Inputs](#inputs)
    - [Features de/activation](#features-deactivation)
    - [Features Configuration](#features-configuration)
- [Action Outputs](#action-outputs)
- [Expected Output](#expected-output)
    - [Index page example](#index-page-example)
    - [Issue page example](#issue-page-example)
- [Project Setup](#project-setup)
- [Run Scripts Locally](#run-scripts-locally)
- [Run unit test](#run-unit-test)
- [Deployment](#deployment)
- [Features](#features)
    - [Data Mining from GitHub Repositories](#data-mining-from-github-repositories)
    - [Data Mining from GitHub Projects](#data-mining-from-github-projects)
    - [Living Documentation Page Generation](#living-documentation-page-generation)
- [Contribution Guidelines](#contribution-guidelines)
- [License Information](#license-information)
- [Contact or Support Information](#contact-or-support-information)

A tool designed to data-mine GitHub repositories for issues containing project documentation (e.g. tagged with feature-related labels). This tool automatically generates comprehensive living documentation in Markdown format, providing detailed feature overview pages and in-depth feature descriptions.

## Motivation
Addresses the need for continuously updated documentation accessible to all team members and stakeholders. Achieves this by extracting information directly from GitHub issues and integrating this functionality to deliver real-time, markdown-formatted output. Ensures everyone has the most current project details, fostering better communication and efficiency throughout development.

## Usage
### Prerequisites
Before we begin, ensure you have a GitHub Token with permission to fetch repository data such as Issues and Pull Requests.

### Adding the Action to Your Workflow

See the default action step definition:

```yaml
- name: Generate Living Documentation
  id: generate_living_doc
  uses: AbsaOSS/living-doc-generator@v0.1.0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  
  with:
    repositories: '[
      {
        "owner": "fin-services",
        "repo-name": "investment-app",
        "query-labels": ["feature", "enhancement"]
      },
      {
        "owner": "health-analytics",
        "repo-name": "patient-data-analysis",
        "query-labels": ["functionality"]
      },
      {
        "owner": "open-source-initiative",
        "repo-name": "community-driven-project",
        "query-labels": ["improvement"]
      }
    ]'
  ```

See the full example of action step definition (in example are used non-default values):

```yaml
- name: Generate Living Documentation
  id: generate_living_doc
  uses: AbsaOSS/living-doc-generator@v0.1.0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  
  with:
    # project state mining de/activation
    project-state-mining: true
    
    # feature to filter projects 
    projects-title-filter": ["Community Outreach Initiatives", "Health Data Analysis"]

    # inputs
    repositories: '[
      {
        "owner": "fin-services",
        "repo-name": "investment-app",
        "query-labels": ["feature", "enhancement"]
      },
      {
        "owner": "health-analytics",
        "repo-name": "patient-data-analysis",
        "query-labels": ["functionality"]
      },
      {
        "owner": "open-source-initiative",
        "repo-name": "community-driven-project",
        "query-labels": ["improvement"]
      }
    ]'
    output-path: "/output/directory/path"
```



## Action Configuration
Configure the action by customizing the following parameters based on your needs:

### Environment Variables
- **GITHUB_TOKEN** (required):
  - **Description**: Your GitHub token for authentication. 
  - **Usage**: Store it as a secret and reference it in the workflow file using  `${{ secrets.GITHUB_TOKEN }}`.
  - **Example**:
    ```yaml
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    ```
    
### Inputs
- **repositories** (required)
  - **Description**: A JSON string defining the repositories to be included in the documentation generation.
  - **Usage**: List each repository with its organization name, repository name, and query labels.
  - **Example**:
    ```yaml
    with:
      repositories: '[
        {
          "owner": "fin-services",
          "repo-name": "investment-app",
          "query-labels": ["feature", "enhancement"]
        },
        {
          "owner": "health-analytics",
          "repo-name": "patient-data-analysis",
          "query-labels": ["functionality"]
        },
        {
          "owner": "open-source-initiative",
          "repo-name": "community-driven-project",
          "query-labels": ["improvement"]
        }
      ]'
      output-path: "/output/directory/path"
    ```

### Features de/activation
- **project-state-mining** (optional, `default: false`)
  - **Description**: Enables or disables the mining of project state data from [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects).
  - **Usage**: Set to true to activate.
  - **Example**:
    ```yaml
    with:
      project-state-mining: true
    ```
    
### Features Configuration
- **projects-title-filter** (optional, `default: []`)
  - **Description**: Filters the projects by titles. Only projects with these titles will be considered.
  - **Usage**: Provide a list of project titles to filter.
  - **Example**:
    ```yaml
    with:
      projects-title-filter: ["Community Outreach Initiatives", "Health Data Analysis"]
    ```

## Action Outputs
The Living Documentation Generator action provides a key output that allows users to locate and access the generated documentation easily. This output can be utilized in various ways within your CI/CD pipeline to ensure the documentation is effectively distributed and accessible.

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
  
## Expected Output
The Living Documentation Generator is designed to produce an Issue Summary page (index.md) along with multiple detailed single issue pages.

### Index page example
```markdown
# Issue Summary page

Our project is designed with a myriad of issues to ensure seamless user experience, top-tier functionality, and efficient operations.
Here, you'll find a summarized list of all these issues, their brief descriptions, and links to their detailed documentation.

## Issue Overview
| Organization name| Repository name            | Issue 'Number - Title'                        | Linked to project | Project Status | Issue URL  |
|------------------|----------------------------|-----------------------------------------------|-------------------|----------------|------------|
|AbsaOSS           | living-doc-example-project | [#89 - Test issue 2](89_test_issue_2.md)      | 🔴                | ---            |[GitHub](#) |
|AbsaOSS           | living-doc-example-project | [#88 - Test issue](88_test_issue.md)          | 🟢                | Todo           |[GitHub](#) |
|AbsaOSS           | living-doc-example-project | [#41 - Initial commit.](41_initial_commit.md) | 🟢                | Done           |[GitHub](#) |
|AbsaOSS           | living-doc-example-project | [#33 - Example bugfix](33_example_bugfix.md)  | 🔴                | ---            |[GitHub](#) |
```

### Issue page example

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

## Project Setup
If you need to build the action locally, follow these steps:

### Prepare the Environment
```
python3 --version
```

### Set Up Python Environment
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run Scripts Locally
If you need to run the scripts locally, follow these steps:

### Create the shell script
Create the shell file in the root directory. We will use `run_script.sh`.
```shell
touch run_script.sh
```
Add the shebang line at the top of the sh script file.
```
#!/bin/sh
```

### Set the environment variables
Set the configuration environment variables in the shell script following the structure below. 
Also make sure that the GITHUB_TOKEN is configured in your environment variables.
```
export INPUT_GITHUB_TOKEN=$(printenv GITHUB_TOKEN)
export INPUT_PROJECT_STATE_MINING="true"
export INPUT_PROJECTS_TITLE_FILTER="[]"
export INPUT_REPOSITORIES='[
            {
              "owner": "Organization Name",
              "repo-name": "example-project",
              "query-labels": ["feature", "bug"]
            }
          ]'
export INPUT_OUTPUT_PATH="/output/directory/path
```

### Running the script locally
For running the GitHub action incorporate these commands into the shell script and save it.
```
cd src || exit 1

python3 main.py

cd .. || exit 1
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

## Run unit test
TODO - check this chapter and update by latest state
### Launch unit tests
```
pytest
```

### To run specific tests or get verbose output:
```
pytest -v  # Verbose mode
pytest path/to/test_file.py  # Run specific test file
```

### To check Test Coverage:
```
pytest --cov=../scripts
```

### After running the tests
```
deactivate
```

### Commit Changes
After testing and ensuring that everything is functioning as expected, prepare your files for deployment:

```
git add action.yml dist/index.js  # Adjust paths as needed
git commit -m "Prepare GitHub Action for deployment"
git push
```

## Deployment
This project uses GitHub Actions for deployment draft creation. The deployment process is semi-automated by a workflow defined in `.github/workflows/release_draft.yml`.

- **Trigger the workflow**: The `release_draft.yml` workflow is triggered on workflow_dispatch.
- **Create a new draft release**: The workflow creates a new draft release in the repository.
- **Finalize the release draft**: Edit the draft release to add a title, description, and any other necessary details related to GitHub Action.
- **Publish the release**: Once the draft is ready, publish the release to make it available to the public.


## Features

### Data Mining from GitHub Repositories

This feature allows you to define which repositories should be included in the living documentation process. By specifying repositories, you can focus on the most relevant projects for your documentation needs.

- **Default Behavior**: By default, the action will include all repositories defined in the repositories input parameter. Each repository is defined with its organization name, repository name, and query labels.

### Data Mining from GitHub Projects

This feature allows you to define which projects should be included in the living documentation process. By specifying projects, you can focus on the most relevant projects for your documentation needs.

- **Default Behavior**: By default, the action will include all projects defined in the repositories. This information is provided by the GitHub API.
- **Non-default Example**: Use available options to customize which projects are included in the documentation.
  - `project-state-mining: false` deactivates the mining of project state data from GitHub Projects. If set to **false**, project state data will not be included in the generated documentation and project related configuration options will be ignored. 
  - `projects-title-filter: ["Community Outreach Initiatives", "Health Data Analysis"]` filters the projects by titles, including only projects with these titles.

### Living Documentation Page Generation

The goal is to provide a straightforward view of all issues in a single table, making it easy to see the overall status and details of issues across repositories.

- **Default Behavior**: By default, the action generates a single table that lists all issues from the defined repositories.

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
