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
    mock_generate_markdown_pages = mocker.patch.object(
        living_documentation_generator,
        "_generate_living_documents",
    )

    # Act
    living_documentation_generator.generate()

    # Assert
    mock_clean_output_directory.assert_called_once()
    mock_fetch_github_issues.assert_called_once()
    mock_fetch_github_project_issues.assert_called_once()
    mock_consolidate_issues_data.assert_called_once_with(
        {"test_org/test_repo": [mock_issue]}, {"test_org/test_repo#1": [project_issue_mock]}
    )
    # mock_generate_markdown_pages.assert_called_once_with({"test_org/test_repo#1": consolidated_issue_mock})
    mock_logger_debug.assert_called_once_with("Output directory cleaned.")
    mock_logger_info.assert_has_calls(
        [
            mocker.call("Fetching repository GitHub issues - started."),
            mocker.call("Fetching repository GitHub issues - finished."),
            mocker.call("Fetching GitHub project data - started."),
            mocker.call("Fetching GitHub project data - finished."),
            mocker.call("Issue and project data consolidation - started."),
            mocker.call("Issue and project data consolidation - finished."),
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


# _generate_living_documents


def test_generate_living_documents_correct_behaviour(mocker, living_documentation_generator):
    # Arrange
    consolidated_issues = {
        "test_org/test_repo#1": mocker.Mock(spec=ConsolidatedIssue),
        "test_org/test_repo#2": mocker.Mock(spec=ConsolidatedIssue),
    }
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")
    mock_logger_error = mocker.patch("living_documentation_regime.living_documentation_generator.logger.error")

    mock_exporter = mocker.Mock()
    mock_exporter.export.return_value = True
    mocker.patch("living_documentation_regime.living_documentation_generator.ExporterFactory.get_exporter", return_value=mock_exporter)

    # Act
    living_documentation_generator._generate_living_documents(consolidated_issues)

    # Assert
    assert mock_exporter.export.call_count == 1
    mock_exporter.export.assert_any_call(issues=consolidated_issues)
    mock_logger_info.assert_called_once_with("Living Documentation output generated successfully.")
    mock_logger_error.assert_not_called()


def test_generate_living_documents_exporter_fails(mocker, living_documentation_generator):
    # Arrange
    consolidated_issues = {
        "test_org/test_repo#1": mocker.Mock(spec=ConsolidatedIssue),
        "test_org/test_repo#2": mocker.Mock(spec=ConsolidatedIssue),
    }
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")
    mock_logger_error = mocker.patch("living_documentation_regime.living_documentation_generator.logger.error")

    mock_exporter = mocker.Mock()
    mock_exporter.export.return_value = False
    mocker.patch("living_documentation_regime.living_documentation_generator.ExporterFactory.get_exporter", return_value=mock_exporter)

    # Act
    living_documentation_generator._generate_living_documents(consolidated_issues)

    # Assert
    assert mock_exporter.export.call_count == 1
    mock_exporter.export.assert_any_call(issues=consolidated_issues)
    mock_logger_info.assert_not_called()
    mock_logger_error.assert_called_once_with("Living Documentation output generation failed.")


def test_generate_living_documents_no_exporter(mocker, living_documentation_generator):
    # Arrange
    consolidated_issues = {
        "test_org/test_repo#1": mocker.Mock(spec=ConsolidatedIssue),
        "test_org/test_repo#2": mocker.Mock(spec=ConsolidatedIssue),
    }
    mock_logger_info = mocker.patch("living_documentation_regime.living_documentation_generator.logger.info")
    mock_logger_error = mocker.patch("living_documentation_regime.living_documentation_generator.logger.error")

    mocker.patch("living_documentation_regime.living_documentation_generator.ActionInputs.get_liv_doc_output_formats", return_value=["non"])

    # Act
    living_documentation_generator._generate_living_documents(consolidated_issues)

    # Assert
    mock_logger_info.assert_not_called()
    mock_logger_error.assert_has_calls(
        [
            mocker.call("No generation process for this format: %s", "non"),
            mocker.call("Living Documentation output generation failed."),

        ],
        any_order=False,
    )
