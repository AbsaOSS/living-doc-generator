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
This module contains the main script for the Living Documentation Generator GH Action.
It sets up logging, loads action inputs, generates the documentation and sets the output
for the GH Action.
"""

import logging

from living_documentation_regime.action_inputs import ActionInputs
from living_documentation_regime.living_documentation_generator import LivingDocumentationGenerator
from utils.constants import OUTPUT_PATH
from utils.utils import set_action_output, make_absolute_path
from utils.logging_config import setup_logging


def run() -> None:
    """
    The main function to run the Living Documentation Generator.

    @return: None
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting Living Documentation generation.")

    ActionInputs().validate_repositories_configuration()

    if ActionInputs.get_liv_doc_regime():
        logger.info("Living Documentation generation - Starting the `LivDoc` generation regime.")

        # Generate the Living documentation
        LivingDocumentationGenerator().generate()

        logger.info("Living Documentation generation - `LivDoc` generation regime completed.")

    # elif ActionInputs.get_ci_regime():
    #     logger.info("Living Documentation generation - Starting the `CI` generation regime.")
    #
    #     # Generate the CI Documentation
    #     CiDocumentationGenerator().generate()
    #
    #     logger.info("Living Documentation generation - `CI` generation regime completed.")

    # Set the output for the GitHub Action
    output_path: str = make_absolute_path(OUTPUT_PATH)
    set_action_output("output-path", output_path)
    logger.info("Living Documentation generation - output path set to `%s`.", output_path)

    logger.info("Living Documentation generation completed.")


if __name__ == "__main__":
    run()
