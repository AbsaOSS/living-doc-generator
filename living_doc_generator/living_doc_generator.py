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
This module contains the LivingDocumentationGenerator class, which is responsible for generating
The Living Documentation output.
"""

import logging
import os
import shutil

from living_doc_utilities.model.issues import Issues

from action_inputs import ActionInputs
from living_doc_generator.mdoc_exporter import MdocExporter

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class MdocLivingDocumentationGenerator:
    """
    A class representing the Living Documentation Generator - Mdoc output format.
    The class generates output in the Mdoc format.
    """

    def __init__(self, output_path: str):
        self.__output_path = output_path

    def generate(self) -> bool:
        """
        Generate the Living Documentation output in Mdoc format.

        @return: True if generation is successful, False otherwise (error occurred).
        """
        self._clean_output_directory()
        logger.debug("Output directory cleaned.")

        # load issues data
        logger.info("Loading of issue from source - started.")
        issues: Issues = Issues.load_from_json(ActionInputs.get_source())
        logger.info("Loading of issue from source - finished.")

        # Generate markdown pages
        logger.info("Generating Living Documentation output - started.")
        res = self._generate_living_documents(issues)
        logger.info("Generating Living Documentation output - finished.")

        return res

    def _clean_output_directory(self) -> None:
        """
        Clean the output directory from the previous run.

        @return: None
        """
        if os.path.exists(self.__output_path):
            shutil.rmtree(self.__output_path)
        os.makedirs(self.__output_path)

    def _generate_living_documents(self, issues: Issues) -> bool:
        """
        Generate the output in the Mdoc format.

        @param issues: Issues object containing the source issue data.
        @return: True if generation is successful, False otherwise (error occurred).
        """
        if MdocExporter(self.__output_path).export(issues=issues):
            logger.info("Living Documentation mdoc output generated successfully.")
            return True

        logger.error("Living Documentation mdoc output generation failed.")
        return False
