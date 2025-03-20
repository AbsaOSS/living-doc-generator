import os.path
from pathlib import Path

import pytest

from living_documentation_regime.exporter.mdoc_exporter import MdocExporter
from living_documentation_regime.model.consolidated_issue import ConsolidatedIssue
from living_documentation_regime.model.project_status import ProjectStatus


@pytest.fixture
def mdoc_exporter(tmp_path, mocker):
    """Fixture to create an instance of MdocExporter with modified template paths."""
    output_dir = os.path.join(tmp_path, "output")
    os.makedirs(output_dir, exist_ok=True)
    return MdocExporter(output_dir)

@pytest.fixture
def sample_issues():
    """Creates a set of sample issues for testing."""
    issue_1 = ConsolidatedIssue(repository_id="org/repo")
    issue_2 = ConsolidatedIssue(repository_id="org/repo")

    return {"ISSUE-1": issue_1, "ISSUE-2": issue_2}


@pytest.fixture
def sample_issue_linked_to_project():
    """Creates a sample issue with linked_to_project set to True."""
    issue: ConsolidatedIssue = ConsolidatedIssue(repository_id="org/repo")
    project_status: ProjectStatus = ProjectStatus()
    project_status.project_title = "Project Title"
    project_status.status = "In Progress"
    project_status.priority = "High"
    project_status.size = "Large"
    project_status.moscow = "Must Have"
    issue.update_with_project_data(project_status)
    return issue


def test_export_real_execution_all_enabled(mdoc_exporter, sample_issues, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=True)
    mocker.patch("action_inputs.ActionInputs.is_grouping_by_topics_enabled", return_value=True)

    # Act
    result = mdoc_exporter.export(issues=sample_issues)

    # Assert
    assert result is True
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "org", "repo", "NoTopic", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "org", "repo", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "org", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "report_page.md"))

    with open(os.path.join(mdoc_exporter._output_path, "org", "repo", "NoTopic", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "NoTopic"', "| org | repo | [#0 - ](features#) | 🔴 | --- |<a href='' target='_blank'>GitHub link</a> |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "org", "repo", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "repo"', "This section displays the living documentation for all topics within the repository: **repo** in a structured output."]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "org", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "org"', "This section displays the living documentation for all repositories within the organization: **org** in a structured output."]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "_index.md"), 'r') as file:
        content = file.read()
    expected = ['toolbar_title: Features', 'description_title: Living Documentation']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "report_page.md"), 'r') as file:
        content = file.read()
    expected = ['title: "Report page"', '<h3>Report page</h3>', "| TopicError | [org/repo#0]() | No Topic label found. |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."


def test_export_real_execution_no_project_mining(mdoc_exporter, sample_issues, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=False)
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=True)
    mocker.patch("action_inputs.ActionInputs.is_grouping_by_topics_enabled", return_value=True)

    # Act
    result = mdoc_exporter.export(issues=sample_issues)

    # Assert
    assert result is True
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "org", "repo", "NoTopic", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "org", "repo", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "org", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "report_page.md"))

    with open(os.path.join(mdoc_exporter._output_path, "org", "repo", "NoTopic", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "NoTopic"', "| org | repo | [#0 - ](features#) |  |<a href='' target='_blank'>GitHub link</a> |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "org", "repo", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "repo"', "This section displays the living documentation for all topics within the repository: **repo** in a structured output."]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "org", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "org"', "This section displays the living documentation for all repositories within the organization: **org** in a structured output."]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "_index.md"), 'r') as file:
        content = file.read()
    expected = ['toolbar_title: Features', 'description_title: Living Documentation']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "report_page.md"), 'r') as file:
        content = file.read()
    expected = ['title: "Report page"', '<h3>Report page</h3>', "| TopicError | [org/repo#0]() | No Topic label found. |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."


def test_export_real_execution_structured_output_no_topics(mdoc_exporter, sample_issues, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=True)
    mocker.patch("action_inputs.ActionInputs.is_grouping_by_topics_enabled", return_value=False)

    # Act
    result = mdoc_exporter.export(issues=sample_issues)

    # Assert
    assert result is True
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "org", "repo", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "org", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "_index.md"))

    with open(os.path.join(mdoc_exporter._output_path, "org", "repo", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "repo"', "This section displays all the information about mined features for **repo**.", "| org | repo | [#0 - ](features#) | 🔴 | --- |<a href='' target='_blank'>GitHub link</a> |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "org", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "org"', "This section displays the living documentation for all repositories within the organization: **org** in a structured output."]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "_index.md"), 'r') as file:
        content = file.read()
    expected = ['toolbar_title: Features', 'description_title: Living Documentation']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."


def test_export_real_execution_flat_with_topics(mdoc_exporter, sample_issues, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=False)
    mocker.patch("action_inputs.ActionInputs.is_grouping_by_topics_enabled", return_value=True)

    # Act
    result = mdoc_exporter.export(issues=sample_issues)

    # Assert
    assert result is True
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "NoTopic", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "report_page.md"))

    with open(os.path.join(mdoc_exporter._output_path, "NoTopic", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "NoTopic"', "| org | repo | [#0 - ](features#) | 🔴 | --- |<a href='' target='_blank'>GitHub link</a> |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "_index.md"), 'r') as file:
        content = file.read()
    expected = ['toolbar_title: Features', 'description_title: Living Documentation']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    with open(os.path.join(mdoc_exporter._output_path, "report_page.md"), 'r') as file:
        content = file.read()
    expected = ['title: "Report page"', '<h3>Report page</h3>', "| TopicError | [org/repo#0]() | No Topic label found. |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."


def test_export_real_execution_flat_no_topics(mdoc_exporter, sample_issues, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=False)
    mocker.patch("action_inputs.ActionInputs.is_grouping_by_topics_enabled", return_value=False)

    # Act
    result = mdoc_exporter.export(issues=sample_issues)

    # Assert
    assert result is True
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "_index.md"))

    with open(os.path.join(mdoc_exporter._output_path, "_index.md"), 'r') as file:
        content = file.read()
    expected = ['toolbar_title: Features', "| org | repo | [#0 - ](features#) | 🔴 | --- |<a href='' target='_blank'>GitHub link</a> |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."


def test_load_all_templates_failure(mocker):
    # Arrange
    mocker.patch('living_documentation_regime.exporter.mdoc_exporter.load_template', side_effect=[None, 'template', 'template', 'template', 'template', 'template', 'template'])
    exporter = MdocExporter('/mocked/output/path')

    # Act
    result = exporter._load_all_templates()

    # Assert
    assert result is False


def test_generate_issue_summary_table_linked_to_project(mocker, sample_issue_linked_to_project):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
    exporter = MdocExporter('/mocked/output/path')

    # Act
    result = exporter._generate_issue_summary_table(sample_issue_linked_to_project)

    # Assert
    assert "Project Title" in result
    assert "In Progress" in result
    assert "High" in result
    assert "Large" in result
    assert "Must Have" in result
