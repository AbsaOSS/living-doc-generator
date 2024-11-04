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

from living_documentation_generator.action_inputs import ActionInputs
from living_documentation_generator.model.config_repository import ConfigRepository


# get_repositories


def test_get_repositories_correct_behaviour(mocker):
    repositories_json = [
        {
            "organization-name": "organizationABC",
            "repository-name": "repositoryABC",
            "topics": ["DocumentedFeature"],
            "projects-title-filter": [],
        },
        {
            "organization-name": "organizationXYZ",
            "repository-name": "repositoryXYZ",
            "topics": ["DocumentedUserStory"],
            "projects-title-filter": ["wanted_project"],
        },
    ]
    mocker.patch(
        "living_documentation_generator.action_inputs.get_action_input", return_value=json.dumps(repositories_json)
    )

    actual = ActionInputs.get_repositories()

    assert 2 == len(actual)
    assert isinstance(actual[0], ConfigRepository)
    assert "organizationABC" == actual[0].organization_name
    assert "repositoryABC" == actual[0].repository_name
    assert ["DocumentedFeature"] == actual[0].topics
    assert [] == actual[0].projects_title_filter
    assert isinstance(actual[1], ConfigRepository)
    assert "organizationXYZ" == actual[1].organization_name
    assert "repositoryXYZ" == actual[1].repository_name
    assert ["DocumentedUserStory"] == actual[1].topics
    assert ["wanted_project"] == actual[1].projects_title_filter


# FixMe: For some reason this test is called 11 times. Please help me to understand the reason.
# def test_get_repositories_error_parsing_json_from_json_string(mocker):
#     mock_log_error = mocker.patch("living_documentation_generator.action_inputs.logger.error")
#     mocker.patch("living_documentation_generator.action_inputs.get_action_input", return_value="not a JSON string")
#     mock_exit = mocker.patch("sys.exit")
#
#     ActionInputs.get_repositories()
#
#     mock_log_error.assert_called_once_with("Error parsing input JSON repositories: `%s.`", mocker.ANY, exc_info=True)
#     mock_exit.assert_called_once_with(1)


def test_get_repositories_default_value_as_json(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.action_inputs.logger.error")
    mocker.patch("living_documentation_generator.action_inputs.get_action_input", return_value="[]")
    mock_exit = mocker.patch("sys.exit")

    actual = ActionInputs.get_repositories()

    assert actual == []
    mock_exit.assert_not_called()
    mock_log_error.assert_not_called()


def test_get_repositories_empty_object_as_input(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.action_inputs.logger.error")
    mocker.patch("living_documentation_generator.action_inputs.get_action_input", return_value="{}")
    mock_exit = mocker.patch("sys.exit")

    actual = ActionInputs.get_repositories()

    assert actual == []
    mock_exit.assert_not_called()
    mock_log_error.assert_not_called()


def test_get_repositories_error_with_loading_repository_json(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.action_inputs.logger.error")
    mocker.patch("living_documentation_generator.action_inputs.get_action_input", return_value="[{}]")
    mocker.patch.object(ConfigRepository, "load_from_json", return_value=False)
    mock_exit = mocker.patch("sys.exit")

    ActionInputs.get_repositories()

    mock_exit.assert_not_called()
    mock_log_error.assert_called_once_with("Failed to load repository from JSON: %s.", {})


def test_get_repositories_number_instead_of_json(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.action_inputs.logger.error")
    mocker.patch("living_documentation_generator.action_inputs.get_action_input", return_value=1)
    mock_exit = mocker.patch("sys.exit")

    ActionInputs.get_repositories()

    mock_exit.assert_called_once_with(1)
    mock_log_error.assert_called_once_with("Type error parsing input JSON repositories: `%s.`", mocker.ANY)


def test_get_repositories_empty_string_as_input(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.action_inputs.logger.error")
    mocker.patch("living_documentation_generator.action_inputs.get_action_input", return_value="")
    mock_exit = mocker.patch("sys.exit")

    actual = ActionInputs.get_repositories()

    assert actual == []
    mock_exit.assert_called_once()
    mock_log_error.assert_called_once_with("Error parsing JSON repositories: %s.", mocker.ANY, exc_info=True)


def test_get_repositories_invalid_string_as_input(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.action_inputs.logger.error")
    mocker.patch("living_documentation_generator.action_inputs.get_action_input", return_value="string")
    mock_exit = mocker.patch("sys.exit")

    actual = ActionInputs.get_repositories()

    assert actual == []
    mock_exit.assert_called_once()
    mock_log_error.assert_called_once_with("Error parsing JSON repositories: %s.", mocker.ANY, exc_info=True)


# validate_inputs


def test_validate_inputs_correct_behaviour(mocker):
    mock_log_debug = mocker.patch("living_documentation_generator.action_inputs.logger.debug")
    mock_log_error = mocker.patch("living_documentation_generator.action_inputs.logger.error")
    repositories_json = [
        {
            "organization-name": "organizationABC",
            "repository-name": "repositoryABC",
            "query-labels": ["feature"],
            "projects-title-filter": [],
        }
    ]
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_repositories", return_value=repositories_json
    )
    mock_exit = mocker.patch("sys.exit")

    ActionInputs.validate_inputs("./output")

    mock_exit.assert_not_called()
    mock_log_debug.assert_called_once_with("Action inputs validation successfully completed.")
    mock_log_error.assert_not_called()


def test_validate_inputs_error_output_path_as_empty_string(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.action_inputs.logger.error")
    mock_exit = mocker.patch("sys.exit")

    ActionInputs.validate_inputs("")

    mock_exit.assert_called_once_with(1)
    mock_log_error.assert_called_once_with("INPUT_OUTPUT_PATH can not be an empty string.")


def test_validate_inputs_error_output_path_as_project_directory(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.action_inputs.logger.error")
    mock_exit = mocker.patch("sys.exit")

    ActionInputs.validate_inputs("./templates/template_subfolder")

    mock_exit.assert_called_once_with(1)
    mock_log_error.assert_called_once_with("INPUT_OUTPUT_PATH cannot be chosen as a part of any project folder.")


def test_validate_inputs_absolute_output_path_with_relative_project_directories(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.action_inputs.logger.error")
    mock_exit = mocker.patch("sys.exit")
    mocker.patch(
        "living_documentation_generator.action_inputs.get_all_project_directories",
        return_value=["project/dir1", "project/dir2"],
    )
    mocker.patch("os.path.abspath", side_effect=lambda path: f"/root/{path}" if not path.startswith("/") else path)
    absolute_out_path = "/root/project/dir1/subfolder"

    ActionInputs.validate_inputs(absolute_out_path)

    mock_exit.assert_called_once_with(1)
    mock_log_error.assert_called_once_with("INPUT_OUTPUT_PATH cannot be chosen as a part of any project folder.")
