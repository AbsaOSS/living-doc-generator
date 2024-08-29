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
from living_documentation_generator.utils.utils import get_action_input, make_absolute_path
from living_documentation_generator.utils.constants import (
    GITHUB_TOKEN,
    PROJECT_STATE_MINING,
    REPOSITORIES,
    OUTPUT_PATH,
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

    def load_from_environment(self, validate: bool = True) -> "ActionInputs":
        """
        Load the action inputs from the environment variables and validate them if needed.

        @param validate: Switch indicating if the inputs should be validated.
        @return: The instance of the ActionInputs class.
        """
        self.__github_token = get_action_input(GITHUB_TOKEN)
        self.__is_project_state_mining_enabled = get_action_input(PROJECT_STATE_MINING, "false").lower() == "true"
        out_path = get_action_input(OUTPUT_PATH, "./output")
        self.__output_directory = make_absolute_path(out_path)
        repositories_json = get_action_input(REPOSITORIES, "")

        logger.debug("Is project state mining allowed: %s.", self.is_project_state_mining_enabled)
        logger.debug("JSON repositories to fetch from: %s.", repositories_json)
        logger.debug("Output directory: %s.", self.output_directory)

        # Validate inputs
        if validate:
            self.validate_inputs(repositories_json)

        # Parse repositories json string into json dictionary format
        try:
            repositories_json = json.loads(repositories_json)
        except json.JSONDecodeError as e:
            logger.error("Error parsing JSON repositories: %s.", e, exc_info=True)
            sys.exit(1)

        for repository_json in repositories_json:
            config_repository = ConfigRepository()
            config_repository.load_from_json(repository_json)
            self.__repositories.append(config_repository)

        return self

    def validate_inputs(self, repositories_json: str) -> None:
        """
        Validate the input attributes of the action.

        @param repositories_json: The JSON string containing the repositories to fetch.
        @return: None
        """

        # Validate correct format of input repositories_json
        try:
            json.loads(repositories_json)
        except json.JSONDecodeError:
            logger.error("Input attr `repositories_json` is not a valid JSON string.", exc_info=True)
            sys.exit(1)

        # Validate GitHub token
        if not self.__github_token:
            logger.error("GitHub token could not be loaded from the environment.", exc_info=True)
            sys.exit(1)
