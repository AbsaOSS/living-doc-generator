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

"""
This module contains an Action Inputs class methods,
which are essential for running the GH action.
"""

import json
import logging
import sys

from living_documentation_generator.model.config_repository import ConfigRepository
from living_documentation_generator.utils.utils import get_action_input, make_absolute_path, get_all_project_directories
from living_documentation_generator.utils.constants import (
    GITHUB_TOKEN,
    PROJECT_STATE_MINING,
    REPOSITORIES,
    OUTPUT_PATH,
    STRUCTURED_OUTPUT, DEFAULT_OUTPUT_PATH,
)

logger = logging.getLogger(__name__)


class ActionInputs:
    """
    A class representing all the action inputs. It is responsible for loading, managing
    and validating the inputs required for running the GH Action.
    """

    def __init__(self):
        self.__github_token: str = ""
        self.__is_project_state_mining_enabled: bool = False
        self.__repositories: list[ConfigRepository] = []
        self.__output_directory: str = ""
        self.__structured_output: bool = False

    @property
    def github_token(self) -> str:
        """Getter of the GitHub authorization token."""
        return self.__github_token

    @property
    def is_project_state_mining_enabled(self) -> bool:
        """Getter of the project state mining switch."""
        return self.__is_project_state_mining_enabled

    @property
    def repositories(self) -> list[ConfigRepository]:
        """Getter of the list of repositories to fetch from."""
        return self.__repositories

    @property
    def output_directory(self) -> str:
        """Getter of the output directory."""
        return self.__output_directory

    @property
    def structured_output(self) -> bool:
        """Getter of the structured output switch."""
        return self.__structured_output

    @staticmethod
    def validate_instance(input_value, expected_type: type, error_message: str, error_buffer: list) -> bool:
        """
        Validates the input value against the expected type.

        @param input_value: The input value to validate.
        @param expected_type: The expected type of the input value.
        @param error_message: The error message to log if the validation fails.
        @param error_buffer: The buffer to store the error messages.
        @return: The boolean result of the validation.
        """

        if not isinstance(input_value, expected_type):
            error_buffer.append(error_message)
            return False
        return True

    def load_from_environment(self, validate: bool = True) -> "ActionInputs":
        """
        Load the action inputs from the environment variables and validate them if needed.

        @param validate: Switch indicating if the inputs should be validated.
        @return: The instance of the ActionInputs class.
        """
        self.__github_token = get_action_input(GITHUB_TOKEN)
        self.__is_project_state_mining_enabled = get_action_input(PROJECT_STATE_MINING, "false").lower() == "true"
        self.__structured_output = get_action_input(STRUCTURED_OUTPUT, "false").lower() == "true"
        repositories_json = get_action_input(REPOSITORIES, "")
        out_path = get_action_input(OUTPUT_PATH, default=DEFAULT_OUTPUT_PATH)
        self.__output_directory = make_absolute_path(out_path)

        # Validate inputs
        if validate:
            self.validate_inputs(repositories_json, out_path)

        logger.debug("Is project state mining allowed: %s.", self.is_project_state_mining_enabled)
        logger.debug("JSON repositories to fetch from: %s.", repositories_json)
        logger.debug("Output directory: %s.", self.output_directory)
        logger.debug("Is output directory structured: %s.", self.structured_output)

        # Parse repositories json string into json dictionary format
        try:
            repositories_json = json.loads(repositories_json)
        except json.JSONDecodeError as e:
            logger.error("Error parsing JSON repositories: %s.", e, exc_info=True)
            sys.exit(1)

        for repository_json in repositories_json:
            config_repository = ConfigRepository()
            if config_repository.load_from_json(repository_json):
                self.__repositories.append(config_repository)
            else:
                logger.error("Failed to load repository from JSON: %s.", repository_json)

        return self

    def validate_inputs(self, repositories_json: str, out_path: str) -> None:
        """
        Validate the input attributes of the action.

        @param repositories_json: The JSON string containing the repositories to fetch.
        @param out_path: The output path to save the results to.
        @return: None
        """
        errors = []

        # Validate INPUT_GITHUB_TOKEN
        if not self.github_token:
            errors.append("INPUT_GITHUB_TOKEN could not be loaded from the environment.")
        if not isinstance(self.github_token, str):
            errors.append("INPUT_GITHUB_TOKEN must be a string.")

        # Validate INPUT_REPOSITORIES and its correct JSON format
        try:
            json.loads(repositories_json)
        except json.JSONDecodeError:
            errors.append("INPUT_REPOSITORIES is not a valid JSON string.")

        # Validate INPUT_OUTPUT_PATH
        if out_path == "":
            errors.append("INPUT_OUTPUT_PATH can not be an empty string.")

        # Check that the INPUT_OUTPUT_PATH is not a directory in the project
        # Note: That would cause a rewriting project files
        project_directories = get_all_project_directories()
        if out_path in project_directories:
            errors.append("INPUT_OUTPUT_PATH can not be a project directory.")

        if errors:
            for error in errors:
                logger.error(error)
            logger.info("GitHub Action is terminating as a cause of an input validation error.")
            sys.exit(1)
