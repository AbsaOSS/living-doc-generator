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
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---
## Run Scripts Locally

If you need to run the scripts locally, follow these steps:

### Create the Shell Script

Create the shell file in the root directory. We will use `run_local.sh`.
```shell
touch run_local.sh
```

### Fill the Shell Script

```
#!/bin/sh

# Essential environment variables for GitHub Action functionality
export INPUT_SOURCE="TODO"

# Optional environment variables
export INPUT_RELEASE=false
export INPUT_STRUCTURED_OUTPUT=true
export INPUT_REPORT_PAGE=true
export INPUT_VERBOSE_LOGGING=true

python3 main.py
```

### Make the Script Executable

From the terminal that is in the root of this project, make the script executable:
```shell
chmod +x run_local.sh
```

### Run the Script

```shell
./run_local.sh
```

---
## Run Pylint Check Locally

This project uses the [Pylint](https://pypi.org/project/pylint/) tool for static code analysis.
Pylint analyses your code without actually running it.
It checks for errors, enforces coding standards, and looks for code smells, among other things.
We do exclude the `tests/` file from the pylint check.

Pylint displays a global evaluation score for the code, rated out of a maximum score of 10.0.
We aim to maintain a code quality score above 9.5.

Follow these steps to run a Pylint check locally:

### Set Up Python Environment

From the terminal in the root of the project, run the following command:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This command will also install a Pylint tool, since it is listed in the project requirements.

### Run Pylint

Run Pylint on all files that Git currently tracks in the project.
```shell
pylint $(git ls-files '*.py')
```

To run Pylint on a specific file, follow the pattern `pylint <path_to_file>/<name_of_file>.py`.

Example:
```shell
pylint living_doc_generator/living_doc_generator.py
``` 

### Expected Output

This is the console's expected output example after running the tool:
```
************* Module main
main.py:30:0: C0116: Missing function or method docstring (missing-function-docstring)

------------------------------------------------------------------
Your code has been rated at 9.41/10 (previous run: 8.82/10, +0.59)
```

---
## Run Black Tool Locally

This project uses the [Black](https://github.com/psf/black) tool for code formatting.
Black aims for consistency, generality, readability, and reducing git diffs.
The coding style used can be viewed as a strict subset of the PEP 8 guidelines.

The project root file `pyproject.toml` defines the Black tool configuration.
In this project, we are accepting a line length of 120 characters.
We also exclude the `tests/` file from the black formatting.

Follow these steps to format your code with Black locally:

### Set Up Python Environment

From the terminal in the root of the project, run the following command:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This command will also install a Black tool, since it is listed in the project requirements.

### Run Black

Run 'Black' on all files currently tracked by Git in the project.
```shell
black $(git ls-files '*.py')
```

To run Black on a specific file, follow the pattern `black <path_to_file>/<name_of_file>.py`.

Example:
```shell
black living_doc_generator/living_doc_generator.py 
``` 

### Expected Output

This is the console's expected output example after running the tool:
```
All done! ✨ 🍰 ✨
1 file reformatted.
```

---

## Run mypy Tool Locally

This project uses the [mypy](https://mypy.readthedocs.io/en/stable/) 
A tool that is a static type checker for Python.

> Type checkers help ensure that you’re using variables and functions in your code correctly.
> With mypy, add type hints (PEP 484) to your Python programs, 
> and mypy will warn you when you use those types incorrectly.

My[py] configuration is in the `pyproject.toml` file.

Follow these steps to format your code with my[py] locally:

### Run my[py]

Run my[py] on all files in the project.
```shell
  mypy .
```

To run my[py] check on a specific file, follow the pattern `mypy <path_to_file>/<name_of_file>.py --check-untyped-defs`.

Example:
```shell
   mypy living_doc_generator/living_doc_generator.py
``` 

### Expected Output

This is the console's expected output example after running the tool:
```
Success: no issues found in 1 source file
```

---


## Run Unit Test

Unit tests are written using the Pytest framework. To run all the tests, use the following command:
```shell
pytest --ignore=tests/integration tests/
```

You can modify the directory to control the level of detail or granularity as per your needs.

To run a specific test, write the command following the pattern below:
```shell
pytest tests/utils/test_utils.py::test_make_issue_key
```

---
## Code Coverage

This project uses the [pytest-cov](https://pypi.org/project/pytest-cov/) plugin to generate test coverage reports.
The objective of the project is to achieve a score of at least 80%. We do exclude the `tests/` file from the coverage report.

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

This project utilizes GitHub Actions for creating deployment drafts. The deployment process is semi-automated by a workflow defined in `.github/workflows/release_draft.yml`.

- **Trigger the workflow**: The `release_draft.yml` workflow is triggered on workflow_dispatch.
- **Create a new draft release**: The workflow creates a new draft release in the repository.
- **Finalize the release draft**: Edit the draft release to add a title, description, and any other necessary details related to GitHub Actions.
- **Publish the release**: Once the draft is ready, publish the release to make it publicly available.
