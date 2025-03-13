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

from action_inputs import ActionInputs
from living_documentation_regime.model.config_repository import ConfigRepository


# Check Action Inputs default values


def test_project_state_mining_default():
    # Arrange
    os.environ.pop("INPUT_PROJECT_STATE_MINING", None)

    # Act
    actual = ActionInputs.get_is_project_state_mining_enabled()

    # Assert
    assert not actual


def test_report_page_default():
    # Act
    actual = os.getenv("INPUT_REPORT_PAGE", "true").lower() == "true"

    # Assert
    assert actual


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


# validate_repositories_configuration


def test_validate_repositories_configuration_correct_behaviour(mocker, config_repository):
    # Arrange
    mock_log_debug = mocker.patch("living_documentation_regime.action_inputs.logger.debug")
    mock_log_error = mocker.patch("living_documentation_regime.action_inputs.logger.error")

    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_repositories", return_value=[config_repository]
    )
    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_github_token", return_value="correct_token"
    )
    mock_exit = mocker.patch("sys.exit")
    fake_correct_response = mocker.Mock()
    fake_correct_response.status_code = 200
    mocker.patch("living_documentation_regime.action_inputs.requests.get", return_value=fake_correct_response)

    # Act
    ActionInputs().validate_user_configuration()

    # Assert
    mock_exit.assert_not_called()
    mock_log_debug.assert_called_once_with("Repositories configuration validation successfully completed.")
    mock_log_error.assert_not_called()


def test_validate_repositories_configuration_wrong_configuration(mocker, config_repository):
    # Arrange
    mock_log_error = mocker.patch("living_documentation_regime.action_inputs.logger.error")

    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_repositories", return_value=[config_repository]
    )
    mocker.patch("living_documentation_regime.action_inputs.ActionInputs.get_github_token", return_value="fake-token")
    mock_exit = mocker.patch("sys.exit")
    mock_error_response = mocker.Mock()
    mock_error_response.status_code = 404
    mocker.patch("living_documentation_regime.action_inputs.requests.get", return_value=mock_error_response)

    # Act
    ActionInputs().validate_repositories_configuration()

    # Assert
    assert mock_exit.call_count == 2
    mock_log_error.assert_any_call(
        "Repository '%s/%s' could not be found on GitHub. Please verify that the repository exists and that your authorization token is correct.",
        "test_org",
        "test_repo",
    )

def test_validate_repositories_wrong_token(mocker, config_repository):
    # Arrange
    mock_log_error = mocker.patch("living_documentation_regime.action_inputs.logger.error")

    mocker.patch("living_documentation_regime.action_inputs.ActionInputs.get_github_token", return_value="")
    mock_exit = mocker.patch("sys.exit")

    mocker.patch(
        "living_documentation_regime.action_inputs.ActionInputs.get_repositories", return_value=list()
    )

    # Act
    ActionInputs().validate_user_configuration()

    # Assert
    mock_exit.assert_called_once_with(1)
    mock_log_error.assert_called_once_with(
        "Can not connect to GitHub. Possible cause: Invalid GitHub token. Please verify that the token is correct.",
         401,
        '{"message":"Bad credentials","documentation_url":"https://docs.github.com/rest","status":"401"}'
    )
