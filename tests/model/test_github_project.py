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

from github.Repository import Repository
from living_documentation_generator.model.github_project import GithubProject


# loads


def test_loads_with_valid_input_loads_correctly(mocker):
    github_project = GithubProject()
    project_json = {
        "id": "123",
        "number": 1,
        "title": "Test Project"
    }
    repository = mocker.Mock(spec=Repository)
    repository.owner.login = "organizationABC"
    repository.full_name = "organizationABC/repoABC"
    field_option_response = {
        "repository": {
            "projectV2": {
                "fields": {
                    "nodes": [
                        {
                            "name": "field",
                            "options": [{"name": "option1"}, {"name": "option2"}]
                        }
                    ]
                }
            }
        }
    }

    actual = github_project.loads(project_json, repository, field_option_response)

    assert actual.id == project_json["id"]
    assert actual.number == project_json["number"]
    assert actual.title == project_json["title"]
    assert actual.organization_name == repository.owner.login
    assert actual.field_options == {"field": ["option1", "option2"]}


def test_loads_with_missing_key(mocker):
    github_project = GithubProject()
    mock_log_error = mocker.patch("living_documentation_generator.model.github_project.logger.error")
    project_json = {
        "id": "123",
        "title": "Test Project",
        "unexpected_key": "unexpected_value"
    }
    repository = mocker.Mock(spec=Repository)
    repository.owner.login = "organizationABC"
    repository.full_name = "organizationABC/repoABC"
    field_option_response = {
        "repository": {
            "projectV2": {
                "fields": {
                    "nodes": [
                        {
                            "name": "field1",
                            "options": [{"name": "option1"}, {"name": "option2"}]
                        }
                    ]
                }
            }
        }
    }

    github_project.loads(project_json, repository, field_option_response)

    mock_log_error.assert_called_once_with(
        'There is no expected response structure for the project json: %s', 'organizationABC/repoABC', exc_info=True)


# _update_field_options


def test_update_field_options_with_valid_input():
    github_project = GithubProject()
    field_option_response = {
        "repository": {
            "projectV2": {
                "fields": {
                    "nodes": [
                        {
                            "name": "field1",
                            "options": [{"name": "option1"}, {"name": "option2"}]
                        },
                        {
                            "wrong_name": "field2",
                            "wrong_options": [{"name": "option3"}, {"name": "option4"}]
                        }
                    ]
                }
            }
        }
    }

    github_project._update_field_options(field_option_response)

    assert github_project.field_options == {"field1": ["option1", "option2"]}


def test_update_field_options_with_no_expected_response_structure(mocker):
    github_project = GithubProject()
    mock_log_error = mocker.patch("living_documentation_generator.model.github_project.logger.error")
    field_option_response = {
        "unexpected_structure": {
            "unexpected_key": "unexpected_value"
        }
    }

    github_project._update_field_options(field_option_response)

    assert github_project.field_options == {}
    mock_log_error.assert_called_once_with(
        "There is no expected response structure for field options fetched from project: %s",
        github_project.title,
        exc_info=True,
    )

