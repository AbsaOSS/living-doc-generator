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
    LIV_DOC_OUTPUT_FORMATS,
    LIV_DOC_PROJECT_STATE_MINING,
    LIV_DOC_REPOSITORIES,
    LIV_DOC_GROUP_OUTPUT_BY_TOPICS,
    LIV_DOC_STRUCTURED_OUTPUT,
    REPORT_PAGE,
    Regime,
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
    def is_living_doc_regime_enabled() -> bool:
        """
        Getter of the LivDoc regime switch.
        @return: True if LivDoc regime is enabled, False otherwise.
        """
        regime: str = Regime.LIV_DOC_REGIME.value
        return get_action_input(regime, "false").lower() == "true"

    @staticmethod
    def get_liv_doc_output_formats() -> list[str]:
        """
        Getter of the LivDoc regime output formats for generated documents.
        @return: A list of LivDoc output formats.
        """
        output_formats_string = get_action_input(LIV_DOC_OUTPUT_FORMATS, "mdoc").strip().lower()
        output_formats = [fmt.strip() for fmt in output_formats_string.split(",")]
        return output_formats

    @staticmethod
    def get_is_project_state_mining_enabled() -> bool:
        """
        Getter of the project state mining switch.
        @return: True if project state mining is enabled, False otherwise.
        """
        return get_action_input(LIV_DOC_PROJECT_STATE_MINING, "false").lower() == "true"

    @staticmethod
    def get_is_grouping_by_topics_enabled() -> bool:
        """
        Getter of the switch, that will group the tickets in the index.md file by topics.
        @return: True if grouping by topics is enabled, False otherwise.
        """
        return get_action_input(LIV_DOC_GROUP_OUTPUT_BY_TOPICS, "false").lower() == "true"

    @staticmethod
    def get_is_structured_output_enabled() -> bool:
        """
        Getter of the structured output switch.
        @return: True if structured output is enabled, False otherwise.
        """
        return get_action_input(LIV_DOC_STRUCTURED_OUTPUT, "false").lower() == "true"

    @staticmethod
    def get_repositories() -> list[ConfigRepository]:
        """
        Getter and parser of the Config Repositories.
        @return: A list of Config Repositories.
        """
        repositories = []
        repositories_json = get_action_input(LIV_DOC_REPOSITORIES, "[]")
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
        Checks that all the user configurations defined are correct.
        @return: None
        """
        logger.debug("User configuration validation started")

        # validate repositories configuration
        repositories: list[ConfigRepository] = self.get_repositories()
        github_token = self.get_github_token()
        headers = {"Authorization": f"token {github_token}"}

        # Validate GitHub token
        response = requests.get("https://api.github.com/octocat", headers=headers, timeout=10)
        if response.status_code != 200:
            logger.error(
                "Can not connect to GitHub. Possible cause: Invalid GitHub token. Status code: %s, Response: %s",
                response.status_code,
                response.text,
            )
            sys.exit(1)

        repository_error_count = 0
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
                repository_error_count += 1
            elif response.status_code != 200:
                logger.error(
                    "An error occurred while validating the repository '%s/%s'. "
                    "The response status code is %s. Response: %s",
                    org_name,
                    repo_name,
                    response.status_code,
                    response.text,
                )
                repository_error_count += 1
        if repository_error_count > 0:
            sys.exit(1)

        # log user configuration
        logger.debug("User configuration validation successfully completed.")

        # log regime: enabled/disabled
        logger.debug("Regime: `LivDoc`: %s.", "Enabled" if ActionInputs.is_living_doc_regime_enabled() else "Disabled")

        # log common user inputs
        logger.debug("Global: `report-page`: %s.", ActionInputs.get_is_report_page_generation_enabled())

        # log liv-doc regime user inputs
        if ActionInputs.is_living_doc_regime_enabled():
            logger.debug("Regime(LivDoc): `liv-doc-repositories`: %s.", ActionInputs.get_repositories())
            logger.debug(
                "Regime(LivDoc): `liv-doc-project-state-mining`: %s.",
                ActionInputs.get_is_project_state_mining_enabled(),
            )
            logger.debug(
                "Regime(LivDoc): `liv-doc-structured-output`: %s.", ActionInputs.get_is_structured_output_enabled()
            )
            logger.debug(
                "Regime(LivDoc): `liv-doc-group-output-by-topics`: %s.",
                ActionInputs.get_is_grouping_by_topics_enabled(),
            )
            logger.debug("Regime(LivDoc): `liv-doc-output-formats`: %s.", ActionInputs.get_liv_doc_output_formats())
