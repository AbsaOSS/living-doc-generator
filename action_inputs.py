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
This module contains an ActionInputs class method,
which are essential for running the GH action.
"""

import logging
import os

from living_doc_utilities.github.utils import get_action_input
from living_doc_utilities.inputs.action_inputs import BaseActionInputs

from utils.constants import REPORT_PAGE, RELEASE, SOURCE, VERBOSE_LOGGING, STRUCTURED_OUTPUT

logger = logging.getLogger(__name__)


class ActionInputs(BaseActionInputs):
    """
    A class representing all the action inputs. It is responsible for loading and managing
    and validating the inputs required for running the GH Action.
    """

    @staticmethod
    def is_report_page_generation_enabled() -> bool:
        """
        Getter of the report page switch. False by default.
        @return: True if report page is enabled, False otherwise.
        """
        return get_action_input(REPORT_PAGE, "false").lower() == "true"

    @staticmethod
    def is_release_filtering_enabled() -> bool:
        """
        Getter of the release filtering switch. False by default.
        @return: True
        """
        return get_action_input(RELEASE, "false").lower() == "true"

    @staticmethod
    def get_verbose_logging() -> bool:
        """
        Getter of the verbose logging switch. False by default.
        @return: True if verbose logging is enabled, False otherwise.
        """
        return get_action_input(VERBOSE_LOGGING, "false").lower() == "true"

    @staticmethod
    def get_source() -> str:
        """
        Getter of the source input.
        @return: The source input.
        """
        return get_action_input(SOURCE)

    @staticmethod
    def is_structured_output_enabled() -> bool:
        """
        Getter of the structured output switch.

        throws raise LivDocFetchRepositoriesException when fetching failed (Json or Type error)
        @return: True if structured output is enabled, False otherwise.
        """
        return get_action_input(STRUCTURED_OUTPUT, "false").lower() == "true"

    def _validate(self) -> int:
        err_counter = 0

        # Validate source input
        source: str = self.get_source()
        if not isinstance(source, str) or not source.strip():
            logger.error("Source input must be a non-empty string.")
            err_counter += 1
        else:
            if not os.path.isfile(source):
                logger.error("Source file not found at received path: '%s'.", source)
                err_counter += 1

        if err_counter > 0:
            logger.error("User configuration validation failed.")
        else:
            logger.info("User configuration validation successfully completed.")

        self.print_effective_configuration()

        return err_counter

    def _print_effective_configuration(self) -> None:
        """
        Print the effective configuration of the action inputs.
        """
        logger.info("source: %s", self.get_source())
        logger.info("release filtering enabled: %s", self.is_release_filtering_enabled())
        logger.info("structured output enabled: %s", self.is_structured_output_enabled())
        logger.info("report page generation enabled: %s", self.is_report_page_generation_enabled())
        logger.info("verbose logging: %s", self.get_verbose_logging())
