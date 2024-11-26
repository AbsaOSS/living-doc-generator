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

from living_documentation_regime.action_inputs import ActionInputs
from living_documentation_regime.living_documentation_generator import LivingDocumentationGenerator
from main import run


# run


def test_run_correct_behaviour_with_all_regimes_enabled(mocker):
    # Arrange
    mock_log_info = mocker.patch("logging.getLogger").return_value.info
    mock_living_doc_generator = mocker.patch("main.LivingDocumentationGenerator")
    mocker.patch.dict(
        os.environ,
        {
            "INPUT_GITHUB_TOKEN": "fake_token",
            "INPUT_MINING_REGIMES": "LivDoc",
            "INPUT_OUTPUT_PATH": "./user/output/path",
        },
    )
    expected_output_path = os.path.abspath("./user/output/path")

    # Act
    run()

    # Assert
    mock_living_doc_generator.assert_called_once()
    mock_log_info.assert_has_calls(
        [
            mocker.call("Starting Living Documentation generation."),
            mocker.call("Living Documentation generation - Starting the `LivDoc` generation regime."),
            mocker.call("Living Documentation generation - `LivDoc` generation regime completed."),
            mocker.call("Living Documentation generation - output path set to `%s`.", expected_output_path),
            mocker.call("Living Documentation generation completed."),
        ],
        any_order=False,
    )


def test_run_with_zero_regimes_enabled(mocker):
    # Arrange
    mock_log_info = mocker.patch("logging.getLogger").return_value.info
    mocker.patch.dict(os.environ, {"INPUT_GITHUB_TOKEN": "fake_token", "INPUT_MINING_REGIMES": "Wrong name of regime"})
    mock_living_doc_generator = mocker.patch("main.LivingDocumentationGenerator")
    expected_output_path = os.path.abspath("./output")  # Adding the default value

    # Act
    run()

    # Assert
    mock_living_doc_generator.assert_not_called()
    mock_log_info.assert_has_calls(
        [
            mocker.call("Starting Living Documentation generation."),
            mocker.call("Living Documentation generation - output path set to `%s`.", expected_output_path),
            mocker.call("Living Documentation generation completed."),
        ],
        any_order=False,
    )
