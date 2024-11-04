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

from living_documentation_generator.model.config_repository import ConfigRepository


def test_load_from_json_with_valid_input_loads_correctly():
    config_repository = ConfigRepository()
    organization_name = "organizationABC"
    repository_name = "repositoryABC"
    topics = ["DocumentedUserStory", "DocumentedFeature"]
    projects_title_filter = ["project1"]
    other_value = "other-value"
    repository_json = {
        "organization-name": organization_name,
        "repository-name": repository_name,
        "topics": topics,
        "projects-title-filter": projects_title_filter,
        "other-field": other_value,
    }

    actual = config_repository.load_from_json(repository_json)

    assert actual
    assert organization_name == config_repository.organization_name
    assert repository_name == config_repository.repository_name
    assert topics == config_repository.topics
    assert projects_title_filter == config_repository.projects_title_filter


def test_load_from_json_with_missing_key_logs_error(mocker):
    config_repository = ConfigRepository()
    mock_log_error = mocker.patch("living_documentation_generator.model.config_repository.logger.error")
    repository_json = {"non-existent-key": "value"}

    actual = config_repository.load_from_json(repository_json)

    assert actual is False
    mock_log_error.assert_called_once_with(
        "The key is not found in the repository JSON input: %s.", mocker.ANY, exc_info=True
    )


def test_load_from_json_with_wrong_structure_input_logs_error(mocker):
    config_repository = ConfigRepository()
    mock_log_error = mocker.patch("living_documentation_generator.model.config_repository.logger.error")
    repository_json = "not a dictionary"

    actual = config_repository.load_from_json(repository_json)

    assert actual is False
    mock_log_error.assert_called_once_with(
        "The repository JSON input does not have a dictionary structure: %s.", mocker.ANY, exc_info=True
    )
