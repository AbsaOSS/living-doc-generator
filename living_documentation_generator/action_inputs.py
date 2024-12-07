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
import os
import sys

from living_documentation_generator.model.config_repository import ConfigRepository
from living_documentation_generator.utils.utils import get_action_input, make_absolute_path, get_all_project_directories
from living_documentation_generator.utils.constants import (
    GITHUB_TOKEN,
    PROJECT_STATE_MINING,
    REPOSITORIES,
    GROUP_OUTPUT_BY_TOPICS,
    STRUCTURED_OUTPUT,
    OUTPUT_PATH,
    DEFAULT_OUTPUT_PATH,
)

logger = logging.getLogger(__name__)


class ActionInputs:
    """
    A class representing all the action inputs. It is responsible for loading, managing
    and validating the inputs required for running the GH Action.
    """

    @staticmethod
    def get_github_token() -> str:
        """
        Getter of the GitHub authorization token.
        @return: The GitHub authorization token.
        """
        return get_action_input(GITHUB_TOKEN)

    @staticmethod
    def get_is_project_state_mining_enabled() -> bool:
        """
        Getter of the project state mining switch.
        @return: True if project state mining is enabled, False otherwise.
        """
        return get_action_input(PROJECT_STATE_MINING, "false").lower() == "true"

    @staticmethod
    def get_is_grouping_by_topics_enabled() -> bool:
        """
        Getter of the switch, that will group the tickets in the index.md file by topics.
        @return: True if grouping by topics is enabled, False otherwise.
        """
        return get_action_input(GROUP_OUTPUT_BY_TOPICS, "false").lower() == "true"

    @staticmethod
    def get_is_structured_output_enabled() -> bool:
        """
        Getter of the structured output switch.
        @return: True if structured output is enabled, False otherwise.
        """
        return get_action_input(STRUCTURED_OUTPUT, "false").lower() == "true"

    @staticmethod
    def get_repositories() -> list[ConfigRepository]:
        """
        Getter and parser of the Config Repositories.
        @return: A list of Config Repositories.
        """
        repositories = []
        repositories_json = get_action_input(REPOSITORIES, "[]")
        try:
            # Parse repositories json string into json dictionary format
            repositories_json = json.loads(repositories_json)

            # Load repositories into ConfigRepository object from JSON
            for repository_json in repositories_json:
                config_repository = ConfigRepository()
                if config_repository.load_from_json(repository_json):
                    repositories.append(config_repository)
                else:
                    logger.error("Failed to load repository from JSON: %s.", repository_json)

        except json.JSONDecodeError as e:
            logger.error("Error parsing JSON repositories: %s.", e, exc_info=True)
            sys.exit(1)

        except TypeError:
            logger.error("Type error parsing input JSON repositories: %s.", repositories_json)
            sys.exit(1)

        return repositories

    @staticmethod
    def get_output_directory() -> str:
        """Getter of the output directory."""
        out_path = get_action_input(OUTPUT_PATH, default=DEFAULT_OUTPUT_PATH)
        return make_absolute_path(out_path)

    @staticmethod
    def validate_inputs(out_path: str) -> None:
        """
        Loads the inputs provided for the Living documentation generator.
        Logs any validation errors and exits if any are found.

        @param out_path: The output path for the generated documentation.
        @return: None
        """

        # Validate INPUT_REPOSITORIES
        ActionInputs.get_repositories()

        # Validate INPUT_OUTPUT_PATH
        if out_path == "":
            logger.error("INPUT_OUTPUT_PATH can not be an empty string.")
            sys.exit(1)

        # Check that the INPUT_OUTPUT_PATH is not a project directory
        # Note: That would cause a rewriting project files
        project_directories = get_all_project_directories()
        abspath_user_output_path = os.path.abspath(ActionInputs.get_output_directory())

        # Ensure project directories are absolute paths
        project_abspath_directories = [os.path.abspath(d) for d in project_directories]

        if abspath_user_output_path in project_abspath_directories:
            project_abspath_directories.remove(abspath_user_output_path)

        for project_directory in project_abspath_directories:
            # Finds the common path between the absolute paths of out_path and project_directory
            common_path = os.path.commonpath([os.path.abspath(out_path), os.path.abspath(project_directory)])

            # Check if common path is equal to the absolute path of project_directory
            if common_path == os.path.abspath(project_directory):
                logger.error("INPUT_OUTPUT_PATH cannot be chosen as a part of any project folder.")
                sys.exit(1)

        logger.debug("Action inputs validation successfully completed.")
