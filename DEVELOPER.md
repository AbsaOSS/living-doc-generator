# Living Documentation Generator - for Developers

- [Project Setup](#project-setup)
- [Run Scripts Locally](#run-scripts-locally)
- [Run Pylint Check Locally](#run-pylint-check-locally)
- [Run Black Tool Locally](#run-black-tool-locally)
- [Run mypy Tool Locally](#run-mypy-tool-locally)
- [Run Unit Test](#run-unit-test)
- [Code Coverage](#code-coverage)
- [Releasing](#releasing)

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
              "projects-title-filter": ["Project Title 1"]
            }
          ]'
export INPUT_LIV_DOC_PROJECT_STATE_MINING=true
export INPUT_LIV_DOC_STRUCTURED_OUTPUT=true
export INPUT_LIV_DOC_GROUP_OUTPUT_BY_TOPICS=true
export INPUT_LIV_DOC_OUTPUT_FORMATS="mdoc"

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
black living_documentation_regime/living_documentation_generator.py 
``` 

### Expected Output

This is the console expected output example after running the tool:
```
All done! ✨ 🍰 ✨
1 file reformatted.
```

---

## Run mypy Tool Locally

This project uses the [my[py]](https://mypy.readthedocs.io/en/stable/) 
tool which is a static type checker for Python.

> Type checkers help ensure that you’re using variables and functions in your code correctly.
> With mypy, add type hints (PEP 484) to your Python programs, 
> and mypy will warn you when you use those types incorrectly.

my[py] configuration is in `pyptoject.toml` file.

Follow these steps to format your code with my[py] locally:

### Run my[py]

Run my[py] on all files in the project.
```shell
  mypy .
```

To run my[py] check on a specific file, follow the pattern `mypy <path_to_file>/<name_of_file>.py --check-untyped-defs`.

Example:
```shell
   mypy living_documentation_regime/living_documentation_generator.py
``` 

### Expected Output

This is the console expected output example after running the tool:
```
Success: no issues found in 1 source file
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
