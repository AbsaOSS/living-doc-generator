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
from living_documentation_generator.model.github_project import GithubProject
from living_documentation_generator.model.project_issue import ProjectIssue


# loads


def test_loads_with_valid_input():
    project_issue = ProjectIssue()
    issue_json = {
        "content": {"number": 1, "repository": {"owner": {"login": "organizationABC"}, "name": "repoABC"}},
        "fieldValues": {
            "nodes": [
                {"__typename": "ProjectV2ItemFieldSingleSelectValue", "name": "Status1"},
                {"__typename": "ProjectV2ItemFieldSingleSelectValue", "name": "Priority1"},
                {"__typename": "ProjectV2ItemFieldSingleSelectValue", "name": "Size1"},
                {"__typename": "ProjectV2ItemFieldSingleSelectValue", "name": "MoSCoW1"},
            ]
        },
    }
    project = GithubProject()
    project.title = "Test Project"
    project.field_options = {
        "Status": ["Status1", "Status2"],
        "Priority": ["Priority1", "Priority2"],
        "Size": ["Size1", "Size2"],
        "MoSCoW": ["MoSCoW1", "MoSCoW2"],
    }

    actual = project_issue.loads(issue_json, project)

    assert actual is not None
    assert actual.number == issue_json["content"]["number"]
    assert actual.organization_name == issue_json["content"]["repository"]["owner"]["login"]
    assert actual.repository_name == issue_json["content"]["repository"]["name"]
    assert actual.project_status.project_title == project.title
    assert actual.project_status.status == "Status1"
    assert actual.project_status.priority == "Priority1"
    assert actual.project_status.size == "Size1"
    assert actual.project_status.moscow == "MoSCoW1"


def test_loads_without_content_key_logs_debug(mocker):
    project_issue = ProjectIssue()
    mock_log = mocker.patch("living_documentation_generator.model.project_issue.logger")
    issue_json = {}
    project = GithubProject()

    actual = project_issue.loads(issue_json, project)

    assert actual is None
    mock_log.debug.assert_called_once_with("No issue data provided in received json: %s.", {})


def test_loads_with_incorrect_json_structure_for_repository_name(mocker):
    project_issue = ProjectIssue()
    mock_log = mocker.patch("living_documentation_generator.model.project_issue.logger")
    incorrect_json = {"content": {"number": 1}}
    project = GithubProject()

    actual = project_issue.loads(incorrect_json, project)

    assert actual.number == 1
    assert actual.organization_name == ""
    assert actual.repository_name == ""
    mock_log.debug.assert_called_once_with("KeyError occurred while parsing issue json: %s.", incorrect_json)
