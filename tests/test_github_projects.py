#
# Copyright 2024 ABSA Group Limited
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
import requests

from living_documentation_generator.github_projects import GithubProjects


# _send_graphql_query


def test_send_graphql_query_correct_behaviour(mocker):
    expected_data = {"repository": {"projectsV2": {"nodes": [{"id": "PVT_k", "number": 3, "title": "Board"}]}}}
    expected_response = {"data": expected_data}

    mock_session = mocker.Mock()
    mock_session.post.return_value.json.return_value = expected_response
    mock_session.post.return_value.raise_for_status = lambda: None

    mocker.patch.object(
        GithubProjects,
        "_GithubProjects__initialize_request_session",
        lambda self: setattr(self, "_GithubProjects__session", mock_session),
    )

    actual_data = GithubProjects("token123")._send_graphql_query("query")

    assert expected_data == actual_data


def test_send_graphql_query_http_error(mocker):
    mock_session = mocker.Mock()
    mocker.patch.object(
        GithubProjects,
        "_GithubProjects__initialize_request_session",
        lambda self: setattr(self, "_GithubProjects__session", mock_session),
    )
    mock_log_error = mocker.patch("living_documentation_generator.github_projects.logger.error")
    mock_session.post.side_effect = requests.HTTPError("HTTP error occurred")

    actual = GithubProjects("token123")._send_graphql_query("query")

    assert actual is None
    mock_log_error.assert_called_once_with("HTTP error occurred: %s.", mocker.ANY, exc_info=True)


def test_send_graphql_query_request_exception(mocker):
    mock_session = mocker.Mock()
    mocker.patch.object(
        GithubProjects,
        "_GithubProjects__initialize_request_session",
        lambda self: setattr(self, "_GithubProjects__session", mock_session),
    )
    mock_log_error = mocker.patch("living_documentation_generator.github_projects.logger.error")
    mock_session.post.side_effect = requests.RequestException("An error occurred.")

    actual = GithubProjects("token123")._send_graphql_query("query")

    assert actual is None
    mock_log_error.assert_called_once_with("An error occurred: %s.", mocker.ANY, exc_info=True)


# get_repository_projects


def test_get_repository_projects_correct_behaviour(mocker, repository_setup):
    # Arrange
    mock_repository = repository_setup()
    projects_title_filter = ["Project A"]
    mock_logger_debug = mocker.patch("living_documentation_generator.github_projects.logger.debug")

    mocker.patch(
        "living_documentation_generator.github_projects.get_projects_from_repo_query",
        return_value="mocked_projects_query",
    )
    mocker.patch(
        "living_documentation_generator.github_projects.get_project_field_options_query",
        return_value="mocked_project_field_options_query",
    )
    mock_send_query = mocker.patch.object(GithubProjects, "_send_graphql_query")
    mock_send_query.side_effect = [
        {
            "repository": {
                "projectsV2": {"nodes": [{"title": "Project A", "number": 1}, {"title": "Project B", "number": 2}]}
            }
        },
        {"data": {}},
    ]

    mock_github_project = mocker.patch("living_documentation_generator.github_projects.GithubProject")
    mock_github_project_instance = mock_github_project.return_value
    mock_github_project_instance.loads.return_value = mock_github_project_instance

    # Act
    github_projects_instance = GithubProjects("token123")
    actual = github_projects_instance.get_repository_projects(mock_repository, projects_title_filter)

    # Assert
    assert 1 == len(actual)
    assert mock_github_project_instance in actual
    mock_send_query.assert_called()
    mock_github_project_instance.loads.assert_called_once_with(
        {"title": "Project A", "number": 1}, mock_repository, {"data": {}}
    )
    mock_logger_debug.assert_called_once_with("Project `%s` is not required based on the filter.", "Project B")


def test_get_repository_projects_response_none(mocker, repository_setup):
    # Arrange
    mock_repository = repository_setup()
    mock_logger_warning = mocker.patch("living_documentation_generator.github_projects.logger.warning")

    mocker.patch(
        "living_documentation_generator.github_projects.get_projects_from_repo_query",
        return_value="mocked_projects_query",
    )
    mocker.patch(
        "living_documentation_generator.github_projects.get_project_field_options_query",
        return_value="mocked_project_field_options_query",
    )
    mock_send_query = mocker.patch.object(GithubProjects, "_send_graphql_query", return_value=None)

    # Act
    github_projects_instance = GithubProjects("mock_token")
    actual = github_projects_instance.get_repository_projects(mock_repository, [])

    # Assert
    assert [] == actual
    mock_send_query.assert_called_once_with("mocked_projects_query")
    mock_logger_warning.assert_called_once_with(
        "Fetching GitHub project data - no project data for repository %s. No data received.", mock_repository.full_name
    )


def test_get_repository_projects_response_nodes_none(mocker, repository_setup):
    # Arrange
    mock_repository = repository_setup()
    mock_logger_warning = mocker.patch("living_documentation_generator.github_projects.logger.warning")

    mocker.patch(
        "living_documentation_generator.github_projects.get_projects_from_repo_query",
        return_value="mocked_projects_query",
    )
    mocker.patch(
        "living_documentation_generator.github_projects.get_project_field_options_query",
        return_value="mocked_project_field_options_query",
    )
    mock_send_query = mocker.patch.object(
        GithubProjects, "_send_graphql_query", return_value={"repository": {"projectsV2": {"nodes": None}}}
    )

    # Act
    github_projects_instance = GithubProjects("mock_token")
    actual = github_projects_instance.get_repository_projects(mock_repository, [])

    # Assert
    assert actual == []
    mock_send_query.assert_called_once_with("mocked_projects_query")
    mock_logger_warning.assert_called_once_with("Repository information is not present in the response")


# get_project_issues


def test_get_project_issues_correct_behaviour(mocker, github_project_setup):
    mock_project = github_project_setup()
    mock_logger_debug = mocker.patch("living_documentation_generator.github_projects.logger.debug")

    mocker.patch(
        "living_documentation_generator.github_projects.get_issues_from_project_query",
        return_value="mocked_issues_query",
    )

    mock_send_query = mocker.patch.object(GithubProjects, "_send_graphql_query")
    mock_send_query.side_effect = [
        {
            "node": {
                "items": {
                    "nodes": [{"id": "issue_1", "title": "Issue 1"}, {"id": "issue_2", "title": "Issue 2"}],
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor_1"},
                }
            }
        },
        {
            "node": {
                "items": {
                    "nodes": [{"id": "issue_3", "title": "Issue 3"}, {"id": "issue_4", "title": "Issue 4"}],
                    "pageInfo": {"hasNextPage": False, "endCursor": "cursor_2"},
                }
            }
        },
    ]

    mock_project_issue = mocker.patch("living_documentation_generator.github_projects.ProjectIssue")
    mock_project_issue_instance = mock_project_issue.return_value
    mock_project_issue_instance.loads.side_effect = lambda issue_data, proj: issue_data if issue_data else None

    # Act
    github_projects_instance = GithubProjects("token123")
    actual = github_projects_instance.get_project_issues(mock_project)

    # Assert
    assert 4 == len(actual)
    assert actual == [
        {"id": "issue_1", "title": "Issue 1"},
        {"id": "issue_2", "title": "Issue 2"},
        {"id": "issue_3", "title": "Issue 3"},
        {"id": "issue_4", "title": "Issue 4"},
    ]
    mock_send_query.assert_called()
    mock_project_issue_instance.loads.assert_any_call({"id": "issue_1", "title": "Issue 1"}, mock_project)
    mock_project_issue_instance.loads.assert_any_call({"id": "issue_4", "title": "Issue 4"}, mock_project)
    mock_logger_debug.assert_any_call("Received `%i` issue(s) records from project: %s.", 2, mock_project.title)
    mock_logger_debug.assert_any_call("Loaded `%i` issue(s) from project: %s.", 4, mock_project.title)


def test_get_project_issues_no_response(mocker, github_project_setup):
    # Arrange
    mock_project = github_project_setup()

    mocker.patch(
        "living_documentation_generator.github_projects.get_issues_from_project_query",
        return_value="mocked_issues_query",
    )
    mock_send_query = mocker.patch.object(GithubProjects, "_send_graphql_query", return_value=None)

    # Act
    github_projects_instance = GithubProjects("mock_token")
    result = github_projects_instance.get_project_issues(mock_project)

    # Assert
    assert result == []
    mock_send_query.assert_called_once_with("mocked_issues_query")
