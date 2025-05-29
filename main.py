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
import os.path
import sys

from living_doc_utilities.constants import OUTPUT_PATH
from living_doc_utilities.github.utils import set_action_output
from living_doc_utilities.logging_config import setup_logging

from action_inputs import ActionInputs
from living_doc_generator.living_doc_generator import MdocLivingDocumentationGenerator
from utils.constants import GENERATOR_OUTPUT_PATH
from utils.utils import make_absolute_path


def run() -> None:
    """
    The main function is to run the Living Documentation Generator in Mdoc format.

    @return: None
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Living Documentation generator - mdoc - starting.")

    if not ActionInputs().validate_user_configuration():
        logger.info("Living Documentation generator - mdoc - user configuration validation failed.")
        sys.exit(1)

    output_path: str = make_absolute_path(os.path.join(OUTPUT_PATH, GENERATOR_OUTPUT_PATH, "mdoc"))

    # Generate the Living documentation
    res = MdocLivingDocumentationGenerator(output_path).generate()

    # Set the output for the GitHub Action
    set_action_output("output-path", output_path)
    logger.info("Living Documentation generator - mdoc - root output path set to `%s`.", output_path)

    logger.info("Living Documentation generator - mdoc - ending.")

    if not res:
        logger.error("Living Documentation generator - mdoc - generation failed.")
        sys.exit(1)

    logger.info("Living Documentation generator - mdoc - generation successfully completed.")

if __name__ == "__main__":
    run()
