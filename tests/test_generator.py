#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from datetime import datetime

from living_documentation_generator.generator import LivingDocumentationGenerator

TABLE_HEADER_WITH_PROJECT_DATA = """
| Organization name | Repository name | Issue 'Number - Title' |Linked to project | Project status | Issue URL |
|-------------------|-----------------|------------------------|------------------|----------------|-----------|
"""


# _clean_output_directory


def test_clean_output_directory(mocker):
    mock_output_path = "/test/output/path"
    mock_get_output_directory = mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_output_directory", return_value=mock_output_path
    )
    mock_exists = mocker.patch("os.path.exists", return_value=True)
    mock_rmtree = mocker.patch("shutil.rmtree")
    mock_makedirs = mocker.patch("os.makedirs")

    LivingDocumentationGenerator._clean_output_directory()

    mock_get_output_directory.assert_called_once()
    mock_exists.assert_called_once_with(mock_output_path)
    mock_rmtree.assert_called_once_with(mock_output_path)
    mock_makedirs.assert_called_once_with(mock_output_path)


# _fetch_github_issues


# _fetch_github_project_issues


def test_fetch_github_project_issues_mining_disabled(mocker, generator):
    mock_get_project_mining_enabled = mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_project_state_mining_enabled", return_value=False
    )
    mock_logger_info = mocker.patch("living_documentation_generator.generator.logger.info")

    actual = generator._fetch_github_project_issues()

    mock_get_project_mining_enabled.assert_called_once()
    mock_logger_info.assert_called_once_with("Fetching GitHub project data - project mining is not allowed.")
    assert {} == actual


# _generate_markdown_pages


def test_generate_markdown_pages_with_structured_output_and_topic_grouping_enabled(mocker, generator, consolidated_issue, load_all_templates_setup):
    # Arrange
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_is_structured_output_enabled", return_value=True)
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True)
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_output_directory", return_value="/base/output")

    mock_load_all_templates = load_all_templates_setup
    mock_generate_md_issue_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_md_issue_page")
    mock_generate_root_level_index_page = mocker.patch("living_documentation_generator.generator.generate_root_level_index_page")
    mock_generate_structured_index_pages = mocker.patch.object(LivingDocumentationGenerator, "_generate_structured_index_pages")
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")
    mock_logger_info = mocker.patch("living_documentation_generator.generator.logger.info")

    issues = {"issue_1": consolidated_issue, "issue_2": consolidated_issue}

    # Act
    generator._generate_markdown_pages(issues)

    # Assert
    mock_load_all_templates.assert_called_once()
    assert mock_generate_md_issue_page.call_count == 2
    mock_generate_md_issue_page.assert_any_call("Issue Page Template", consolidated_issue)
    mock_generate_root_level_index_page.assert_called_once_with("Root Level Page Template", "/base/output")
    mock_generate_structured_index_pages.assert_called_once_with("Data Level Template", "Repo Page Template", "Org Level Template", issues)
    mock_generate_index_page.assert_not_called()
    mock_logger_info.assert_called_once_with("Markdown page generation - generated `%i` issue pages.", 2)


def test_generate_markdown_pages_with_structured_output_enabled_and_topic_grouping_disabled(mocker, generator, consolidated_issue, load_all_templates_setup):
    # Arrange
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_is_structured_output_enabled", return_value=True)
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=False)
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_output_directory", return_value="/base/output")

    mock_load_all_templates = load_all_templates_setup
    mock_generate_md_issue_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_md_issue_page")
    mock_generate_root_level_index_page = mocker.patch("living_documentation_generator.generator.generate_root_level_index_page")
    mock_generate_structured_index_pages = mocker.patch.object(LivingDocumentationGenerator, "_generate_structured_index_pages")
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")
    mock_logger_info = mocker.patch("living_documentation_generator.generator.logger.info")

    issues = {"issue_1": consolidated_issue, "issue_2": consolidated_issue, "issue_3": consolidated_issue}

    # Act
    generator._generate_markdown_pages(issues)

    # Assert
    mock_load_all_templates.assert_called_once()
    assert mock_generate_md_issue_page.call_count == 3
    mock_generate_md_issue_page.assert_any_call("Issue Page Template", consolidated_issue)
    mock_generate_root_level_index_page.assert_called_once_with("Root Level Page Template", "/base/output")
    mock_generate_structured_index_pages.assert_called_once_with("Data Level Template", "Repo Page Template", "Org Level Template", issues)
    mock_generate_index_page.assert_not_called()
    mock_logger_info.assert_called_once_with("Markdown page generation - generated `%i` issue pages.", 3)


def test_generate_markdown_pages_with_structured_output_and_topic_grouping_disabled(mocker, generator, consolidated_issue, load_all_templates_setup):
    # Arrange
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_is_structured_output_enabled", return_value=False)
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=False)
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_output_directory", return_value="/base/output")

    mock_load_all_templates = load_all_templates_setup
    mock_generate_md_issue_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_md_issue_page")
    mock_generate_root_level_index_page = mocker.patch("living_documentation_generator.generator.generate_root_level_index_page")
    mock_generate_structured_index_pages = mocker.patch.object(LivingDocumentationGenerator, "_generate_structured_index_pages")
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")
    mock_logger_info = mocker.patch("living_documentation_generator.generator.logger.info")

    issues = {"issue_1": consolidated_issue}

    # Act
    generator._generate_markdown_pages(issues)

    # Assert
    mock_load_all_templates.assert_called_once()
    assert mock_generate_md_issue_page.call_count == 1
    mock_generate_md_issue_page.assert_any_call("Issue Page Template", consolidated_issue)
    mock_generate_root_level_index_page.assert_not_called()
    mock_generate_structured_index_pages.assert_not_called()
    mock_generate_index_page.assert_called_once_with("Index Page Template", list(issues.values()))
    mock_logger_info.assert_any_call("Markdown page generation - generated `%i` issue pages.", 1)
    mock_logger_info.assert_any_call("Markdown page generation - generated `_index.md`")


def test_generate_markdown_pages_with_topic_grouping_enabled_and_structured_output_disabled(mocker, generator, consolidated_issue, load_all_templates_setup):
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_is_structured_output_enabled", return_value=False)
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True)
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_output_directory", return_value="/base/output")

    mock_load_all_templates = load_all_templates_setup
    mock_generate_md_issue_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_md_issue_page")
    mock_generate_root_level_index_page = mocker.patch("living_documentation_generator.generator.generate_root_level_index_page")
    mock_generate_structured_index_pages = mocker.patch.object(LivingDocumentationGenerator, "_generate_structured_index_pages")
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")

    consolidated_issue.topics = ["documentationTopic, FETopic"]
    issues = {"issue_1": consolidated_issue, "issue_2": consolidated_issue}

    generator._generate_markdown_pages(issues)

    # Assertions
    mock_load_all_templates.assert_called_once()
    assert mock_generate_md_issue_page.call_count == 2
    mock_generate_md_issue_page.assert_any_call("Issue Page Template", consolidated_issue)
    mock_generate_root_level_index_page.assert_called_once_with("Root Level Page Template", "/base/output")
    mock_generate_structured_index_pages.assert_not_called()
    mock_generate_index_page.assert_called_once_with("Data Level Template", list(issues.values()), topic="documentationTopic")


# _generate_md_issue_page


def test_generate_md_issue_page(mocker, generator, consolidated_issue):
    # Arrange
    mock_generate_issue_summary_table = mocker.patch.object(LivingDocumentationGenerator, "_generate_issue_summary_table", return_value="Generated Issue Summary Table")
    mock_makedirs = mocker.patch("os.makedirs")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    issue_page_template = "Title: {title}\nDate: {date}\nSummary:\n{issue_summary_table}\nContent:\n{issue_content}"
    consolidated_issue.generate_directory_path = mocker.Mock(return_value=["/base/output/org/repo/issues"])
    consolidated_issue.generate_page_filename = mocker.Mock(return_value="issue_42.md")

    # Act
    generator._generate_md_issue_page(issue_page_template, consolidated_issue)

    # Assert
    expected_date = datetime.now().strftime("%Y-%m-%d")
    expected_content = (
        f"Title: Sample Issue\nDate: {expected_date}\nSummary:\nGenerated Issue Summary Table\nContent:\nThis is the issue content."
    )

    mock_generate_issue_summary_table.assert_called_once_with(consolidated_issue)
    mock_makedirs.assert_called_once_with("/base/output/org/repo/issues", exist_ok=True)
    mock_open.assert_called_once_with("/base/output/org/repo/issues/issue_42.md", "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_content)


# _generate_structured_index_pages


def test_generate_structured_index_pages_with_topic_grouping_enabled(
    mocker, generator, consolidated_issue
):
    # Arrange
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True
    )

    mock_generate_sub_level_index_page = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_sub_level_index_page"
    )
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")
    mock_logger_info = mocker.patch("living_documentation_generator.generator.logger.info")
    mock_logger_debug = mocker.patch("living_documentation_generator.generator.logger.debug")

    index_data_level_template = "Data Level Template"
    index_repo_level_template = "Repo Level Template"
    index_org_level_template = "Org Level Template"
    consolidated_issues = {"issue_1": consolidated_issue, "issue_2": consolidated_issue}

    # Act
    generator._generate_structured_index_pages(
        index_data_level_template,
        index_repo_level_template,
        index_org_level_template,
        consolidated_issues,
    )

    # Assert
    mock_generate_sub_level_index_page.assert_any_call(index_org_level_template, "org", "TestOrg/TestRepo")
    mock_generate_sub_level_index_page.assert_any_call(index_repo_level_template, "repo", "TestOrg/TestRepo")
    mock_generate_index_page.assert_called_once_with(
        index_data_level_template, [consolidated_issue, consolidated_issue], "TestOrg/TestRepo", "documentationTopic"
    )
    mock_logger_info.assert_called_once_with(
        "Markdown page generation - generated `_index.md` pages for %s.", "TestOrg/TestRepo"
    )
    mock_logger_debug.assert_any_call("Generated organization level `_index.md` for %s.", "TestOrg")
    mock_logger_debug.assert_any_call("Generated repository level _index.md` for repository: %s.", "TestRepo")
    mock_logger_debug.assert_any_call("Generated data level `_index.md` with topic: %s for %s.", "documentationTopic", "TestOrg/TestRepo")


def test_generate_structured_index_pages_with_topic_grouping_disabled(mocker, generator, consolidated_issue):
    # Arrange
    mocker.patch("living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=False)

    mock_generate_sub_level_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_sub_level_index_page")
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")
    mock_logger_debug = mocker.patch("living_documentation_generator.generator.logger.debug")

    index_data_level_template = "Data Level Template"
    index_repo_level_template = "Repo Level Template"
    index_org_level_template = "Org Level Template"
    consolidated_issue.repository_id = "TestOrg/TestRepo"
    consolidated_issues = {"issue_1": consolidated_issue, "issue_2": consolidated_issue}

    # Act
    generator._generate_structured_index_pages(
        index_data_level_template,
        index_repo_level_template,
        index_org_level_template,
        consolidated_issues,
    )

    # Assert
    mock_generate_sub_level_index_page.assert_called_once_with(index_org_level_template, "org", "TestOrg/TestRepo")
    mock_generate_index_page.assert_called_once_with(index_data_level_template, [consolidated_issue, consolidated_issue], "TestOrg/TestRepo")
    mock_logger_debug.assert_any_call("Generated organization level `_index.md` for %s.", "TestOrg")
    mock_logger_debug.assert_any_call("Generated data level `_index.md` for %s", "TestOrg/TestRepo")


# _generate_index_page


def test_generate_index_page_with_all_features_enabled(mocker, generator, consolidated_issue, project_status):
    # Arrange
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_project_state_mining_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_structured_output_enabled", return_value=True
    )

    mock_generate_index_directory_path = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_index_directory_path", return_value="/base/output/org/repo/topic"
    )
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.makedirs")

    issue_index_page_template = "Date: {date}\nIssues:\n{issue_overview_table}\nData Level: {data_level_name}"
    consolidated_issue.linked_to_project = True
    consolidated_issue.project_issue_statuses = [project_status]
    consolidated_issues = [consolidated_issue, consolidated_issue]

    repository_id = "TestOrg/TestRepo"
    topic = "documentationTopic"

    expected_date = datetime.now().strftime("%Y-%m-%d")
    expected_issue_line = "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🟢 | In Progress |<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    expected_issue_table = TABLE_HEADER_WITH_PROJECT_DATA + expected_issue_line + expected_issue_line
    expected_data_level_name = "documentationTopic"
    expected_index_page_content = (
        f"Date: {expected_date}\nIssues:\n{expected_issue_table}\nData Level: {expected_data_level_name}"
    )
    expected_output_path = "/base/output/org/repo/topic/_index.md"

    # Act
    generator._generate_index_page(issue_index_page_template, consolidated_issues, repository_id, topic)

    # Assert
    mock_generate_index_directory_path.assert_called_once_with(repository_id, topic)
    mock_open.assert_called_once_with(expected_output_path, "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_index_page_content)


def test_generate_index_page_with_topic_grouping_disabled_structured_output_project_mining_enabled(
    mocker, generator, consolidated_issue, project_status
):
    # Arrange
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_project_state_mining_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=False
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_structured_output_enabled", return_value=True
    )

    mock_generate_index_directory_path = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_index_directory_path", return_value="/base/output/org/repo"
    )
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.makedirs")

    issue_index_page_template = "Date: {date}\nIssues:\n{issue_overview_table}\nData Level: {data_level_name}"
    consolidated_issue.linked_to_project = True
    consolidated_issue.project_issue_statuses = [project_status]
    consolidated_issues = [consolidated_issue, consolidated_issue]

    repository_id = "TestOrg/TestRepo"
    topic = None

    expected_date = datetime.now().strftime("%Y-%m-%d")
    expected_issue_line = "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🟢 | In Progress |<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    expected_issue_table = TABLE_HEADER_WITH_PROJECT_DATA + expected_issue_line + expected_issue_line
    expected_data_level_name = "TestRepo"
    expected_index_page_content = (
        f"Date: {expected_date}\nIssues:\n{expected_issue_table}\nData Level: {expected_data_level_name}"
    )
    expected_output_path = "/base/output/org/repo/_index.md"

    # Act
    generator._generate_index_page(issue_index_page_template, consolidated_issues, repository_id, topic)

    # Assert
    mock_generate_index_directory_path.assert_called_once_with(repository_id, topic)
    mock_open.assert_called_once_with(expected_output_path, "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_index_page_content)


def test_generate_index_page_with_topic_grouping_and_structured_output_disabled_project_mining_enabled(
    mocker, generator, consolidated_issue, project_status
):
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_project_state_mining_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=False
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_structured_output_enabled", return_value=False
    )

    mock_generate_index_directory_path = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_index_directory_path", return_value="/base/output"
    )
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.makedirs")

    issue_index_page_template = "Date: {date}\nIssues:\n{issue_overview_table}\n"
    consolidated_issue.project_issue_statuses = [project_status]
    consolidated_issues = [consolidated_issue, consolidated_issue]

    repository_id = None
    topic = None

    expected_date = datetime.now().strftime("%Y-%m-%d")
    expected_issue_line = "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🔴 | In Progress |<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    expected_issue_table = TABLE_HEADER_WITH_PROJECT_DATA + expected_issue_line + expected_issue_line
    expected_index_page_content = f"Date: {expected_date}\nIssues:\n{expected_issue_table}\n"
    expected_output_path = "/base/output/_index.md"

    generator._generate_index_page(issue_index_page_template, consolidated_issues, repository_id, topic)

    mock_generate_index_directory_path.assert_called_once_with(repository_id, topic)
    mock_open.assert_called_once_with(expected_output_path, "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_index_page_content)


# _generate_sub_level_index_page


def test_generate_sub_level_index_page_for_org_level(mocker):
    mock_get_output_directory = mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_output_directory", return_value="/base/output"
    )
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.makedirs")

    index_template = "Organization: {organization_name}, Date: {date}"
    level = "org"
    repository_id = "TestOrg/TestRepo"

    expected_replacement_content = f"Organization: TestOrg, Date: {datetime.now().strftime('%Y-%m-%d')}"
    expected_output_path = "/base/output/TestOrg/_index.md"

    LivingDocumentationGenerator._generate_sub_level_index_page(index_template, level, repository_id)

    mock_get_output_directory.assert_called_once()
    mock_open.assert_called_once_with(expected_output_path, "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_replacement_content)


def test_generate_sub_level_index_page_for_repo_level(mocker):
    mock_get_output_directory = mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_output_directory", return_value="/base/output"
    )
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.makedirs")

    index_template = "Repository: {repository_name}, Date: {date}"
    level = "repo"
    repository_id = "TestOrg/TestRepo"

    expected_replacement_content = f"Repository: TestRepo, Date: {datetime.now().strftime('%Y-%m-%d')}"
    expected_output_path = "/base/output/TestOrg/TestRepo/_index.md"

    LivingDocumentationGenerator._generate_sub_level_index_page(index_template, level, repository_id)

    mock_get_output_directory.assert_called_once()
    mock_open.assert_called_once_with(expected_output_path, "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_replacement_content)


# _generate_markdown_line


def test_generate_markdown_line_with_project_state_mining_enabled_linked_true(
    mocker, consolidated_issue, project_status
):
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_project_state_mining_enabled", return_value=True
    )

    consolidated_issue.linked_to_project = True
    consolidated_issue.project_issue_statuses = [project_status, project_status]

    expected_md_issue_line = (
        "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🟢 | In Progress, In Progress |"
        "<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    )

    actual_md_issue_line = LivingDocumentationGenerator._generate_markdown_line(consolidated_issue)

    assert expected_md_issue_line == actual_md_issue_line


def test_generate_markdown_line_with_project_state_mining_enabled_linked_false(
    mocker, consolidated_issue, project_status
):
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_project_state_mining_enabled", return_value=True
    )

    consolidated_issue.project_issue_statuses = [project_status]

    expected_md_issue_line = (
        "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🔴 | In Progress |"
        "<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    )

    actual_md_issue_line = LivingDocumentationGenerator._generate_markdown_line(consolidated_issue)

    assert expected_md_issue_line == actual_md_issue_line


def test_generate_markdown_line_with_project_state_mining_disabled(mocker, consolidated_issue, project_status):
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_project_state_mining_enabled", return_value=False
    )

    consolidated_issue.project_issue_statuses = [project_status]

    expected_md_issue_line = (
        "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | OPEN |"
        "<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    )

    actual_md_issue_line = LivingDocumentationGenerator._generate_markdown_line(consolidated_issue)

    assert expected_md_issue_line == actual_md_issue_line


# _generate_issue_summary_table


def test_generate_issue_summary_table_without_project_state_mining(mocker, consolidated_issue):
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_project_state_mining_enabled", return_value=False
    )
    expected_issue_info = (
        "| Attribute | Content |\n"
        "|---|---|\n"
        "| Organization name | TestOrg |\n"
        "| Repository name | TestRepo |\n"
        "| Issue number | 42 |\n"
        "| State | open |\n"
        "| Issue URL | <a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a>  |\n"
        "| Created at | 2024-01-01T00:00:00Z |\n"
        "| Updated at | 2024-01-02T00:00:00Z |\n"
        "| Closed at | None |\n"
        "| Labels | bug, urgent |\n"
    )

    actual_issue_info = LivingDocumentationGenerator._generate_issue_summary_table(consolidated_issue)

    assert expected_issue_info == actual_issue_info


def test_generate_issue_summary_table_with_project_state_mining_and_multiple_project_statuses(
    mocker, consolidated_issue, project_status
):
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_project_state_mining_enabled", return_value=True
    )

    consolidated_issue.linked_to_project = True
    consolidated_issue.project_issue_statuses = [project_status, project_status]

    expected_issue_info = (
        "| Attribute | Content |\n"
        "|---|---|\n"
        "| Organization name | TestOrg |\n"
        "| Repository name | TestRepo |\n"
        "| Issue number | 42 |\n"
        "| State | open |\n"
        "| Issue URL | <a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a>  |\n"
        "| Created at | 2024-01-01T00:00:00Z |\n"
        "| Updated at | 2024-01-02T00:00:00Z |\n"
        "| Closed at | None |\n"
        "| Labels | bug, urgent |\n"
        "| Project title | Test Project |\n"
        "| Status | In Progress |\n"
        "| Priority | High |\n"
        "| Size | Large |\n"
        "| MoSCoW | Must Have |\n"
        "| Project title | Test Project |\n"
        "| Status | In Progress |\n"
        "| Priority | High |\n"
        "| Size | Large |\n"
        "| MoSCoW | Must Have |\n"
    )

    actual_issue_info = LivingDocumentationGenerator._generate_issue_summary_table(consolidated_issue)

    assert expected_issue_info == actual_issue_info


def test_generate_issue_summary_table_with_project_state_mining_but_no_linked_project(
    mocker, consolidated_issue, project_status
):
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_project_state_mining_enabled", return_value=True
    )

    consolidated_issue.linked_to_project = False

    expected_issue_info = (
        "| Attribute | Content |\n"
        "|---|---|\n"
        "| Organization name | TestOrg |\n"
        "| Repository name | TestRepo |\n"
        "| Issue number | 42 |\n"
        "| State | open |\n"
        "| Issue URL | <a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a>  |\n"
        "| Created at | 2024-01-01T00:00:00Z |\n"
        "| Updated at | 2024-01-02T00:00:00Z |\n"
        "| Closed at | None |\n"
        "| Labels | bug, urgent |\n"
        "| Linked to project | 🔴 |\n"
    )

    actual_issue_info = LivingDocumentationGenerator._generate_issue_summary_table(consolidated_issue)

    assert expected_issue_info == actual_issue_info


# _generate_index_directory_path


def test_generate_index_directory_path_with_structured_output_grouped_by_topics(mocker):
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_output_directory", return_value="/base/output"
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_structured_output_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True
    )
    mocker.patch("os.makedirs")

    repository_id = "org123/repo456"
    topic = "documentation"
    expected_path = "/base/output/org123/repo456/documentation"

    actual_path = LivingDocumentationGenerator._generate_index_directory_path(repository_id, topic)

    assert expected_path == actual_path


def test_generate_index_directory_path_with_structured_output_not_grouped_by_topics(mocker):
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_output_directory", return_value="/base/output"
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_structured_output_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=False
    )
    mocker.patch("os.makedirs")

    repository_id = "org123/repo456"
    topic = None
    expected_path = "/base/output/org123/repo456"

    actual_path = LivingDocumentationGenerator._generate_index_directory_path(repository_id, topic)

    assert expected_path == actual_path


def test_generate_index_directory_path_with_only_grouping_by_topic_no_structured_output(mocker):
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_output_directory", return_value="/base/output"
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_structured_output_enabled", return_value=False
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True
    )
    mocker.patch("os.makedirs")

    repository_id = "org123/repo456"
    topic = "documentation"
    expected_path = "/base/output/documentation"

    actual_path = LivingDocumentationGenerator._generate_index_directory_path(repository_id, topic)

    assert expected_path == actual_path


def test_generate_index_directory_path_with_no_structured_output_and_no_grouping_by_topics(mocker):
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_output_directory", return_value="/base/output"
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_structured_output_enabled", return_value=False
    )
    mocker.patch(
        "living_documentation_generator.generator.ActionInputs.get_is_grouping_by_topics_enabled", return_value=False
    )
    mocker.patch("os.makedirs")

    repository_id = None
    topic = None
    expected_path = "/base/output"

    actual_path = LivingDocumentationGenerator._generate_index_directory_path(repository_id, topic)

    assert expected_path == actual_path


# _load_all_templates


def test_load_all_templates_loads_correctly(mocker):
    load_template_mock = mocker.patch("living_documentation_generator.generator.load_template")
    load_template_mock.side_effect = [
        "Issue Page Template Content",
        "Index Page Template Content",
        "Root Level Template Content",
        "Organization Level Template Content",
        "Repository Level Template Content",
        "Data Level Template Content",
    ]

    expected_templates = (
        "Issue Page Template Content",
        "Index Page Template Content",
        "Root Level Template Content",
        "Organization Level Template Content",
        "Repository Level Template Content",
        "Data Level Template Content",
    )

    actual_templates = LivingDocumentationGenerator._load_all_templates()

    assert actual_templates == expected_templates
    assert load_template_mock.call_count == 6


def test_load_all_templates_loads_just_some_templates(mocker):
    load_template_mock = mocker.patch("living_documentation_generator.generator.load_template")
    load_template_mock.side_effect = [
        None,
        None,
        None,
        None,
        None,
        "Data Level Template Content",
    ]

    expected_templates = (
        None,
        None,
        None,
        None,
        None,
        "Data Level Template Content",
    )

    actual_templates = LivingDocumentationGenerator._load_all_templates()

    assert actual_templates == expected_templates
    assert load_template_mock.call_count == 6
