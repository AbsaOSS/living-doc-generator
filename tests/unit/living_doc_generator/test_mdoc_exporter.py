import os.path
import pytest

from living_doc_generator.mdoc_exporter import MdocExporter
from living_doc_utilities.model.feature_issue import FeatureIssue
from living_doc_utilities.model.functionality_issue import FunctionalityIssue
from living_doc_utilities.model.issues import Issues
from living_doc_utilities.model.project_status import ProjectStatus
from living_doc_utilities.model.user_story_issue import UserStoryIssue


@pytest.fixture
def mdoc_exporter(tmp_path):
    """Fixture to create an instance of MdocExporter with modified template paths."""
    output_dir = os.path.join(tmp_path, "output")
    os.makedirs(output_dir, exist_ok=True)
    return MdocExporter(output_dir)


@pytest.fixture
def sample_issues_without_project_states():
    issues: Issues = Issues()

    issue_us_1: UserStoryIssue = UserStoryIssue()
    issue_us_1.repository_id = "org/repo"
    issue_us_1.issue_number = 1
    issue_us_1.title = "Sample User Story 1"
    issue_us_1.body = "This is a sample user story issue body."
    issue_us_1.state = "In Progress"
    issue_us_2: UserStoryIssue = UserStoryIssue()
    issue_us_2.repository_id = "org/repo"
    issue_us_2.issue_number = 2
    issue_us_2.title = "Sample User Story 2"
    issue_us_2.body = "This is another sample user story issue body."
    issue_us_2.state = "To Do"
    issue_feat_1: FeatureIssue = FeatureIssue()
    issue_feat_1.repository_id = "org/repo"
    issue_feat_1.issue_number = 3
    issue_feat_1.title = "Sample Feature 1"
    issue_feat_1.body = "This is a sample feature issue body."
    issue_feat_1.state = "In Progress"
    issue_feat_2: FeatureIssue = FeatureIssue()
    issue_feat_2.repository_id = "org/repo"
    issue_feat_2.issue_number = 4
    issue_feat_2.title = "Sample Feature 2"
    issue_feat_2.body = "This is a sample feature issue body."
    issue_feat_2.state = "To Do"
    issue_func_1: FunctionalityIssue = FunctionalityIssue()
    issue_func_1.repository_id = "org/repo"
    issue_func_1.issue_number = 5
    issue_func_1.title = "Sample Functionality 1"
    issue_func_1.body = "This is a sample function issue body."
    issue_func_1.state = "In Progress"
    issue_func_2: FunctionalityIssue = FunctionalityIssue()
    issue_func_2.repository_id = "org/repo"
    issue_func_2.issue_number = 6
    issue_func_2.title = "Sample Functionality 2"
    issue_func_2.body = "This is a sample function issue body."
    issue_func_2.state = "To Do"

    issues.issues["org/repo/1"] = issue_us_1
    issues.issues["org/repo/2"] = issue_us_2
    issues.issues["org/repo/3"] = issue_feat_1
    issues.issues["org/repo/4"] = issue_feat_2
    issues.issues["org/repo/5"] = issue_func_1
    issues.issues["org/repo/6"] = issue_func_2

    return issues

@pytest.fixture
def sample_issues_with_project_states(sample_issues_without_project_states):
    prj_status_in_progress = ProjectStatus()
    prj_status_in_progress.status = "In Progress"
    prj_status_todo = ProjectStatus()
    prj_status_todo.status = "To Do"

    sample_issues_without_project_states.issues["org/repo/1"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/1"].project_statuses.append(prj_status_in_progress)
    sample_issues_without_project_states.issues["org/repo/2"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/2"].project_statuses.append(prj_status_todo)
    sample_issues_without_project_states.issues["org/repo/3"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/3"].project_statuses.append(prj_status_in_progress)
    sample_issues_without_project_states.issues["org/repo/4"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/4"].project_statuses.append(prj_status_todo)
    sample_issues_without_project_states.issues["org/repo/5"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/5"].project_statuses.append(prj_status_in_progress)
    sample_issues_without_project_states.issues["org/repo/6"].linked_to_project = True
    sample_issues_without_project_states.issues["org/repo/6"].project_statuses.append(prj_status_todo)

    sample_issues_without_project_states.project_states_included = True

    return sample_issues_without_project_states


@pytest.fixture
def sample_issues_with_errors_without_project_states(sample_issues_without_project_states):
    sample_issues_without_project_states.get_issue("org/repo/1").add_errors({"SomeError": "Fake some error."})
    sample_issues_without_project_states.get_issue("org/repo/2").add_errors({"SomeError": "Fake some error."})
    return sample_issues_without_project_states


@pytest.fixture
def sample_issues_with_errors_with_project_states(sample_issues_with_project_states):
    sample_issues_with_project_states.get_issue("org/repo/1").add_errors({"SomeError": "Fake some error."})
    sample_issues_with_project_states.get_issue("org/repo/2").add_errors({"SomeError": "Fake some error."})
    return sample_issues_with_project_states


# def test_export_real_execution_all_enabled(mdoc_exporter, sample_issues_with_errors_with_project_states, mocker):
#     # Arrange
#     mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=True)
#     mocker.patch("action_inputs.ActionInputs.is_report_page_generation_enabled", return_value=True)
#
#     # Act
#     result = mdoc_exporter.export(issues=sample_issues_with_errors_with_project_states)
#
#     # Assert
#     assert result is True
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "repo", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "org", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "org", "repo", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"))
#     # TODO - support of second report page have to be implemented - mdoc export holds only one report page data
#     # assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"))
#
#     # "user_stories", "_index.md"
#     with open(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: User Stories', 'toolbar_title: User Stories', 'description_title: User Stories',
#                 "The comprehensive list of AqueDuct Project's User Stories."]
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "user_stories", "org", "_index.md"
#     with open(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: "org"', 'weight: 0']
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "user_stories", "org", "repo", "_index.md"
#     with open(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "repo", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: User Stories', "| org | repo | [#1 - Sample User Story 1](features#sample-user-story-1) | 🟢 | In Progress |<a href='None' target='_blank'>GitHub link</a> |"]
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "features", "_index.md"
#     with open(os.path.join(mdoc_exporter._output_path, "features", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: Features', 'toolbar_title: Features', 'description_title: Features and Functionalities',
#                 "The comprehensive list of AqueDuct Project's Features and Functiona"]
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "features", "org", "_index.md"
#     with open(os.path.join(mdoc_exporter._output_path, "features", "org", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: "org"', 'weight: 0']
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "features", "org", "repo", "_index.md"
#     with open(os.path.join(mdoc_exporter._output_path, "features", "org", "repo", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: Features', "| org | repo | [#3 - Sample Feature 1](features#sample-feature-1) | 🟢 | In Progress |<a href='None' target='_blank'>GitHub link</a> |"]
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "user_stories", "report_page.md"
#     with open(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - User Story',
#                 '| SomeError | [org/repo#1](None) | Fake some error. |']
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "features", "report_page.md"
#     # TODO - support of second report page have to be implemented - mdoc export holds only one report page data
#     # with open(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"), 'r') as file:
#     #     content = file.read()
#     # expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - Feature',
#     #             '| AnotherError | [org/repo#0]() | Another fake error. |']
#     # for item in expected:
#     #     assert item in content, f"Expected string '{item}' not found in file content."


# def test_export_real_execution_no_structure(mdoc_exporter, sample_issues_with_errors, mocker):
#     # Arrange
#     mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
#     mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=False)
#
#     # Act
#     result = mdoc_exporter.export(issues=sample_issues_with_errors)
#
#     # Assert
#     assert result is True
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"))
#
#     # "user_stories", "_index.md"
#     with open(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: User Stories', 'toolbar_title: User Stories', 'description_title: User Stories',
#                 "The comprehensive list of AqueDuct Project's User Stories."]
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "features", "_index.md"))
#     with open(os.path.join(mdoc_exporter._output_path, "features", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: Features', 'toolbar_title: Features', 'description_title: Features and Functionalities',
#                 "The comprehensive list of AqueDuct Project's Features and Functiona"]
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "user_stories", "report_page.md"))
#     with open(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - User Story',
#                 '| SomeError | [org/repo#0]() | Fake some error. |']
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "features", "report_page.md"))
#     with open(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - Feature',
#                 '| AnotherError | [org/repo#0]() | Another fake error. |']
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#
# def test_export_real_execution_no_project_mining(mdoc_exporter, sample_issues_with_errors, mocker):
#     # Arrange
#     mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=False)
#     mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=True)
#
#     # Act
#     result = mdoc_exporter.export(issues=sample_issues_with_errors)
#
#     # Assert
#     assert result is True
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "repo", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "org", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "org", "repo", "_index.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"))
#     assert os.path.exists(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"))
#
#     # "user_stories", "_index.md"
#     with open(os.path.join(mdoc_exporter._output_path, "user_stories", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: User Stories', 'toolbar_title: User Stories', 'description_title: User Stories',
#                 "The comprehensive list of AqueDuct Project's User Stories."]
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "user_stories", "org", "_index.md"))
#     with open(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: "org"', 'weight: 0']
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "user_stories", "org", "repo", "_index.md"))
#     with open(os.path.join(mdoc_exporter._output_path, "user_stories", "org", "repo", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: User Stories', "| org | repo | [#0 - ](features#) |  |<a href=\'\' target=\'_blank\'>GitHub link</a> |"]
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "features", "_index.md"))
#     with open(os.path.join(mdoc_exporter._output_path, "features", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: Features', 'toolbar_title: Features', 'description_title: Features and Functionalities',
#                 "The comprehensive list of AqueDuct Project's Features and Functiona"]
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "features", "org", "_index.md"))
#     with open(os.path.join(mdoc_exporter._output_path, "features", "org", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: "org"', 'weight: 0']
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "features", "org", "repo", "_index.md"))
#     with open(os.path.join(mdoc_exporter._output_path, "features", "org", "repo", "_index.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: Features', "| org | repo | [#0 - ](features#) |  |<a href=\'\' target=\'_blank\'>GitHub link</a> |"]
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "user_stories", "report_page.md"))
#     with open(os.path.join(mdoc_exporter._output_path, "user_stories", "report_page.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - User Story',
#                 '| SomeError | [org/repo#0]() | Fake some error. |']
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
#     # "features", "report_page.md"))
#     with open(os.path.join(mdoc_exporter._output_path, "features", "report_page.md"), 'r') as file:
#         content = file.read()
#     expected = ['title: "!!! Report !!!"', 'Summary of the errors found during the generation of living documents - Feature',
#                 '| AnotherError | [org/repo#0]() | Another fake error. |']
#     for item in expected:
#         assert item in content, f"Expected string '{item}' not found in file content."
#
# def test_generate_index_page_no_issues(mocker):
#     # Arrange
#     mock_logger_info = mocker.patch("living_documentation_regime.exporter.mdoc_exporter.logger.info")
#     exporter = MdocExporter("/mocked/output/path")
#     mock_template = "mock_template"
#     group_name = "user_stories"
#     consolidated_issues = []  # Empty list to trigger the branch
#
#     # Act
#     exporter._generate_index_page(mock_template, group_name, consolidated_issues)
#
#     # Assert
#     mock_logger_info.assert_called_once_with("No consolidated issues found for group: %s.", group_name)
#
#
# def test_generate_mdoc_line_linked_to_project(consolidated_issue, mocker):
#     # Arrange
#     mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
#     consolidated_issue.linked_to_project = True
#
#     exporter = MdocExporter("/mocked/output/path")
#
#     # Act
#     result = exporter._generate_mdoc_line(consolidated_issue)
#
#     # Assert
#     assert "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🟢 | In Progress |<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |" in result
#
#
# def test_generate_mdoc_line_not_linked_to_project(consolidated_issue, mocker):
#     # Arrange
#     mocker.patch("action_inputs.ActionInputs.is_project_state_mining_enabled", return_value=True)
#     consolidated_issue.linked_to_project = False
#
#     exporter = MdocExporter("/mocked/output/path")
#
#     # Act
#     result = exporter._generate_mdoc_line(consolidated_issue)
#
#     # Assert
#     assert "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🔴 | In Progress |<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |" in result


# _generate_issue_summary_table

def test_generate_issue_summary_table_not_linked_to_project(sample_issues_without_project_states):
    # Arrange
    exporter = MdocExporter("/mocked/output/path")

    # Act
    result = exporter._generate_issue_summary_table(sample_issues_without_project_states.issues["org/repo/1"])

    # Assert
    assert "| Status |" not in result


def test_generate_issue_summary_table_linked_to_project(sample_issues_with_project_states):
    # Arrange
    exporter = MdocExporter("/mocked/output/path")
    exporter.project_statuses_included = True
    sample_issues_with_project_states.get_issue("org/repo/2").linked_to_project = False

    # Act
    result_1 = exporter._generate_issue_summary_table(sample_issues_with_project_states.issues["org/repo/1"])
    result_2 = exporter._generate_issue_summary_table(sample_issues_with_project_states.issues["org/repo/2"])

    # Assert
    assert "| Status |" in result_1
    assert "| Status |" not in result_2


# _generate_index_directory_path


@pytest.mark.parametrize("structured,repo_id,expected_path", [
    (True, "org/repo", os.path.join("abs_out", "group", "org", "repo")),
    (False, "org/repo", os.path.join("abs_out", "group")),
    (True, None, os.path.join("abs_out", "group")),
    (False, None, os.path.join("abs_out", "group")),
])
def test_generate_index_directory_path(mocker, structured, repo_id, expected_path):
    # Arrange
    mocker.patch("living_doc_generator.mdoc_exporter.ActionInputs.is_structured_output_enabled", return_value=structured)
    mocker.patch("living_doc_generator.mdoc_exporter.make_absolute_path", return_value="abs_out")
    mocker.patch("os.makedirs")  # Prevent actual directory creation

    exporter = MdocExporter("output")
    group_name = "group"

    # Act
    result = exporter._generate_index_directory_path(group_name, repo_id)

    # Assert
    assert result == expected_path


# _load_all_templates


def test_load_all_templates_success(mocker):
    # Arrange
    exporter = MdocExporter("/mocked/output/path")
    mocker.patch("living_doc_generator.mdoc_exporter.load_template", return_value="template_content")
    # Act
    result = exporter._load_all_templates()
    # Assert
    assert result is True
    assert exporter._us_issue_page_detail_template == "template_content"
    assert exporter._feat_issue_page_detail_template == "template_content"
    assert exporter._func_issue_page_detail_template == "template_content"
    assert exporter._us_index_no_struct_template_file == "template_content"
    assert exporter._feat_index_no_struct_template_file == "template_content"
    assert exporter._us_index_root_level_template_page == "template_content"
    assert exporter._feat_index_root_level_template_page == "template_content"
    assert exporter._index_org_level_template == "template_content"
    assert exporter._report_page_template == "template_content"


def test_load_all_templates_failure(mocker):
    # Arrange
    exporter = MdocExporter("/mocked/output/path")
    # First template returns None, simulating a load failure
    mocker.patch("living_doc_generator.mdoc_exporter.load_template", side_effect=[None] + ["template"]*8)
    mock_logger_error = mocker.patch("living_doc_generator.mdoc_exporter.logger.error")
    # Act
    result = exporter._load_all_templates()
    # Assert
    assert result is False
    mock_logger_error.assert_called_once_with("MDoc page generation - failed to load all templates.")


# _update_error_page


def test_update_error_page_adds_errors(mocker):
    # Arrange
    exporter = MdocExporter("/mocked/output/path")
    mocker.patch("living_doc_generator.mdoc_exporter.ActionInputs.is_report_page_generation_enabled", return_value=True)
    issue = mocker.Mock()
    issue.errors = {"TypeError": "Something went wrong."}
    issue.repository_id = "org/repo"
    issue.issue_number = 42
    issue.html_url = "https://github.com/org/repo/issues/42"
    group = "user_stories"

    # Act
    exporter._update_error_page(issue, group)

    # Assert
    assert group in exporter._report_page_content
    assert "| TypeError | [org/repo#42](https://github.com/org/repo/issues/42) | Something went wrong. |" in exporter._report_page_content[group]


# _generate_directory_path_us


def test_generate_directory_path_us_structured(mocker):
    # Arrange
    exporter = MdocExporter("/mocked/output/path")
    mocker.patch("living_doc_generator.mdoc_exporter.ActionInputs.is_structured_output_enabled", return_value=True)

    group_name = "user_stories"
    repo_id = "org/repo"

    # Act
    result = exporter._generate_directory_path_us(group_name, repo_id)

    # Assert
    expected_path = os.path.join("/mocked/output/path", group_name, "org", "repo")
    assert result == expected_path


def test_generate_directory_path_us_not_structured(mocker):
    # Arrange
    exporter = MdocExporter("/mocked/output/path")

    group_name = "user_stories"
    repo_id = "org/repo"

    # Act
    result = exporter._generate_directory_path_us(group_name, repo_id)

    # Assert
    expected_path = os.path.join("/mocked/output/path", group_name)
    assert result == expected_path


# _generate_directory_path_feat

