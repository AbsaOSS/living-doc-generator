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

from github.Issue import Issue

from living_documentation_regime.living_documentation_generator import LivingDocumentationGenerator
from living_documentation_regime.model.consolidated_issue import ConsolidatedIssue
from living_documentation_regime.model.project_issue import ProjectIssue


# generate


def test_generate_correct_behaviour(mocker, living_documentation_generator):
    # Arrange
    mock_clean_output_directory = mocker.patch.object(living_documentation_generator, "_clean_output_directory")
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")
    mock_logger_debug = mocker.patch("living_documentation_regime.living_documentation_generator.logger.debug")

    mock_issue = mocker.Mock()
    project_issue_mock = mocker.Mock()
    consolidated_issue_mock = mocker.Mock()

    mock_fetch_github_issues = mocker.patch.object(
        living_documentation_generator, "_fetch_github_issues", return_value={"test_org/test_repo": [mock_issue]}
    )
    mock_fetch_github_project_issues = mocker.patch.object(
        living_documentation_generator,
        "_fetch_github_project_issues",
        return_value={"test_org/test_repo#1": [project_issue_mock]},
    )
    mock_consolidate_issues_data = mocker.patch.object(
        living_documentation_generator,
        "_consolidate_issues_data",
        return_value={"test_org/test_repo#1": consolidated_issue_mock},
    )
    mock_generate_markdown_pages = mocker.patch.object(living_documentation_generator, "_generate_markdown_pages")

    # Act
    living_documentation_generator.generate()

    # Assert
    mock_clean_output_directory.assert_called_once()
    mock_fetch_github_issues.assert_called_once()
    mock_fetch_github_project_issues.assert_called_once()
    mock_consolidate_issues_data.assert_called_once_with(
        {"test_org/test_repo": [mock_issue]}, {"test_org/test_repo#1": [project_issue_mock]}
    )
    mock_generate_markdown_pages.assert_called_once_with({"test_org/test_repo#1": consolidated_issue_mock})
    mock_logger_debug.assert_called_once_with("Output directory cleaned.")
    mock_logger_info.assert_has_calls(
        [
            mocker.call("Fetching repository GitHub issues - started."),
            mocker.call("Fetching repository GitHub issues - finished."),
            mocker.call("Fetching GitHub project data - started."),
            mocker.call("Fetching GitHub project data - finished."),
            mocker.call("Issue and project data consolidation - started."),
            mocker.call("Issue and project data consolidation - finished."),
            mocker.call("Markdown page generation - started."),
            mocker.call("Markdown page generation - finished."),
        ],
        any_order=True,
    )


# _clean_output_directory


def test_clean_output_directory_correct_behaviour(mocker, living_documentation_generator):
    # Arrange
    mock_output_path = "/test/output/path"
    mock_get_output_directory = mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value=mock_output_path,
    )
    mock_exists = mocker.patch("os.path.exists", return_value=True)
    mock_rmtree = mocker.patch("shutil.rmtree")
    mock_makedirs = mocker.patch("os.makedirs")

    # Act
    living_documentation_generator._clean_output_directory()

    # Assert
    mock_get_output_directory.assert_called_once()
    mock_exists.assert_called_once_with(mock_output_path)
    mock_rmtree.assert_called_once_with(mock_output_path)
    mock_makedirs.assert_called_once_with(mock_output_path)


# _fetch_github_issues


def test_fetch_github_issues_no_query_labels(mocker, living_documentation_generator, config_repository):
    # Arrange
    config_repository.query_labels = []
    repo = mocker.Mock()
    repo.full_name = "test_org/test_repo"
    issue1 = mocker.Mock()
    issue2 = mocker.Mock()
    issue3 = mocker.Mock()

    expected_issues = {"test_org/test_repo": [issue1, issue2, issue3]}
    mock_get_repo = living_documentation_generator._LivingDocumentationGenerator__github_instance.get_repo
    mock_get_repo.return_value = repo

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_repositories",
        return_value=[config_repository],
    )
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")
    mock_logger_debug = mocker.patch("living_documentation_regime.living_documentation_generator.logger.debug")
    mock_get_issues = mocker.patch.object(repo, "get_issues", return_value=[issue1, issue2, issue3])

    # Act
    actual = living_documentation_generator._fetch_github_issues()

    # Assert
    assert expected_issues == actual
    assert 1 == len(actual)
    assert 3 == len(actual["test_org/test_repo"])
    mock_get_repo.assert_called_once_with("test_org/test_repo")
    mock_get_issues.assert_called_once_with(state="all")
    mock_logger_info.assert_has_calls(
        [
            mocker.call("Fetching repository GitHub issues - from `%s`.", "test_org/test_repo"),
            mocker.call(
                "Fetching repository GitHub issues - fetched `%i` repository issues (%s).", 3, "test_org/test_repo"
            ),
            mocker.call("Fetching repository GitHub issues - loaded `%i` repository issues in total.", 3),
        ],
        any_order=True,
    )
    mock_logger_debug.assert_has_calls(
        [
            mocker.call("Fetching all issues in the repository"),
            mocker.call("Fetched `%i` repository issues (%s)`.", 3, "test_org/test_repo"),
        ],
        any_order=True,
    )


def test_fetch_github_issues_with_given_query_labels(mocker, living_documentation_generator, config_repository):
    # Arrange
    config_repository.query_labels = ["bug", "enhancement"]
    repo = mocker.Mock()
    repo.full_name = "test_org/test_repo"
    issue1 = mocker.Mock()
    issue2 = mocker.Mock()

    expected_issues = {"test_org/test_repo": [issue1, issue2]}
    mock_get_repo = living_documentation_generator._LivingDocumentationGenerator__github_instance.get_repo
    mock_get_repo.return_value = repo

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_repositories",
        return_value=[config_repository],
    )
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")
    mock_logger_debug = mocker.patch("living_documentation_regime.living_documentation_generator.logger.debug")
    mock_get_issues = mocker.patch.object(repo, "get_issues", side_effect=[[issue1], [issue2]])

    # Act
    actual = living_documentation_generator._fetch_github_issues()

    # Assert
    assert expected_issues == actual
    assert 1 == len(actual)
    mock_get_repo.assert_called_once_with("test_org/test_repo")
    mock_get_issues.assert_any_call(state="all", labels=["bug"])
    mock_get_issues.assert_any_call(state="all", labels=["enhancement"])
    mock_logger_info.assert_has_calls(
        [
            mocker.call("Fetching repository GitHub issues - from `%s`.", "test_org/test_repo"),
            mocker.call(
                "Fetching repository GitHub issues - fetched `%i` repository issues (%s).", 2, "test_org/test_repo"
            ),
            mocker.call("Fetching repository GitHub issues - loaded `%i` repository issues in total.", 2),
        ],
        any_order=True,
    )
    mock_logger_debug.assert_has_calls(
        [
            mocker.call("Labels to be fetched from: %s.", config_repository.query_labels),
            mocker.call("Fetching issues with label `%s`.", "bug"),
            mocker.call("Fetching issues with label `%s`.", "enhancement"),
        ],
        any_order=True,
    )


def test_fetch_github_issues_repository_none(mocker, living_documentation_generator, config_repository):
    # Arrange
    mock_get_repo = living_documentation_generator._LivingDocumentationGenerator__github_instance.get_repo
    mock_get_repo.return_value = None
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_repositories",
        return_value=[config_repository],
    )

    # Act
    actual = living_documentation_generator._fetch_github_issues()

    # Assert
    assert {} == actual
    mock_get_repo.assert_called_once_with("test_org/test_repo")


# _fetch_github_project_issues


def test_fetch_github_project_issues_correct_behaviour(mocker, living_documentation_generator):
    # Arrange
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=True,
    )
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")
    mock_logger_debug = mocker.patch("living_documentation_regime.living_documentation_generator.logger.debug")

    repository_1 = mocker.Mock()
    repository_1.organization_name = "OrgA"
    repository_1.repository_name = "RepoA"
    repository_1.projects_title_filter = ""

    repository_2 = mocker.Mock()
    repository_2.organization_name = "OrgA"
    repository_2.repository_name = "RepoB"
    repository_2.projects_title_filter = "ProjectB"

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_repositories",
        return_value=[repository_1, repository_2],
    )

    mock_github_projects_instance = mocker.patch.object(
        living_documentation_generator, "_LivingDocumentationGenerator__github_projects_instance"
    )

    repo_a = mocker.Mock()
    repo_a.full_name = "OrgA/RepoA"
    repo_b = mocker.Mock()
    repo_b.full_name = "OrgA/RepoB"
    living_documentation_generator._LivingDocumentationGenerator__github_instance.get_repo.side_effect = [
        repo_a,
        repo_b,
    ]

    project_a = mocker.Mock(title="Project A")
    project_b = mocker.Mock(title="Project B")
    mock_github_projects_instance.get_repository_projects.side_effect = [[project_a], [project_b]]

    project_status_1 = mocker.Mock()
    project_status_1.status = "In Progress"

    project_status_2 = mocker.Mock()
    project_status_2.status = "Done"

    project_issue_1 = mocker.Mock(spec=ProjectIssue)
    project_issue_1.organization_name = "OrgA"
    project_issue_1.repository_name = "RepoA"
    project_issue_1.number = 1
    project_issue_1.project_status = project_status_1

    # By creating two same Project Issues (same unique issue key) that has different project statuses
    # we test the situation where one issue is linked to more projects (need of keeping all project statuses)
    project_issue_2 = mocker.Mock(spec=ProjectIssue)
    project_issue_2.organization_name = "OrgA"
    project_issue_2.repository_name = "RepoA"
    project_issue_2.number = 1
    project_issue_2.project_status = project_status_2

    mock_github_projects_instance.get_project_issues.side_effect = [[project_issue_1], [project_issue_2]]

    mock_make_issue_key = mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_issue_key",
        side_effect=lambda org, repo, num: f"{org}/{repo}#{num}",
    )

    # Act
    actual = living_documentation_generator._fetch_github_project_issues()

    # Assert
    assert mock_make_issue_key.call_count == 2
    assert len(actual) == 1
    assert "OrgA/RepoA#1" in actual
    assert actual["OrgA/RepoA#1"] == [project_issue_1, project_issue_2]

    living_documentation_generator._LivingDocumentationGenerator__github_instance.get_repo.assert_any_call("OrgA/RepoA")
    living_documentation_generator._LivingDocumentationGenerator__github_instance.get_repo.assert_any_call("OrgA/RepoB")
    mock_github_projects_instance.get_repository_projects.assert_any_call(repository=repo_a, projects_title_filter="")
    mock_github_projects_instance.get_repository_projects.assert_any_call(
        repository=repo_b, projects_title_filter="ProjectB"
    )
    mock_github_projects_instance.get_project_issues.assert_any_call(project=project_a)
    mock_github_projects_instance.get_project_issues.assert_any_call(project=project_b)
    mock_logger_info.assert_has_calls(
        [
            mocker.call("Fetching GitHub project data - for repository `%s` found `%i` project/s.", "OrgA/RepoA", 1),
            mocker.call("Fetching GitHub project data - fetching project data from `%s`.", "Project A"),
            mocker.call("Fetching GitHub project data - successfully fetched project data from `%s`.", "Project A"),
            mocker.call("Fetching GitHub project data - for repository `%s` found `%i` project/s.", "OrgA/RepoB", 1),
            mocker.call("Fetching GitHub project data - fetching project data from `%s`.", "Project B"),
            mocker.call("Fetching GitHub project data - successfully fetched project data from `%s`.", "Project B"),
        ],
        any_order=True,
    )
    mock_logger_debug.assert_has_calls(
        [
            mocker.call("Project data mining allowed."),
            mocker.call("Filtering projects: %s. If filter is empty, fetching all.", ""),
            mocker.call("Filtering projects: %s. If filter is empty, fetching all.", "ProjectB"),
            mocker.call("Fetching GitHub project data - looking for repository `%s` projects.", "OrgA/RepoA"),
            mocker.call("Fetching GitHub project data - looking for repository `%s` projects.", "OrgA/RepoB"),
        ],
        any_order=True,
    )


def test_fetch_github_project_issues_project_mining_disabled(mocker, living_documentation_generator):
    # Arrange
    mock_get_project_mining_enabled = mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=False,
    )
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")

    # Act
    actual = living_documentation_generator._fetch_github_project_issues()

    # Assert
    assert {} == actual
    mock_get_project_mining_enabled.assert_called_once()
    mock_logger_info.assert_called_once_with("Fetching GitHub project data - project mining is not allowed.")


def test_fetch_github_project_issues_no_repositories(mocker, living_documentation_generator, config_repository):
    # Arrange
    mock_get_repo = living_documentation_generator._LivingDocumentationGenerator__github_instance.get_repo
    mock_get_repo.return_value = None

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_repositories",
        return_value=[config_repository],
    )

    # Act
    actual = living_documentation_generator._fetch_github_project_issues()

    # Assert
    assert {} == actual
    mock_get_repo.assert_called_once_with("test_org/test_repo")


def test_fetch_github_project_issues_with_no_projects(mocker, living_documentation_generator, config_repository):
    # Arrange
    mock_get_repo = living_documentation_generator._LivingDocumentationGenerator__github_instance.get_repo
    repo_a = mocker.Mock()
    repo_a.full_name = "test_org/test_repo"
    mock_get_repo.return_value = repo_a

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_repositories",
        return_value=[config_repository],
    )
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")
    mock_get_repository_projects = mocker.patch.object(
        living_documentation_generator._LivingDocumentationGenerator__github_projects_instance,
        "get_repository_projects",
        return_value=[],
    )

    # Act
    actual = living_documentation_generator._fetch_github_project_issues()

    # Assert
    assert {} == actual
    mock_get_repo.assert_called_once_with("test_org/test_repo")
    mock_get_repository_projects.assert_called_once_with(repository=repo_a, projects_title_filter=[])
    mock_logger_info.assert_called_once_with(
        "Fetching GitHub project data - no project data found for repository `%s`.", "test_org/test_repo"
    )


# _consolidate_issues_data


def test_consolidate_issues_data_correct_behaviour(mocker, living_documentation_generator):
    # Arrange
    consolidated_issue_mock_1 = mocker.Mock(spec=ConsolidatedIssue)
    consolidated_issue_mock_2 = mocker.Mock(spec=ConsolidatedIssue)
    repository_issues = {"TestOrg/TestRepo": [mocker.Mock(spec=Issue, number=1), mocker.Mock(spec=Issue, number=2)]}
    project_issues = {
        "TestOrg/TestRepo#1": [mocker.Mock(spec=ProjectIssue, project_status="In Progress")],
        "TestOrg/TestRepo#2": [mocker.Mock(spec=ProjectIssue, project_status="Done")],
    }

    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")
    mock_logger_debug = mocker.patch("living_documentation_regime.living_documentation_generator.logger.debug")
    mock_make_issue_key = mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_issue_key",
        side_effect=lambda org, repo, num: f"{org}/{repo}#{num}",
    )
    mock_consolidated_issue_class = mocker.patch(
        "living_documentation_regime.living_documentation_generator.ConsolidatedIssue",
        side_effect=[consolidated_issue_mock_1, consolidated_issue_mock_2],
    )

    # Act
    actual = living_documentation_generator._consolidate_issues_data(repository_issues, project_issues)

    # Assert
    assert 2 == len(actual)
    assert 2 == mock_consolidated_issue_class.call_count
    assert 2 == mock_make_issue_key.call_count
    assert actual["TestOrg/TestRepo#1"] == consolidated_issue_mock_1
    assert actual["TestOrg/TestRepo#2"] == consolidated_issue_mock_2
    consolidated_issue_mock_1.update_with_project_data.assert_called_once_with("In Progress")
    consolidated_issue_mock_2.update_with_project_data.assert_called_once_with("Done")
    mock_logger_info.assert_called_once_with(
        "Issue and project data consolidation - consolidated `%i` repository issues with extra project data.", 2
    )
    mock_logger_debug.assert_called_once_with("Updating consolidated issue structure with project data.")


# _generate_markdown_pages


def test_generate_markdown_pages_with_structured_output_and_topic_grouping_enabled(
    mocker, living_documentation_generator, consolidated_issue, load_all_templates_setup
):
    # Arrange
    mock_load_all_templates = load_all_templates_setup
    topics = {"documentationTopic"}
    issues = {"issue_1": consolidated_issue, "issue_2": consolidated_issue}

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value="/base/output",
    )
    mock_generate_root_level_index_page = mocker.patch(
        "living_documentation_regime.living_documentation_generator.generate_root_level_index_page"
    )
    mock_generate_structured_index_pages = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_structured_index_pages"
    )
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")
    mock_generate_md_issue_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_md_issue_page")

    # Act
    living_documentation_generator._generate_markdown_pages(issues)

    # Assert
    assert 2 == mock_generate_md_issue_page.call_count
    mock_load_all_templates.assert_called_once()
    mock_generate_md_issue_page.assert_any_call("Issue Page Template", consolidated_issue)
    mock_generate_root_level_index_page.assert_called_once_with("Root Level Page Template", "/base/output")
    mock_generate_structured_index_pages.assert_called_once_with(
        "Data Level Template", "Repo Page Template", "Org Level Template", topics, issues
    )
    mock_generate_index_page.assert_not_called()
    mock_logger_info.assert_called_once_with("Markdown page generation - generated `%i` issue pages.", 2)


def test_generate_markdown_pages_with_structured_output_enabled_and_topic_grouping_disabled(
    mocker, living_documentation_generator, consolidated_issue, load_all_templates_setup
):
    # Arrange
    topics = {"documentationTopic", "FETopic"}
    consolidated_issue.topics = ["documentationTopic", "FETopic"]
    issues = {"issue_1": consolidated_issue, "issue_2": consolidated_issue, "issue_3": consolidated_issue}

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value="/base/output",
    )
    mock_generate_md_issue_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_md_issue_page")
    mock_generate_root_level_index_page = mocker.patch(
        "living_documentation_regime.living_documentation_generator.generate_root_level_index_page"
    )
    mock_generate_structured_index_pages = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_structured_index_pages"
    )
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")

    # Act
    living_documentation_generator._generate_markdown_pages(issues)

    # Assert
    assert 3 == mock_generate_md_issue_page.call_count
    load_all_templates_setup.assert_called_once()
    mock_generate_md_issue_page.assert_any_call("Issue Page Template", consolidated_issue)
    mock_generate_root_level_index_page.assert_called_once_with("Root Level Page Template", "/base/output")
    mock_generate_structured_index_pages.assert_called_once_with(
        "Data Level Template", "Repo Page Template", "Org Level Template", topics, issues
    )
    mock_logger_info.assert_called_once_with("Markdown page generation - generated `%i` issue pages.", 3)


def test_generate_markdown_pages_with_structured_output_and_topic_grouping_disabled(
    mocker, living_documentation_generator, consolidated_issue, load_all_templates_setup
):
    # Arrange
    issues = {"issue_1": consolidated_issue}

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=False,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value="/base/output",
    )
    mock_generate_md_issue_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_md_issue_page")
    mock_generate_root_level_index_page = mocker.patch(
        "living_documentation_regime.living_documentation_generator.generate_root_level_index_page"
    )
    mock_generate_structured_index_pages = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_structured_index_pages"
    )
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")

    # Act
    living_documentation_generator._generate_markdown_pages(issues)

    # Assert
    load_all_templates_setup.assert_called_once()
    assert mock_generate_md_issue_page.call_count == 1
    mock_generate_md_issue_page.assert_any_call("Issue Page Template", consolidated_issue)
    mock_generate_root_level_index_page.assert_not_called()
    mock_generate_structured_index_pages.assert_not_called()
    mock_generate_index_page.assert_called_once_with("Index Page Template", list(issues.values()))
    mock_logger_info.assert_any_call("Markdown page generation - generated `%i` issue pages.", 1)
    mock_logger_info.assert_any_call("Markdown page generation - generated `_index.md`.")


def test_generate_markdown_pages_with_topic_grouping_enabled_and_structured_output_disabled(
    mocker, living_documentation_generator, consolidated_issue, load_all_templates_setup
):
    # Arrange
    consolidated_issue.topics = ["documentationTopic", "FETopic"]
    issues = {"issue_1": consolidated_issue, "issue_2": consolidated_issue}

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=False,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value="/base/output",
    )
    mock_generate_md_issue_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_md_issue_page")
    mock_generate_root_level_index_page = mocker.patch(
        "living_documentation_regime.living_documentation_generator.generate_root_level_index_page"
    )
    mock_generate_structured_index_pages = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_structured_index_pages"
    )
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")

    # Act
    living_documentation_generator._generate_markdown_pages(issues)

    # Assert
    assert 2 == mock_generate_md_issue_page.call_count
    load_all_templates_setup.assert_called_once()
    mock_generate_md_issue_page.assert_any_call("Issue Page Template", consolidated_issue)
    mock_generate_root_level_index_page.assert_called_once_with("Root Level Page Template", "/base/output")
    mock_generate_structured_index_pages.assert_not_called()
    mock_generate_index_page.assert_any_call(
        "Data Level Template", list(issues.values()), grouping_topic="documentationTopic"
    )
    mock_generate_index_page.assert_any_call("Data Level Template", list(issues.values()), grouping_topic="FETopic")


def test_generate_markdown_pages_generates_report_page_with_errors(
    mocker, living_documentation_generator, consolidated_issue, tmp_path
):
    # Arrange
    consolidated_issue.errors = {"ZError": "error z", "AError": "error a"}
    issues = {"issue_1": consolidated_issue}
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=False,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value=str(output_dir),
    )
    mock_templates = (
        "Issue Page Template",
        "Index Page Template",
        "Root Level Page Template",
        "Org Level Template",
        "Repo Page Template",
        "Data Level Template",
        "Report Page Template: Date: {date}\nContent:\n{livdoc_report_page_content}",
    )
    mocker.patch.object(living_documentation_generator, "_load_all_templates", return_value=mock_templates)
    mocker.patch.object(living_documentation_generator, "_generate_md_issue_page")
    mocker.patch.object(living_documentation_generator, "_generate_index_page")
    mock_logger_warning = mocker.patch("living_documentation_regime.living_documentation_generator.logger.warning")

    # Act
    living_documentation_generator._generate_markdown_pages(issues)

    # Assert
    report_file = output_dir / "report_page.md"
    assert report_file.exists()
    report_page_content = report_file.read_text(encoding="utf-8")
    assert "| Error Type | Source | Message |" in report_page_content
    assert "[TestOrg/TestRepo#42](https://github.com/TestOrg/TestRepo/issues/42)" in report_page_content
    assert "error a" in report_page_content
    assert "error z" in report_page_content
    mock_logger_warning.assert_called_once_with("Markdown page generation - Report page generated.")


# _generate_md_issue_page


def test_generate_md_issue_page(mocker, living_documentation_generator, consolidated_issue):
    # Arrange
    issue_page_template = "Title: {title}\nDate: {date}\nSummary:\n{issue_summary_table}\nContent:\n{issue_content}"
    consolidated_issue.generate_directory_path = mocker.Mock(return_value=["/base/output/org/repo/issues"])
    consolidated_issue.generate_page_filename = mocker.Mock(return_value="issue_42.md")
    expected_date = datetime.now().strftime("%Y-%m-%d")
    expected_content = f"Title: Sample Issue\nDate: {expected_date}\nSummary:\nGenerated Issue Summary Table\nContent:\nThis is the issue content."

    mock_generate_issue_summary_table = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_issue_summary_table", return_value="Generated Issue Summary Table"
    )
    mock_makedirs = mocker.patch("os.makedirs")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    # Act
    living_documentation_generator._generate_md_issue_page(issue_page_template, consolidated_issue)

    # Assert
    mock_generate_issue_summary_table.assert_called_once_with(consolidated_issue)
    mock_makedirs.assert_called_once_with("/base/output/org/repo/issues", exist_ok=True)
    mock_open.assert_called_once_with("/base/output/org/repo/issues/issue_42.md", "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_content)


# _generate_structured_index_pages


def test_generate_structured_index_pages_with_topic_grouping_enabled(
    mocker, living_documentation_generator, consolidated_issue
):
    # Arrange
    index_data_level_template = "Data Level Template"
    index_repo_level_template = "Repo Level Template"
    index_org_level_template = "Org Level Template"
    topics = ["documentationTopic"]
    consolidated_issues = {"issue_1": consolidated_issue, "issue_2": consolidated_issue}

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=True,
    )
    mock_generate_sub_level_index_page = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_sub_level_index_page"
    )
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")
    mock_logger_debug = mocker.patch("living_documentation_regime.living_documentation_generator.logger.debug")

    # Act
    living_documentation_generator._generate_structured_index_pages(
        index_data_level_template,
        index_repo_level_template,
        index_org_level_template,
        topics,
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
    mock_logger_debug.assert_any_call(
        "Generated data level `_index.md` with topic: %s for %s.", "documentationTopic", "TestOrg/TestRepo"
    )


def test_generate_structured_index_pages_with_topic_grouping_disabled(
    mocker, living_documentation_generator, consolidated_issue
):
    # Arrange
    index_data_level_template = "Data Level Template"
    index_repo_level_template = "Repo Level Template"
    index_org_level_template = "Org Level Template"
    topics = ["documentationTopic"]
    consolidated_issue.repository_id = "TestOrg/TestRepo"
    consolidated_issues = {"issue_1": consolidated_issue, "issue_2": consolidated_issue}

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mock_generate_sub_level_index_page = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_sub_level_index_page"
    )
    mock_generate_index_page = mocker.patch.object(LivingDocumentationGenerator, "_generate_index_page")
    mock_logger_debug = mocker.patch("living_documentation_regime.living_documentation_generator.logger.debug")

    # Act
    living_documentation_generator._generate_structured_index_pages(
        index_data_level_template,
        index_repo_level_template,
        index_org_level_template,
        topics,
        consolidated_issues,
    )

    # Assert
    mock_generate_sub_level_index_page.assert_called_once_with(index_org_level_template, "org", "TestOrg/TestRepo")
    mock_generate_index_page.assert_called_once_with(
        index_data_level_template, [consolidated_issue, consolidated_issue], "TestOrg/TestRepo"
    )
    mock_logger_debug.assert_any_call("Generated organization level `_index.md` for %s.", "TestOrg")
    mock_logger_debug.assert_any_call("Generated data level `_index.md` for %s", "TestOrg/TestRepo")


# _generate_index_page
TABLE_HEADER_WITH_PROJECT_DATA = """
| Organization name | Repository name | Issue 'Number - Title' |Linked to project | Project status | Issue URL |
|-------------------|-----------------|------------------------|------------------|----------------|-----------|
"""


def test_generate_index_page_with_all_features_enabled(
    mocker, living_documentation_generator, consolidated_issue, project_status
):
    # Arrange
    issue_index_page_template = "Date: {date}\nIssues:\n{issue_overview_table}\nData Level: {data_level_name}"
    consolidated_issue.linked_to_project = True
    consolidated_issue.project_issue_statuses = [project_status]
    consolidated_issues = [consolidated_issue, consolidated_issue]

    repository_id = "TestOrg/TestRepo"
    grouping_topic = "documentationTopic"

    expected_date = datetime.now().strftime("%Y-%m-%d")
    expected_issue_line = "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🟢 | In Progress |<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    expected_issue_table = TABLE_HEADER_WITH_PROJECT_DATA + expected_issue_line + expected_issue_line
    expected_data_level_name = "documentationTopic"
    expected_index_page_content = (
        f"Date: {expected_date}\nIssues:\n{expected_issue_table}\nData Level: {expected_data_level_name}"
    )
    expected_output_path = "/base/output/org/repo/topic/_index.md"

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=True,
    )
    mock_generate_index_directory_path = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_index_directory_path", return_value="/base/output/org/repo/topic"
    )
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.makedirs")

    # Act
    living_documentation_generator._generate_index_page(
        issue_index_page_template, consolidated_issues, repository_id, grouping_topic
    )

    # Assert
    mock_generate_index_directory_path.assert_called_once_with(repository_id, grouping_topic)
    mock_open.assert_called_once_with(expected_output_path, "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_index_page_content)


def test_generate_index_page_with_topic_grouping_disabled_structured_output_project_mining_enabled(
    mocker, living_documentation_generator, consolidated_issue, project_status
):
    # Arrange
    issue_index_page_template = "Date: {date}\nIssues:\n{issue_overview_table}\nData Level: {data_level_name}"
    consolidated_issue.linked_to_project = True
    consolidated_issue.project_issue_statuses = [project_status]
    consolidated_issues = [consolidated_issue, consolidated_issue]

    repository_id = "TestOrg/TestRepo"
    grouping_topic = None

    expected_date = datetime.now().strftime("%Y-%m-%d")
    expected_issue_line = "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🟢 | In Progress |<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    expected_issue_table = TABLE_HEADER_WITH_PROJECT_DATA + expected_issue_line + expected_issue_line
    expected_data_level_name = "TestRepo"
    expected_index_page_content = (
        f"Date: {expected_date}\nIssues:\n{expected_issue_table}\nData Level: {expected_data_level_name}"
    )
    expected_output_path = "/base/output/org/repo/_index.md"

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=True,
    )
    mock_generate_index_directory_path = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_index_directory_path", return_value="/base/output/org/repo"
    )
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.makedirs")

    # Act
    living_documentation_generator._generate_index_page(
        issue_index_page_template, consolidated_issues, repository_id, grouping_topic
    )

    # Assert
    mock_generate_index_directory_path.assert_called_once_with(repository_id, grouping_topic)
    mock_open.assert_called_once_with(expected_output_path, "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_index_page_content)


def test_generate_index_page_with_topic_grouping_and_structured_output_disabled_project_mining_enabled(
    mocker, living_documentation_generator, consolidated_issue, project_status
):
    # Arrange
    issue_index_page_template = "Date: {date}\nIssues:\n{issue_overview_table}\n"
    consolidated_issue.project_issue_statuses = [project_status]
    consolidated_issues = [consolidated_issue, consolidated_issue]

    repository_id = None
    grouping_topic = None

    expected_date = datetime.now().strftime("%Y-%m-%d")
    expected_issue_line = "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🔴 | In Progress |<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    expected_issue_table = TABLE_HEADER_WITH_PROJECT_DATA + expected_issue_line + expected_issue_line
    expected_index_page_content = f"Date: {expected_date}\nIssues:\n{expected_issue_table}\n"
    expected_output_path = "/base/output/_index.md"

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=False,
    )
    mock_generate_index_directory_path = mocker.patch.object(
        LivingDocumentationGenerator, "_generate_index_directory_path", return_value="/base/output"
    )
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.makedirs")

    # Act
    living_documentation_generator._generate_index_page(
        issue_index_page_template, consolidated_issues, repository_id, grouping_topic
    )

    # Assert
    mock_generate_index_directory_path.assert_called_once_with(repository_id, grouping_topic)
    mock_open.assert_called_once_with(expected_output_path, "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_index_page_content)


# _generate_sub_level_index_page


def test_generate_sub_level_index_page_for_org_level(mocker, living_documentation_generator):
    # Arrange
    index_template = "Organization: {organization_name}, Date: {date}"
    level = "org"
    repository_id = "TestOrg/TestRepo"
    expected_replacement_content = f"Organization: TestOrg, Date: {datetime.now().strftime('%Y-%m-%d')}"
    expected_output_path = "/base/output/TestOrg/_index.md"

    mock_get_output_directory = mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value="/base/output",
    )
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.makedirs")

    # Act
    living_documentation_generator._generate_sub_level_index_page(index_template, level, repository_id)

    # Assert
    mock_get_output_directory.assert_called_once()
    mock_open.assert_called_once_with(expected_output_path, "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_replacement_content)


def test_generate_sub_level_index_page_for_repo_level(mocker, living_documentation_generator):
    # Arrange
    index_template = "Repository: {repository_name}, Date: {date}"
    level = "repo"
    repository_id = "TestOrg/TestRepo"
    expected_replacement_content = f"Repository: TestRepo, Date: {datetime.now().strftime('%Y-%m-%d')}"
    expected_output_path = "/base/output/TestOrg/TestRepo/_index.md"

    mock_get_output_directory = mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value="/base/output",
    )
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.makedirs")

    # Act
    living_documentation_generator._generate_sub_level_index_page(index_template, level, repository_id)

    # Assert
    mock_get_output_directory.assert_called_once()
    mock_open.assert_called_once_with(expected_output_path, "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(expected_replacement_content)


# _generate_markdown_line


def test_generate_markdown_line_with_project_state_mining_enabled_linked_to_project_true_symbol(
    mocker, consolidated_issue, project_status
):
    # Arrange
    consolidated_issue.linked_to_project = True
    consolidated_issue.project_issue_statuses = [project_status, project_status]
    expected_md_issue_line = (
        "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🟢 | In Progress, In Progress |"
        "<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    )

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=True,
    )

    # Act
    actual = LivingDocumentationGenerator._generate_markdown_line(consolidated_issue)

    # Assert
    assert expected_md_issue_line == actual


def test_generate_markdown_line_with_project_state_mining_enabled_linked_to_project_false_symbol(
    mocker, consolidated_issue, project_status
):
    # Arrange
    consolidated_issue.project_issue_statuses = [project_status]
    expected_md_issue_line = (
        "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | 🔴 | In Progress |"
        "<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    )

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=True,
    )

    # Act
    actual = LivingDocumentationGenerator._generate_markdown_line(consolidated_issue)

    # Assert
    assert expected_md_issue_line == actual


def test_generate_markdown_line_with_project_state_mining_disabled(mocker, consolidated_issue, project_status):
    # Arrange
    consolidated_issue.project_issue_statuses = [project_status]
    expected_md_issue_line = (
        "| TestOrg | TestRepo | [#42 - Sample Issue](features#sample-issue) | OPEN |"
        "<a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a> |\n"
    )

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=False,
    )

    # Act
    actual = LivingDocumentationGenerator._generate_markdown_line(consolidated_issue)

    # Assert
    assert expected_md_issue_line == actual


# _generate_issue_summary_table


def test_generate_issue_summary_table_without_project_state_mining(
    mocker, living_documentation_generator, consolidated_issue
):
    # Arrange
    expected_issue_info = (
        "| Attribute | Content |\n"
        "|---|---|\n"
        "| Organization name | TestOrg |\n"
        "| Repository name | TestRepo |\n"
        "| Issue number | 42 |\n"
        "| Title | Sample Issue |\n"
        "| State | open |\n"
        "| Issue URL | <a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a>  |\n"
        "| Created at | 2024-01-01T00:00:00Z |\n"
        "| Updated at | 2024-01-02T00:00:00Z |\n"
        "| Closed at | None |\n"
        "| Labels | bug, urgent |\n"
    )

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=False,
    )

    actual = living_documentation_generator._generate_issue_summary_table(consolidated_issue)

    assert expected_issue_info == actual


def test_generate_issue_summary_table_with_project_state_mining_and_multiple_project_statuses(
    mocker, consolidated_issue, project_status
):
    # Arrange
    consolidated_issue.linked_to_project = True
    consolidated_issue.project_issue_statuses = [project_status, project_status]
    expected_issue_info = (
        "| Attribute | Content |\n"
        "|---|---|\n"
        "| Organization name | TestOrg |\n"
        "| Repository name | TestRepo |\n"
        "| Issue number | 42 |\n"
        "| Title | Sample Issue |\n"
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

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=True,
    )

    # Act
    actual = LivingDocumentationGenerator._generate_issue_summary_table(consolidated_issue)

    # Assert
    assert expected_issue_info == actual


def test_generate_issue_summary_table_with_project_state_mining_but_no_linked_project(
    mocker, consolidated_issue, project_status
):
    # Arrange
    consolidated_issue.linked_to_project = False
    expected_issue_info = (
        "| Attribute | Content |\n"
        "|---|---|\n"
        "| Organization name | TestOrg |\n"
        "| Repository name | TestRepo |\n"
        "| Issue number | 42 |\n"
        "| Title | Sample Issue |\n"
        "| State | open |\n"
        "| Issue URL | <a href='https://github.com/TestOrg/TestRepo/issues/42' target='_blank'>GitHub link</a>  |\n"
        "| Created at | 2024-01-01T00:00:00Z |\n"
        "| Updated at | 2024-01-02T00:00:00Z |\n"
        "| Closed at | None |\n"
        "| Labels | bug, urgent |\n"
        "| Linked to project | 🔴 |\n"
    )

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_project_state_mining_enabled",
        return_value=True,
    )

    # Act
    actual = LivingDocumentationGenerator._generate_issue_summary_table(consolidated_issue)

    assert expected_issue_info == actual


# _generate_index_directory_path


def test_generate_index_directory_path_with_structured_output_grouped_by_topics(mocker):
    # Arrange
    repository_id = "org123/repo456"
    topic = "documentation"
    expected_path = "/base/output/org123/repo456/documentation"

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value="/base/output",
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=True,
    )
    mocker.patch("os.makedirs")

    # Act
    actual = LivingDocumentationGenerator._generate_index_directory_path(repository_id, topic)

    # Assert
    assert expected_path == actual


def test_generate_index_directory_path_with_structured_output_not_grouped_by_topics(mocker):
    # Arrange
    repository_id = "org123/repo456"
    topic = None
    expected_path = "/base/output/org123/repo456"

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value="/base/output",
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=True,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mocker.patch("os.makedirs")

    # Act
    actual = LivingDocumentationGenerator._generate_index_directory_path(repository_id, topic)

    # Assert
    assert expected_path == actual


def test_generate_index_directory_path_with_only_grouping_by_topic_no_structured_output(mocker):
    # Arrange
    repository_id = "org123/repo456"
    topic = "documentation"
    expected_path = "/base/output/documentation"

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value="/base/output",
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=False,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=True,
    )
    mocker.patch("os.makedirs")

    # Act
    actual = LivingDocumentationGenerator._generate_index_directory_path(repository_id, topic)

    assert expected_path == actual


def test_generate_index_directory_path_with_no_structured_output_and_no_grouping_by_topics(mocker):
    # Arrange
    repository_id = None
    topic = None
    expected_path = "/base/output"

    mocker.patch(
        "living_documentation_regime.living_documentation_generator.make_absolute_path",
        return_value="/base/output",
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_structured_output_enabled",
        return_value=False,
    )
    mocker.patch(
        "living_documentation_regime.living_documentation_generator.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mocker.patch("os.makedirs")

    # Act
    actual = LivingDocumentationGenerator._generate_index_directory_path(repository_id, topic)

    # Assert
    assert expected_path == actual


# _load_all_templates


def test_load_all_templates_loads_correctly(mocker):
    # Arrange
    expected_templates = (
        "Issue Page Template Content",
        "Index Page Template Content",
        "Root Level Template Content",
        "Organization Level Template Content",
        "Repository Level Template Content",
        "Data Level Template Content",
        "Report Page Template Content",
    )

    load_template_mock = mocker.patch("living_documentation_regime.living_documentation_generator.load_template")
    load_template_mock.side_effect = [
        "Issue Page Template Content",
        "Index Page Template Content",
        "Root Level Template Content",
        "Organization Level Template Content",
        "Repository Level Template Content",
        "Data Level Template Content",
        "Report Page Template Content",
    ]

    # Act
    actual = LivingDocumentationGenerator._load_all_templates()

    assert actual == expected_templates
    assert load_template_mock.call_count == 7

def test_load_all_templates_loads_just_some_templates(mocker):
    # Arrange
    expected_templates = (
        None,
        None,
        None,
        None,
        None,
        "Data Level Template Content",
        None,
    )

    load_template_mock = mocker.patch("living_documentation_regime.living_documentation_generator.load_template")
    load_template_mock.side_effect = [
        None,
        None,
        None,
        None,
        None,
        "Data Level Template Content",
        None,
    ]

    # Act
    actual = LivingDocumentationGenerator._load_all_templates()

    # Assert
    assert actual == expected_templates
    assert load_template_mock.call_count == 7
