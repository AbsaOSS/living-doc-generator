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

from living_documentation_generator.action_inputs import ActionInputs
from living_documentation_generator.generator import LivingDocumentationGenerator
from living_documentation_generator.utils.constants import OUTPUT_PATH, DEFAULT_OUTPUT_PATH
from living_documentation_generator.utils.utils import set_action_output, get_action_input
from living_documentation_generator.utils.logging_config import setup_logging


def run() -> None:
    """
    The main function to run the Living Documentation Generator.

    @return: None
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting Living Documentation generation.")

    # Validate the action inputs
    out_path_from_config = get_action_input(OUTPUT_PATH, default=DEFAULT_OUTPUT_PATH)
    ActionInputs.validate_inputs(out_path_from_config)

    # Create the Living Documentation Generator
    generator = LivingDocumentationGenerator()

    # Generate the Living Documentation
    generator.generate()

    # Set the output for the GitHub Action
    output_path = ActionInputs.get_output_directory()
    set_action_output("output-path", output_path)
    logger.info("Living Documentation generation - output path set to `%s`.", output_path)

    logger.info("Living Documentation generation completed.")


if __name__ == "__main__":
    run()
