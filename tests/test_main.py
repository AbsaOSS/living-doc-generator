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

from living_documentation_generator.generator import LivingDocumentationGenerator
from main import run


# run


def test_run_correct_behaviour(mocker):
    # Arrange
    mock_log_info = mocker.patch("logging.getLogger").return_value.info
    mock_get_action_input = mocker.patch("main.get_action_input")
    mock_get_action_input.side_effect = lambda first_arg, **kwargs: (
        "./user/output/path" if first_arg == "OUTPUT_PATH" else None
    )
    mocker.patch("main.ActionInputs.get_output_directory", return_value="./user/output/path")
    mocker.patch.dict(os.environ, {"INPUT_GITHUB_TOKEN": "fake_token"})
    mocker.patch.object(LivingDocumentationGenerator, "generate")

    # Act
    run()

    # Assert
    mock_log_info.assert_has_calls(
        [
            mocker.call("Starting Living Documentation generation."),
            mocker.call("Living Documentation generation - output path set to `%s`.", "./user/output/path"),
            mocker.call("Living Documentation generation completed."),
        ]
    )
