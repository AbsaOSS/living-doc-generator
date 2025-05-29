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

import pytest

from action_inputs import ActionInputs
from living_doc_generator.model.config_repository import ConfigRepository
from utils.exceptions import FetchRepositoriesException


# Check Action Inputs default values


def test_project_state_mining_default():
    # Arrange
    os.environ.pop("INPUT_PROJECT_STATE_MINING", None)

    # Act
    actual = ActionInputs.is_project_state_mining_enabled()

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
    actual = ActionInputs.is_structured_output_enabled()

    # Assert
    assert not actual


# get_repositories


def test_get_repositories_correct_behaviour(mocker):
    # Arrange
    repositories_json = [
        {
            "organization-name": "organizationABC",
            "repository-name": "repositoryABC",
            "projects-title-filter": [],
        },
        {
            "organization-name": "organizationXYZ",
            "repository-name": "repositoryXYZ",
            "projects-title-filter": ["wanted_project"],
        },
    ]
    mocker.patch(
        "action_inputs.get_action_input", return_value=json.dumps(repositories_json)
    )

    # Act
    actual = ActionInputs.get_repositories()

    # Assert
    assert 2 == len(actual)
    assert isinstance(actual[0], ConfigRepository)
    assert "organizationABC" == actual[0].organization_name
    assert "repositoryABC" == actual[0].repository_name
    assert [] == actual[0].projects_title_filter
    assert isinstance(actual[1], ConfigRepository)
    assert "organizationXYZ" == actual[1].organization_name
    assert "repositoryXYZ" == actual[1].repository_name
    assert ["wanted_project"] == actual[1].projects_title_filter


def test_get_repositories_default_value_as_json(mocker):
    # Arrange
    mock_log_error = mocker.patch("action_inputs.logger.error")
    mocker.patch("action_inputs.get_action_input", return_value="[]")

    # Act
    actual = ActionInputs.get_repositories()

    # Assert
    assert [] == actual
    mock_log_error.assert_not_called()


def test_get_repositories_empty_object_as_input(mocker):
    # Arrange
    mock_log_error = mocker.patch("action_inputs.logger.error")
    mocker.patch("action_inputs.get_action_input", return_value="{}")

    # Act
    actual = ActionInputs.get_repositories()

    # Assert
    assert [] == actual
    mock_log_error.assert_not_called()


def test_get_repositories_error_with_loading_repository_json(mocker):
    # Arrange
    mock_log_error = mocker.patch("action_inputs.logger.error")
    mocker.patch("action_inputs.get_action_input", return_value="[{}]")
    mocker.patch.object(ConfigRepository, "load_from_json", return_value=False)

    # Act
    ActionInputs.get_repositories()

    # Assert
    mock_log_error.assert_called_once_with("Failed to load repository from JSON: %s.", {})


def test_get_repositories_number_instead_of_json(mocker):
    # Arrange
    mock_log_error = mocker.patch("action_inputs.logger.error")
    mocker.patch("action_inputs.get_action_input", return_value=1)

    # Act & Assert
    with pytest.raises(FetchRepositoriesException):
        ActionInputs.get_repositories()
        mock_log_error.assert_called_once_with("Type error parsing input JSON repositories: %s.", mocker.ANY)


def test_get_repositories_empty_string_as_input(mocker):
    # Arrange
    mock_log_error = mocker.patch("action_inputs.logger.error")
    mocker.patch("action_inputs.get_action_input", return_value="")

    # Act & Assert
    with pytest.raises(FetchRepositoriesException):
        actual = ActionInputs.get_repositories()
        assert [] == actual
        mock_log_error.assert_called_once_with("Error parsing JSON repositories: %s.", mocker.ANY, exc_info=True)



def test_get_repositories_invalid_string_as_input(mocker):
    # Arrange
    mock_log_error = mocker.patch("action_inputs.logger.error")
    mocker.patch("action_inputs.get_action_input", return_value="not a JSON string")

    # Act & Assert
    with pytest.raises(FetchRepositoriesException):
        actual = ActionInputs.get_repositories()
        assert [] == actual
        mock_log_error.assert_called_once_with("Error parsing JSON repositories: %s.", mocker.ANY, exc_info=True)


# validate_repositories_configuration


def test_validate_repositories_configuration_correct_behaviour(mocker, config_repository):
    # Arrange
    mock_log_debug = mocker.patch("action_inputs.logger.debug")
    mock_log_error = mocker.patch("action_inputs.logger.error")

    mocker.patch(
        "action_inputs.ActionInputs.get_repositories", return_value=[config_repository]
    )
    mocker.patch(
        "action_inputs.ActionInputs.get_github_token", return_value="correct_token"
    )
    mocker.patch(
        "action_inputs.ActionInputs.is_living_doc_regime_enabled", return_value="true"
    )
    fake_correct_response = mocker.Mock()
    fake_correct_response.status_code = 200
    mocker.patch("action_inputs.requests.get", return_value=fake_correct_response)

    # Act
    return_value = ActionInputs().validate_user_configuration()

    # Assert
    assert return_value is True
    mock_log_debug.assert_has_calls(
        [
            mocker.call("User configuration validation started"),
            mocker.call("User configuration validation successfully completed."),
            mocker.call('Regime: `LivDoc`: %s.', 'Enabled'),
            mocker.call('Global: `report-page`: %s.', True),
            mocker.call('Regime(LivDoc): `liv-doc-repositories`: %s.', mocker.ANY),
            mocker.call('Regime(LivDoc): `liv-doc-project-state-mining`: %s.', False),
            mocker.call('Regime(LivDoc): `liv-doc-structured-output`: %s.', False),
            mocker.call('Regime(LivDoc): `liv-doc-output-formats`: %s.', ['mdoc']),
    ],
        any_order=False,
    )
    mock_log_error.assert_not_called()


def test_validate_user_configuration_wrong_repository_404(mocker, config_repository):
    # Arrange
    mock_log_error = mocker.patch("action_inputs.logger.error")

    mocker.patch(
        "action_inputs.ActionInputs.get_repositories", return_value=[config_repository]
    )
    mocker.patch("action_inputs.ActionInputs.get_github_token", return_value="fake-token")
    mock_error_response = mocker.Mock()
    mock_error_response.status_code = 404
    mocker.patch("action_inputs.requests.get", return_value=mock_error_response)

    # Act
    return_value = ActionInputs().validate_user_configuration()

    # Assert
    assert return_value is False


def test_validate_user_configuration_wrong_repository_non_200(mocker, config_repository):
    # Arrange
    mock_log_error = mocker.patch("action_inputs.logger.error")

    mocker.patch(
        "action_inputs.ActionInputs.get_repositories", return_value=[config_repository]
    )
    mocker.patch("action_inputs.ActionInputs.get_github_token", return_value="correct_token")

    mock_response_200 = mocker.Mock()
    mock_response_200.status_code = 200
    mock_response_500 = mocker.Mock()
    mock_response_500.status_code = 500
    mocker.patch("requests.get", side_effect=[mock_response_200, mock_response_500])

    # Act
    return_value = ActionInputs().validate_user_configuration()

    # Assert
    assert return_value is False
    mock_log_error.assert_called_once_with(
        "An error occurred while validating the repository '%s/%s'. The response status code is %s. Response: %s",
        "test_org",
        "test_repo",
        500,
        mock_response_500.text,
    )


def test_validate_repositories_wrong_token(mocker, config_repository):
    # Arrange
    mock_log_error = mocker.patch("action_inputs.logger.error")

    mocker.patch("action_inputs.ActionInputs.get_github_token", return_value="")

    mocker.patch(
        "action_inputs.ActionInputs.get_repositories", return_value=list()
    )

    # Act
    return_value = ActionInputs().validate_user_configuration()

    # Assert
    assert return_value is False
    mock_log_error.assert_called_once_with(
        "Can not connect to GitHub. Possible cause: Invalid GitHub token. Status code: %s, Response: %s",
         401,
        '{"message":"Bad credentials","documentation_url":"https://docs.github.com/rest","status":"401"}'
    )
