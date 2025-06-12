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

from main import run


# run


def test_run_correct_behaviour(mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.validate_user_configuration", return_value=True)
    mock_generator = mocker.patch("main.MdocLivingDocumentationGenerator")
    mock_generator.return_value.generate.return_value = True
    mocker.patch("main.make_absolute_path", return_value="/unit/test/output/path")

    mock_log_info = mocker.patch("logging.getLogger").return_value.info
    mocker.patch.dict(
        os.environ,
        {
            "INPUT_GITHUB_TOKEN": "fake_token",
            "INPUT_LIV_DOC_REGIME": "true",
            "INPUT_OUTPUT_PATH": "./user/output/path",
        },
    )

    # Act
    run()

    # Assert
    mock_generator.return_value.generate.assert_called_once()
    mock_log_info.assert_has_calls(
        [
            mocker.call("Living Documentation generator - mdoc - starting."),
            mocker.call("Living Documentation generator - mdoc - root output path set to `%s`.", "/unit/test/output/path"),
            mocker.call("Living Documentation generator - mdoc - ending."),
            mocker.call("Living Documentation generator - mdoc - generation successfully completed."),
        ],
        any_order=False,
    )


def test_validate_user_configuration_failed(mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.validate_user_configuration", return_value=False)
    mocker.patch("main.make_absolute_path", return_value="/unit/test/output/path")

    mock_logger = mocker.Mock()
    mocker.patch("logging.getLogger", return_value=mock_logger)
    mock_exit = mocker.patch("sys.exit")
    mocker.patch("os.makedirs")

    # Act
    run()

    # Assert
    mock_logger.info.assert_any_call("Living Documentation generator - mdoc - starting.")
    mock_logger.error.assert_any_call("Living Documentation generator - mdoc - user configuration validation failed.")
    mock_exit.assert_called_once_with(1)


def test_generate_failed(mocker):
    # Arrange
    mocker.patch("action_inputs.ActionInputs.validate_user_configuration", return_value=True)
    mock_generator = mocker.patch("main.MdocLivingDocumentationGenerator")
    mock_generator.return_value.generate.return_value = False
    mocker.patch("main.make_absolute_path", return_value="/unit/test/output/path")

    mock_logger = mocker.Mock()
    mocker.patch("logging.getLogger", return_value=mock_logger)
    mock_exit = mocker.patch("sys.exit")
    mocker.patch("os.makedirs")

    # Act
    run()

    # Assert
    mock_logger.info.assert_any_call("Living Documentation generator - mdoc - starting.")
    mock_logger.info.assert_any_call("Living Documentation generator - mdoc - root output path set to `%s`.", "/unit/test/output/path")
    mock_logger.info.assert_any_call("Living Documentation generator - mdoc - ending.")
    mock_logger.error.assert_any_call("Living Documentation generator - mdoc - generation failed.")
    mock_exit.assert_called_once_with(1)
