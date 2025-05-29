import os.path
import pytest

from living_doc_generator.mdoc_exporter import MdocExporter
from living_doc_generator.model.consolidated_issue import ConsolidatedIssue
from living_doc_generator.model.project_status import ProjectStatus


@pytest.fixture
def mdoc_exporter(tmp_path, mocker):
    """Fixture to create an instance of MdocExporter with modified template paths."""
    output_dir = os.path.join(tmp_path, "output")
    os.makedirs(output_dir, exist_ok=True)
    return MdocExporter(output_dir)


@pytest.fixture
def sample_issues(mocker):
    class IssueWithCustomLabels(ConsolidatedIssue):
        def __init__(self, labels: list[str], body: str = "", **kwargs):
            super().__init__(**kwargs)
            self._custom_labels = labels
            self._body = body

        @property
        def labels(self) -> list[str]:
            return self._custom_labels

        @property
        def body(self) -> str:
            return self._body

    issue_1 = IssueWithCustomLabels(labels=["DocumentedUserStory"], repository_id="org/repo")
    issue_2 = IssueWithCustomLabels(labels=["DocumentedFeature"], repository_id="org/repo")
    issue_3 = IssueWithCustomLabels(labels=["DocumentedFunctionality"], repository_id="org/repo")
    issue_4 = IssueWithCustomLabels(labels=["DocumentedFunctionality"], repository_id="org/repo", body="### Associated Feature\n- #13")

    return {"ISSUE-1": issue_1, "ISSUE-2": issue_2, "ISSUE-3": issue_3, "org/repo/13": issue_4}


@pytest.fixture
def sample_issues_with_errors(sample_issues, mocker):
    sample_issues["ISSUE-1"].errors.update({"SomeError": "Fake some error."})
    sample_issues["ISSUE-2"].errors.update({"AnotherError": "Another fake error."})

    return sample_issues


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


def test_export_real_execution_all_enabled(mdoc_exporter, sample_issues_with_errors, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=True)

    # Act
    result = mdoc_exporter.export(issues=sample_issues_with_errors)

    # Assert
    assert result is True
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "repo", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "org", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "org", "repo", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"))

    # "user_stories", "_index.md"
    with open(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: User Stories', 'toolbar_title: User Stories', 'description_title: User Stories',
                "The comprehensive list of AqueDuct Project's User Stories."]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "user_stories", "org", "_index.md"))
    with open(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "org"', 'weight: 0']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "user_stories", "org", "repo", "_index.md"))
    with open(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "repo", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: User Stories', "| org | repo | [#0 - ](features#) | 🔴 | --- |<a href='' target='_blank'>GitHub link</a> |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "features", "_index.md"))
    with open(os.path.join(mdoc_exporter._output_path, "features", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: Features', 'toolbar_title: Features', 'description_title: Features and Functionalities',
                "The comprehensive list of AqueDuct Project's Features and Functiona"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "features", "org", "_index.md"))
    with open(os.path.join(mdoc_exporter._output_path, "features", "org", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "org"', 'weight: 0']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "features", "org", "repo", "_index.md"))
    with open(os.path.join(mdoc_exporter._output_path, "features", "org", "repo", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: Features', "| org | repo | [#0 - ](features#) | 🔴 | --- |<a href='' target='_blank'>GitHub link</a> |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "user_stories", "report_page.md"))
    with open(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"), 'r') as file:
        content = file.read()
    expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - User Story',
                '| SomeError | [org/repo#0]() | Fake some error. |']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "features", "report_page.md"))
    with open(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"), 'r') as file:
        content = file.read()
    expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - Feature',
                '| AnotherError | [org/repo#0]() | Another fake error. |']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."


def test_export_real_execution_no_structure(mdoc_exporter, sample_issues_with_errors, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=False)

    # Act
    result = mdoc_exporter.export(issues=sample_issues_with_errors)

    # Assert
    assert result is True
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"))

    # "user_stories", "_index.md"
    with open(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: User Stories', 'toolbar_title: User Stories', 'description_title: User Stories',
                "The comprehensive list of AqueDuct Project's User Stories."]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "features", "_index.md"))
    with open(os.path.join(mdoc_exporter._output_path, "features", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: Features', 'toolbar_title: Features', 'description_title: Features and Functionalities',
                "The comprehensive list of AqueDuct Project's Features and Functiona"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "user_stories", "report_page.md"))
    with open(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"), 'r') as file:
        content = file.read()
    expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - User Story',
                '| SomeError | [org/repo#0]() | Fake some error. |']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "features", "report_page.md"))
    with open(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"), 'r') as file:
        content = file.read()
    expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - Feature',
                '| AnotherError | [org/repo#0]() | Another fake error. |']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."


def test_export_real_execution_no_project_mining(mdoc_exporter, sample_issues_with_errors, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=False)
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=True)

    # Act
    result = mdoc_exporter.export(issues=sample_issues_with_errors)

    # Assert
    assert result is True
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "repo", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "org", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "org", "repo", "_index.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"))
    assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"))

    # "user_stories", "_index.md"
    with open(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: User Stories', 'toolbar_title: User Stories', 'description_title: User Stories',
                "The comprehensive list of AqueDuct Project's User Stories."]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "user_stories", "org", "_index.md"))
    with open(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "org"', 'weight: 0']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "user_stories", "org", "repo", "_index.md"))
    with open(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "repo", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: User Stories', "| org | repo | [#0 - ](features#) |  |<a href=\'\' target=\'_blank\'>GitHub link</a> |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "features", "_index.md"))
    with open(os.path.join(mdoc_exporter._output_path, "features", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: Features', 'toolbar_title: Features', 'description_title: Features and Functionalities',
                "The comprehensive list of AqueDuct Project's Features and Functiona"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "features", "org", "_index.md"))
    with open(os.path.join(mdoc_exporter._output_path, "features", "org", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: "org"', 'weight: 0']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "features", "org", "repo", "_index.md"))
    with open(os.path.join(mdoc_exporter._output_path, "features", "org", "repo", "_index.md"), 'r') as file:
        content = file.read()
    expected = ['title: Features', "| org | repo | [#0 - ](features#) |  |<a href=\'\' target=\'_blank\'>GitHub link</a> |"]
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "user_stories", "report_page.md"))
    with open(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"), 'r') as file:
        content = file.read()
    expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - User Story',
                '| SomeError | [org/repo#0]() | Fake some error. |']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."

    # "features", "report_page.md"))
    with open(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"), 'r') as file:
        content = file.read()
    expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - Feature',
                '| AnotherError | [org/repo#0]() | Another fake error. |']
    for item in expected:
        assert item in content, f"Expected string '{item}' not found in file content."


def test_load_all_templates_failure(mocker):
    # Arrange
    mocker.patch('living_documentation_regime.exporter.mdoc_exporter.load_template', side_effect=[None, 'template', 'template', 'template', 'template', 'template', 'template', 'template', 'template', 'template'])
    exporter = MdocExporter('/mocked/output/path')

    # Act
    result = exporter.export()

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


def test_generate_index_page_no_issues(mocker):
    # Arrange
    mock_logger_info = mocker.patch("living_documentation_regime.exporter.mdoc_exporter.logger.info")
    exporter = MdocExporter("/mocked/output/path")
    mock_template = "mock_template"
    group_name = "user_stories"
    consolidated_issues = []  # Empty list to trigger the branch

    # Act
    exporter._generate_index_page(mock_template, group_name, consolidated_issues)

    # Assert
    mock_logger_info.assert_called_once_with("No consolidated issues found for group: %s.", group_name)


def test_generate_mdoc_line_linked_to_project(consolidated_issue, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
    consolidated_issue.linked_to_project = True

    exporter = MdocExporter("/mocked/output/path")

    # Act
    result = exporter._generate_mdoc_line(consolidated_issue)

    # Assert
    assert "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🟢 | In Progress |<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |" in result


def test_generate_mdoc_line_not_linked_to_project(consolidated_issue, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
    consolidated_issue.linked_to_project = False

    exporter = MdocExporter("/mocked/output/path")

    # Act
    result = exporter._generate_mdoc_line(consolidated_issue)

    # Assert
    assert "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🔴 | In Progress |<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |" in result


def test_generate_issue_summary_table_not_linked_to_project(consolidated_issue, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
    consolidated_issue.linked_to_project = False

    exporter = MdocExporter("/mocked/output/path")

    # Act
    result = exporter._generate_issue_summary_table(consolidated_issue)

    # Assert
    assert "Linked to project | 🔴 |" in result
