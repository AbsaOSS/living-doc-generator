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
import requests

from living_documentation_regime.model.config_repository import ConfigRepository
from utils.utils import get_action_input
from utils.constants import (
    GITHUB_TOKEN,
    LIV_DOC_REGIME,
    OUTPUT_FORMATS,
    PROJECT_STATE_MINING,
    REPOSITORIES,
    GROUP_OUTPUT_BY_TOPICS,
    STRUCTURED_OUTPUT,
    REPORT_PAGE,
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
    def get_is_report_page_generation_enabled() -> bool:
        """
        Getter of the report page switch. True by default.
        @return: True if report page is enabled, False otherwise.
        """
        return get_action_input(REPORT_PAGE, "true").lower() == "true"

    @staticmethod
    def get_liv_doc_regime() -> bool:
        """
        Getter of the LivDoc regime switch.
        @return: True if LivDoc regime is enabled, False otherwise.
        """
        return get_action_input(LIV_DOC_REGIME, "false").lower() == "true"

    @staticmethod
    def get_output_formats() -> list[str]:
        """
        Getter of the output formats for generated documents.
        @return: A list of output formats.
        """
        output_formats_json = get_action_input(OUTPUT_FORMATS, "[]").strip().lower()
        try:
            normalized_input_json = output_formats_json.replace("'", '"')
            return json.loads(normalized_input_json)
        except json.JSONDecodeError:
            logger.error("Error parsing JSON output formats: %s.", output_formats_json)
            sys.exit(1)

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

    def validate_user_configuration(self) -> None:
        """
        Checks that all the user configuration defined is correct.

        @return: None
        """
        # validate output formats
        ActionInputs.get_output_formats()

        # validate repositories configuration
        repositories: list[ConfigRepository] = self.get_repositories()
        github_token = self.get_github_token()
        headers = {"Authorization": f"token {github_token}"}

        for repository in repositories:
            org_name = repository.organization_name
            repo_name = repository.repository_name
            github_repo_url = f"https://api.github.com/repos/{org_name}/{repo_name}"

            response = requests.get(github_repo_url, headers=headers, timeout=10)

            if response.status_code == 404:
                logger.error(
                    "Repository '%s/%s' could not be found on GitHub. Please verify that the repository "
                    "exists and that your authorization token is correct.",
                    org_name,
                    repo_name,
                )
                sys.exit(1)

        logger.debug("User configuration validation successfully completed.")
