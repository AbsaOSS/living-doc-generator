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
import json
import os

from living_documentation_regime.action_inputs import ActionInputs
from living_documentation_regime.model.config_repository import ConfigRepository


# Check Action Inputs default values


def test_project_state_mining_default():
    # Arrange
    os.environ.pop("INPUT_PROJECT_STATE_MINING", None)

    # Act
    actual = ActionInputs.get_is_project_state_mining_enabled()

    # Assert
    assert not actual


def test_verbose_logging_default():
    # Act
    actual = os.getenv("INPUT_VERBOSE_LOGGING", "false").lower() == "true"

    # Assert
    assert not actual


def test_structured_output_default():
    # Arrange
    os.environ.pop("INPUT_STRUCTURED_OUTPUT", None)

    # Act
    actual = ActionInputs.get_is_structured_output_enabled()

    # Assert
    assert not actual


def test_group_output_by_topics_default():
    # Arrange
    os.environ.pop("INPUT_GROUP_OUTPUT_BY_TOPICS", None)

    # Act
    actual = ActionInputs.get_is_grouping_by_topics_enabled()

    # Assert
    assert not actual


# get_repositories


def test_get_repositories_correct_behaviour(mocker):
    # Arrange
    repositories_json = [
        {
            "organization-name": "organizationABC",
            "repository-name": "repositoryABC",
            "query-labels": ["feature"],
            "projects-title-filter": [],
        },
        {
            "organization-name": "organizationXYZ",
            "repository-name": "repositoryXYZ",
            "query-labels": ["bug"],
            "projects-title-filter": ["wanted_project"],
        },
    ]
    mocker.patch(
        "living_documentation_regime.action_inputs.get_action_input", return_value=json.dumps(repositories_json)
    )

    # Act
    actual = ActionInputs.get_repositories()

    # Assert
    assert 2 == len(actual)
    assert isinstance(actual[0], ConfigRepository)
    assert "organizationABC" == actual[0].organization_name
    assert "repositoryABC" == actual[0].repository_name
    assert ["feature"] == actual[0].query_labels
    assert [] == actual[0].projects_title_filter
    assert isinstance(actual[1], ConfigRepository)
    assert "organizationXYZ" == actual[1].organization_name
    assert "repositoryXYZ" == actual[1].repository_name
    assert ["bug"] == actual[1].query_labels
    assert ["wanted_project"] == actual[1].projects_title_filter


def test_get_repositories_default_value_as_json(mocker):
    # Arrange
    mock_log_error = mocker.patch("living_documentation_regime.action_inputs.logger.error")
    mocker.patch("living_documentation_regime.action_inputs.get_action_input", return_value="[]")
    mock_exit = mocker.patch("sys.exit")

    # Act
    actual = ActionInputs.get_repositories()

    # Assert
    assert [] == actual
    mock_exit.assert_not_called()
    mock_log_error.assert_not_called()


def test_get_repositories_empty_object_as_input(mocker):
    # Arrange
    mock_log_error = mocker.patch("living_documentation_regime.action_inputs.logger.error")
    mocker.patch("living_documentation_regime.action_inputs.get_action_input", return_value="{}")
    mock_exit = mocker.patch("sys.exit")

    # Act
    actual = ActionInputs.get_repositories()

    # Assert
    assert [] == actual
    mock_exit.assert_not_called()
    mock_log_error.assert_not_called()


def test_get_repositories_error_with_loading_repository_json(mocker):
    # Arrange
    mock_log_error = mocker.patch("living_documentation_regime.action_inputs.logger.error")
    mocker.patch("living_documentation_regime.action_inputs.get_action_input", return_value="[{}]")
    mocker.patch.object(ConfigRepository, "load_from_json", return_value=False)
    mock_exit = mocker.patch("sys.exit")

    # Act
    ActionInputs.get_repositories()

    # Assert
    mock_exit.assert_not_called()
    mock_log_error.assert_called_once_with("Failed to load repository from JSON: %s.", {})


def test_get_repositories_number_instead_of_json(mocker):
    # Arrange
    mock_log_error = mocker.patch("living_documentation_regime.action_inputs.logger.error")
    mocker.patch("living_documentation_regime.action_inputs.get_action_input", return_value=1)
    mock_exit = mocker.patch("sys.exit")

    # Act
    ActionInputs.get_repositories()

    # Assert
    mock_exit.assert_called_once_with(1)
    mock_log_error.assert_called_once_with("Type error parsing input JSON repositories: %s.", mocker.ANY)


def test_get_repositories_empty_string_as_input(mocker):
    # Arrange
    mock_log_error = mocker.patch("living_documentation_regime.action_inputs.logger.error")
    mocker.patch("living_documentation_regime.action_inputs.get_action_input", return_value="")
    mock_exit = mocker.patch("sys.exit")

    # Act
    actual = ActionInputs.get_repositories()

    # Assert
    assert [] == actual
    mock_exit.assert_called_once()
    mock_log_error.assert_called_once_with("Error parsing JSON repositories: %s.", mocker.ANY, exc_info=True)


def test_get_repositories_invalid_string_as_input(mocker):
    # Arrange
    mock_log_error = mocker.patch("living_documentation_regime.action_inputs.logger.error")
    mocker.patch("living_documentation_regime.action_inputs.get_action_input", return_value="not a JSON string")
    mock_exit = mocker.patch("sys.exit")

    # Act
    actual = ActionInputs.get_repositories()

    # Assert
    assert [] == actual
    mock_log_error.assert_called_once_with("Error parsing JSON repositories: %s.", mocker.ANY, exc_info=True)
    mock_exit.assert_called_once_with(1)


# validate_inputs


def test_validate_inputs_correct_behaviour(mocker):
    # Arrange
    repositories_json = [
        {
            "organization-name": "organizationABC",
            "repository-name": "repositoryABC",
            "query-labels": ["feature"],
            "projects-title-filter": [],
        }
    ]
    mock_log_debug = mocker.patch("living_documentation_regime.action_inputs.logger.debug")
    mock_log_error = mocker.patch("living_documentation_regime.action_inputs.logger.error")

    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_repositories", return_value=repositories_json
    )
    mock_exit = mocker.patch("sys.exit")

    # Act
    ActionInputs().validate_inputs()

    # Assert
    mock_exit.assert_not_called()
    mock_log_debug.assert_called_once_with("Action inputs validation successfully completed.")
    mock_log_error.assert_not_called()