import os.path
import pytest

from living_doc_generator.mdoc_exporter import MdocExporter
from living_doc_utilities.model.feature_issue import FeatureIssue
from living_doc_utilities.model.functionality_issue import FunctionalityIssue
from living_doc_utilities.model.user_story_issue import UserStoryIssue

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


def test_generate_directory_path_feat_structured(mocker):
    exporter = MdocExporter("/mocked/output/path")
    mocker.patch("living_doc_generator.mdoc_exporter.ActionInputs.is_structured_output_enabled", return_value=True)

    parent_path = "features"
    repo_id = "org/repo"
    feature_title = "MyFeature"

    result = exporter._generate_directory_path_feat(parent_path, repo_id, feature_title)

    expected_path = os.path.join("/mocked/output/path", parent_path, "org", "repo", feature_title)
    assert result == expected_path


def test_generate_directory_path_feat_not_structured(mocker):
    exporter = MdocExporter("/mocked/output/path")
    mocker.patch("living_doc_generator.mdoc_exporter.ActionInputs.is_structured_output_enabled", return_value=False)

    parent_path = "features"
    repo_id = "org/repo"
    feature_title = "MyFeature"

    result = exporter._generate_directory_path_feat(parent_path, repo_id, feature_title)

    expected_path = os.path.join("/mocked/output/path", parent_path, feature_title)
    assert result == expected_path


# _generate_directory_path_func


def test_generate_directory_path_func_structured(mocker):
    exporter = MdocExporter("/mocked/output/path")
    mocker.patch("living_doc_generator.mdoc_exporter.ActionInputs.is_structured_output_enabled", return_value=True)

    parent_path = "functionalities"
    repo_id = "org/repo"
    feature_title = "MyFunctionality"

    result = exporter._generate_directory_path_func(parent_path, repo_id, feature_title)

    expected_path = os.path.join("/mocked/output/path", parent_path, "org", "repo", feature_title)
    assert result == expected_path


def test_generate_directory_path_func_not_structured(mocker):
    exporter = MdocExporter("/mocked/output/path")
    mocker.patch("living_doc_generator.mdoc_exporter.ActionInputs.is_structured_output_enabled", return_value=False)

    parent_path = "functionalities"
    repo_id = "org/repo"
    feature_title = "MyFunctionality"

    result = exporter._generate_directory_path_func(parent_path, repo_id, feature_title)

    expected_path = os.path.join("/mocked/output/path", parent_path, feature_title)
    assert result == expected_path


# _generate_mdoc_line


def test_generate_mdoc_line_linked_and_not_linked(mdoc_exporter, sample_issues_without_project_states):
    mdoc_exporter.project_statuses_included = True

    # Linked to project
    issue = sample_issues_without_project_states.issues["org/repo/1"]
    issue.linked_to_project = True
    result_linked = mdoc_exporter._generate_mdoc_line(issue)
    assert "| org | repo | [#1 - Sample User Story 1]" in result_linked
    assert "🟢" in result_linked

    # Not linked to project
    issue.linked_to_project = False
    result_not_linked = mdoc_exporter._generate_mdoc_line(issue)
    assert "| org | repo | [#1 - Sample User Story 1]" in result_not_linked
    assert "🔴" in result_not_linked


def test_generate_mdoc_line_no_project_data(mdoc_exporter, sample_issues_without_project_states):
    # Linked to project
    issue = sample_issues_without_project_states.issues["org/repo/1"]
    issue.linked_to_project = False
    result_not_linked = mdoc_exporter._generate_mdoc_line(issue)
    assert "| org | repo | [#1 - Sample User Story 1]" in result_not_linked
    assert "🟢" not in result_not_linked
    assert "🔴" not in result_not_linked


# _generate_sub_level_index_page


def test_generate_sub_level_index_page(tmp_path, mdoc_exporter, sample_issues_without_project_states):
    # Arrange
    mock_template = "title: Sub Level Index\n{{organization_name}}"
    repository_id = "org/repo"
    group_name = "user_stories"
    output_dir = os.path.join(tmp_path, "user_stories", "org")
    os.makedirs(output_dir)
    mdoc_exporter._output_path = str(tmp_path)
    file_path = os.path.join(output_dir, "_index.md")

    # Act
    mdoc_exporter._generate_sub_level_index_page(
        mock_template, repository_id, group_name
    )

    # Assert
    assert os.path.exists(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "title: Sub Level Index" in content
    assert "org" in content


# _generate_index_page


def test_generate_index_page_creates_file(tmp_path, mdoc_exporter, sample_issues_without_project_states):
    # Arrange
    mock_template = "title: User Stories\n{issue_overview_table}"
    group_name = "user_stories"
    issues = [
        sample_issues_without_project_states.issues["org/repo/1"],
        sample_issues_without_project_states.issues["org/repo/2"],
    ]
    mdoc_exporter._output_path = str(tmp_path)
    output_file = os.path.join(tmp_path, group_name, "_index.md")

    # Act
    mdoc_exporter._generate_index_page(mock_template, group_name, issues)

    # Assert
    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "title: User Stories" in content
    assert "[#1 - Sample User Story 1]" in content
    assert "[#2 - Sample User Story 2]" in content


def test_generate_index_page_creates_file_structured(tmp_path, mdoc_exporter, sample_issues_without_project_states, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=True)
    mock_template = "title: User Stories\n{issue_overview_table}"
    group_name = "user_stories"
    issues = [
        sample_issues_without_project_states.issues["org/repo/1"],
        sample_issues_without_project_states.issues["org/repo/2"],
    ]
    mdoc_exporter._output_path = str(tmp_path)
    output_file = os.path.join(tmp_path, group_name, "org", "repo", "_index.md")

    # Act
    mdoc_exporter._generate_index_page(mock_template, group_name, issues)

    # Assert
    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "title: User Stories" in content
    assert "[#1 - Sample User Story 1]" in content
    assert "[#2 - Sample User Story 2]" in content


def test_generate_index_page_creates_file_no_issues(tmp_path, mdoc_exporter, mocker):
    # Arrange
    mock_logger_info = mocker.patch("living_doc_generator.mdoc_exporter.logger.info")
    mock_template = "title: User Stories\n{issue_overview_table}"
    group_name = "user_stories"
    issues = []
    mdoc_exporter._output_path = str(tmp_path)
    output_file = os.path.join(tmp_path, group_name, "_index.md")

    # Act
    mdoc_exporter._generate_index_page(mock_template, group_name, issues)

    # Assert
    assert not os.path.exists(output_file)
    mock_logger_info.assert_has_calls(
        [
            mocker.call("No source issues found for group: %s.", "user_stories"),
        ],
        any_order=True,
    )


# _generate_structured_index_pages


def test_generate_structured_index_pages_creates_files(tmp_path, mdoc_exporter, sample_issues_without_project_states, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=True)
    group_name = "user_stories"
    mdoc_exporter._output_path = str(tmp_path)
    mocker.patch.object(mdoc_exporter, "_generate_sub_level_index_page")

    # Act
    mdoc_exporter._generate_structured_index_pages(sample_issues_without_project_states, group_name)

    # Assert
    # Check that sub-level index pages are generated for each unique repository
    calls = mdoc_exporter._generate_sub_level_index_page.call_args_list
    repo_ids = set(issue.repository_id for issue in sample_issues_without_project_states.issues.values())
    assert len(calls) == len(repo_ids)
    for call in calls:
        args, kwargs = call
        # args: (index_template, repository_id, group_name)
        assert args[1] in repo_ids
        assert args[2] == group_name


# generate_page_filename


def test_generate_page_filename(mdoc_exporter, mocker):
    # Arrange: create a mock issue
    issue = mocker.Mock()
    issue.issue_number = 42
    issue.title = "My Feature Title"

    # Act
    filename = mdoc_exporter.generate_page_filename(issue)

    # Assert
    assert filename == "42.md"


def test_generate_page_filename_with_real_user_story_issue(mdoc_exporter):
    # Arrange: create a real UserStoryIssue
    issue = UserStoryIssue()
    issue.issue_number = 101
    issue.title = "Implement Login Feature"

    # Act
    filename = mdoc_exporter.generate_page_filename(issue)

    # Assert
    assert filename == "101_implement_login_feature.md"


def test_generate_page_filename_with_real_feature_issue(mdoc_exporter):
    # Arrange: create a real UserStoryIssue
    issue = FeatureIssue()
    issue.issue_number = 101
    issue.title = "Implement Login Feature"

    # Act
    filename = mdoc_exporter.generate_page_filename(issue)

    # Assert
    assert filename == "_index.md"


# _generate_md_issue_page_for_func


def test_generate_md_issue_page_for_func(mdoc_exporter, tmp_path, mocker):
    # Arrange
    issue = FunctionalityIssue()
    issue.issue_number = 7
    issue.title = "Sample Functionality"
    issue.body = "This is a sample functionality issue body."
    issue.repository_id = "org/repo"
    issue.state = "In Progress"
    issue.html_url = "https://github.com/org/repo/issues/7"

    # Mock the template to include all replacements
    mock_template = "{title}\n{date}\n{issue_content}"
    mocker.patch.object(mdoc_exporter, "_func_issue_page_detail_template", mock_template)

    mdoc_exporter._output_path = str(tmp_path)
    output_file = os.path.join(tmp_path, "functionalities", "7_sample-functionality.md")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Act
    mdoc_exporter._generate_md_issue_page_for_func(issue)

    # Assert
    md_file_path = os.path.join(mdoc_exporter._output_path, "features", "no_feature", "7_sample_functionality.md")
    assert os.path.exists(md_file_path)
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Sample Functionality" in content
    assert "This is a sample functionality issue body." in content


# _generate_md_issue_page_for_feat


def test_generate_md_issue_page_for_feat(mdoc_exporter, tmp_path, mocker):
    # Arrange
    issue = FeatureIssue()
    issue.issue_number = 10
    issue.title = "Sample Feature"
    issue.body = "This is a sample feature issue body."
    issue.repository_id = "org/repo"
    issue.state = "Completed"
    issue.html_url = "https://github.com/org/repo/issues/10"

    # Mock the template to include all replacements
    mock_template = "{title}\n{date}\n{issue_content}"
    mocker.patch.object(mdoc_exporter, "_feat_issue_page_detail_template", mock_template)

    mdoc_exporter._output_path = str(tmp_path)
    output_file = os.path.join(tmp_path, "features", "Sample Feature", "_index.md")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Act
    mdoc_exporter._generate_md_issue_page_for_feat(issue)

    # Assert
    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Sample Feature" in content
    assert "This is a sample feature issue body." in content


# _generate_md_issue_page_for_us


def test_generate_md_issue_page_for_us(mdoc_exporter, tmp_path, mocker):
    # Arrange
    issue = UserStoryIssue()
    issue.issue_number = 15
    issue.title = "Sample User Story"
    issue.body = "This is a sample user story issue body."
    issue.repository_id = "org/repo"
    issue.state = "In Progress"
    issue.html_url = "https://github.com/org/repo/issues/15"

    # Mock the template to include all replacements
    mock_template = "{title}\n{date}\n{issue_content}"
    mocker.patch.object(mdoc_exporter, "_us_issue_page_detail_template", mock_template)

    mdoc_exporter._output_path = str(tmp_path)
    output_file = os.path.join(tmp_path, "user_stories", "15_sample_user_story.md")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Act
    mdoc_exporter._generate_md_issue_page_for_us(issue)

    # Assert
    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Sample User Story" in content
    assert "This is a sample user story issue body." in content


# _generate_output_structure


def test_generate_output_structure_with_prepared_issues_not_structured(mdoc_exporter, tmp_path, sample_issues_without_project_states, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=False)
    mdoc_exporter._output_path = str(tmp_path)

    # Act
    mdoc_exporter._generate_output_structure(sample_issues_without_project_states)

    # Assert
    expected_us_path = os.path.join(tmp_path, "user_stories")
    expected_feat_path = os.path.join(tmp_path, "features")
    assert os.path.exists(expected_us_path)
    assert os.path.exists(expected_feat_path)

def test_generate_output_structure_with_prepared_issues_structured(mdoc_exporter, tmp_path, sample_issues_without_project_states, mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.is_structured_output_enabled", return_value=True)
    mdoc_exporter._output_path = str(tmp_path)

    # Act
    mdoc_exporter._generate_output_structure(sample_issues_without_project_states)

    # Assert
    assert os.path.exists(os.path.join(tmp_path, "user_stories", "_index.md"))
    assert os.path.exists(os.path.join(tmp_path, "user_stories", "org", "_index.md"))
    assert os.path.exists(os.path.join(tmp_path, "user_stories", "org", "repo", "_index.md"))
    assert os.path.exists(os.path.join(tmp_path, "features", "_index.md"))
    assert os.path.exists(os.path.join(tmp_path, "features", "org", "_index.md"))
    assert os.path.exists(os.path.join(tmp_path, "features", "org", "repo", "_index.md"))


# _generate_page_per_issue


def test_generate_page_per_issue(mdoc_exporter, tmp_path, sample_issues_without_project_states, mocker):
    # Arrange
    mdoc_exporter._output_path = str(tmp_path)
    mocker.patch.object(mdoc_exporter, "_generate_md_issue_page_for_us")
    mocker.patch.object(mdoc_exporter, "_update_error_page")
    mocker.patch.object(mdoc_exporter, "_generate_md_issue_page_for_feat")
    mocker.patch.object(mdoc_exporter, "_generate_md_issue_page_for_func")

    sample_issues_without_project_states.issues.pop("org/repo/2")
    sample_issues_without_project_states.issues.pop("org/repo/4")
    sample_issues_without_project_states.issues.pop("org/repo/6")

    # Act
    mdoc_exporter._generate_page_per_issue(sample_issues_without_project_states)

    # Assert
    assert mdoc_exporter._generate_md_issue_page_for_us.call_count == 1
    assert mdoc_exporter._generate_md_issue_page_for_feat.call_count == 1
    assert mdoc_exporter._generate_md_issue_page_for_func.call_count == 1
    assert mdoc_exporter._update_error_page.call_count == 3

    assert mdoc_exporter._generate_md_issue_page_for_us.call_args[0][0].issue_number == 1
    assert mdoc_exporter._generate_md_issue_page_for_feat.call_args[0][0].issue_number == 3
    assert mdoc_exporter._generate_md_issue_page_for_func.call_args[0][0].issue_number == 5


# _generate_report_page


def test_generate_report_page(mdoc_exporter, tmp_path, mocker):
    # Arrange
    mdoc_exporter._output_path = str(tmp_path)
    mocker.patch("living_doc_generator.mdoc_exporter.ActionInputs.is_report_page_generation_enabled", return_value=True)
    mocker.patch.object(mdoc_exporter, "_report_page_template", "{date}\n{livdoc_report_page_content}\n{group}")
    mdoc_exporter._report_page_content = {
        "User Story": (
            "| Error Type | Issue | Description |\n"
            "|------------|-------|-------------|\n"
            "| SomeError  | [org/repo#1](https://github.com/org/repo/issues/1) | Fake some error. |\n"
        )
    }
    report_file_path = os.path.join(tmp_path, "user_stories", "report_page.md")
    os.makedirs(os.path.dirname(report_file_path), exist_ok=True)

    # Act
    mdoc_exporter._generate_report_page()

    # Assert
    assert os.path.exists(report_file_path)
    with open(report_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "User Story" in content
    assert "| SomeError  | [org/repo#1](https://github.com/org/repo/issues/1) | Fake some error. |" in content


# export


def test_export(mdoc_exporter, tmp_path, sample_issues_with_errors_without_project_states, mocker):
    # Arrange
    mdoc_exporter._output_path = str(tmp_path)
    mocker.patch("living_doc_generator.mdoc_exporter.ActionInputs.is_report_page_generation_enabled", return_value=True)
    mock_load_all_templates = mocker.patch.object(mdoc_exporter, "_load_all_templates", return_value=True)
    mock_generate_page_per_issue = mocker.patch.object(mdoc_exporter, "_generate_page_per_issue")
    mock_generate_output_structure = mocker.patch.object(mdoc_exporter, "_generate_output_structure")
    mock_generate_report_page = mocker.patch.object(mdoc_exporter, "_generate_report_page")

    # Act
    result = mdoc_exporter.export(issues = sample_issues_with_errors_without_project_states)

    # Assert
    assert result is True
    mock_load_all_templates.assert_called_once()
    mock_generate_output_structure.assert_called_once_with(sample_issues_with_errors_without_project_states)
    mock_generate_page_per_issue.assert_called_once_with(sample_issues_with_errors_without_project_states)
    mock_generate_report_page.assert_called_once()


def test_export_load_template_fails(mdoc_exporter, tmp_path, sample_issues_with_errors_without_project_states, mocker):
    # Arrange
    mdoc_exporter._output_path = str(tmp_path)
    mocker.patch("living_doc_generator.mdoc_exporter.ActionInputs.is_report_page_generation_enabled", return_value=True)
    mock_load_all_templates = mocker.patch.object(mdoc_exporter, "_load_all_templates", return_value=False)
    mock_generate_page_per_issue = mocker.patch.object(mdoc_exporter, "_generate_page_per_issue")
    mock_generate_output_structure = mocker.patch.object(mdoc_exporter, "_generate_output_structure")
    mock_generate_report_page = mocker.patch.object(mdoc_exporter, "_generate_report_page")

    # Act
    result = mdoc_exporter.export(issues = sample_issues_with_errors_without_project_states)

    # Assert
    assert result is False
    mock_load_all_templates.assert_called_once()
    mock_generate_output_structure.assert_not_called()
    mock_generate_page_per_issue.assert_not_called()
    mock_generate_report_page.assert_not_called()
