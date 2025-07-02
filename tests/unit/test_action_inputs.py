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
import os

from action_inputs import ActionInputs


# Check Action Inputs default values


def test_report_page_default():
    # Act
    actual = ActionInputs.is_report_page_generation_enabled()

    # Assert
    assert not actual


def test_get_source_returns_env_value(monkeypatch):
    # Arrange
    monkeypatch.setenv("INPUT_SOURCE", "my_source.json")
    # Act
    result = ActionInputs.get_source()
    # Assert
    assert result == "my_source.json"

def test_get_source_returns_empty_when_not_set(monkeypatch):
    # Arrange
    monkeypatch.delenv("INPUT_SOURCE", raising=False)
    # Act
    result = ActionInputs.get_source()
    # Assert
    assert result == ""


def test_structured_output_default():
    # Arrange
    os.environ.pop("INPUT_STRUCTURED_OUTPUT", None)

    # Act
    actual = ActionInputs.is_structured_output_enabled()

    # Assert
    assert not actual


# _validate


def test_validate_source_found(mocker, tmp_path):
    # Arrange
    mock_log_debug = mocker.patch("action_inputs.logger.debug")
    mock_log_error = mocker.patch("action_inputs.logger.error")
    mock_log_info = mocker.patch("action_inputs.logger.info")

    # Create a temporary file to act as the source
    source_file = tmp_path / "source.json"
    source_file.write_text("{}")

    mocker.patch("action_inputs.ActionInputs.get_source", return_value=str(source_file))
    mocker.patch("os.path.isfile", return_value=True)

    # Act
    return_value = ActionInputs().validate_user_configuration()

    # Assert
    assert return_value is True
    mock_log_debug.assert_not_called()
    mock_log_error.assert_not_called()
    mock_log_info.assert_any_call("User configuration validation successfully completed.")


def test_validate_source_not_string(mocker):
    # Arrange
    mock_log_debug = mocker.patch("action_inputs.logger.debug")
    mock_log_error = mocker.patch("action_inputs.logger.error")

    mocker.patch(
        "action_inputs.ActionInputs.get_source", return_value=1
    )

    # Act
    return_value = ActionInputs().validate_user_configuration()

    # Assert
    assert return_value is False
    mock_log_error.assert_has_calls(
        [
            mocker.call("Source input must be a non-empty string."),
            mocker.call("User configuration validation failed."),
    ],
        any_order=False,
    )
    mock_log_debug.assert_not_called()


def test_validate_source_not_found(mocker):
    # Arrange
    mock_log_debug = mocker.patch("action_inputs.logger.debug")
    mock_log_error = mocker.patch("action_inputs.logger.error")

    mocker.patch(
        "action_inputs.ActionInputs.get_source", return_value="/non/existing/path/to/file.json"
    )

    # Act
    return_value = ActionInputs().validate_user_configuration()

    # Assert
    assert return_value is False
    mock_log_error.assert_has_calls(
        [
            mocker.call("Source file not found at received path: '%s'.", "/non/existing/path/to/file.json"),
            mocker.call("User configuration validation failed."),
        ],
        any_order=False,
    )
    mock_log_debug.assert_not_called()
