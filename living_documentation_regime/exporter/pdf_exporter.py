# Copyright 2025 ABSA Group Limited
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
This module contains the PDF Output Factory class which is responsible
for generating outputs in the PDF format.
"""

import logging

from exporter.exporter import Exporter
from living_documentation_regime.model.consolidated_issue import ConsolidatedIssue
from pypdf import PdfWriter
from fpdf import FPDF

logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class PDFExporter(Exporter):
    def __init__(self, output_path: str):
        self._output_path = output_path
        # self.pdf_writer = PdfWriter()
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_font('helvetica', size=12)

    def export(self, **kwargs) -> bool:
        logger.info("PDF generation - started.")

        issues: dict[str, ConsolidatedIssue] = kwargs.get("issues", {})
        logger.debug("Exporting %d issues...", len(issues))
        # self.pdf_writer.add_blank_page(width=8.27 * 72, height=11.7 * 72)
        # self.pdf_writer.write(self._output_path)
        self.pdf.cell(text="hello world number of issues is: " + str(len(issues)), ln=True)
        self.pdf.output(self._output_path)
        # # Load the template files for generating the MDoc pages
        # if not self._load_all_templates():
        #     return False
        #
        # # Generate a MDoc page for every issue in expected path
        # self._generate_page_per_issue(issues)
        #
        # # Generate all structure of the index pages
        # self._generate_output_structure(issues)
        #
        # # Generate a report page
        # if ActionInputs.is_report_page_generation_enabled():
        #     self._generate_report_page()

        logger.info("MDoc page generation - finished.")
        return True