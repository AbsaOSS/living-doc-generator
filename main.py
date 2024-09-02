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
from living_documentation_generator.utils.utils import set_action_output
from living_documentation_generator.utils.logging_config import setup_logging


def run() -> None:
    """
    The main function to run the Living Documentation Generator.

    @return: None
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting Living Documentation generation.")
    action_inputs = ActionInputs().load_from_environment()

    generator = LivingDocumentationGenerator(
        github_token=action_inputs.github_token,
        repositories=action_inputs.repositories,
        project_state_mining_enabled=action_inputs.is_project_state_mining_enabled,
        output_path=action_inputs.output_directory,
    )

    # Generate the Living Documentation
    generator.generate()

    # Set the output for the GitHub Action
    set_action_output("output-path", generator.output_path)
    logger.info("Living Documentation generation - output path set to `%s`.", generator.output_path)

    logger.info("Living Documentation generation completed.")


if __name__ == "__main__":
    run()
