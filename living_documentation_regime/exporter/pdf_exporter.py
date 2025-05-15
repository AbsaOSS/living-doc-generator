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
from datetime import datetime
from pathlib import Path
import markdown

from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader

from exporter.exporter import Exporter
from living_documentation_regime.model.consolidated_issue import ConsolidatedIssue

logger = logging.getLogger(__name__)

from fpdf import FPDF

lorem_ipsum = "Etiam bibendum elit eget erat. Vivamus ac leo pretium faucibus. Pellentesque sapien. Morbi scelerisque luctus velit. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Aenean placerat. Nulla non arcu lacinia neque faucibus fringilla. Et harum quidem rerum facilis est et expedita distinctio. Integer vulputate sem a nibh rutrum consequat. Pellentesque ipsum."

class PDF(FPDF):
    def header(self):
        # Setting font: helvetica bold 15
        self.set_font("helvetica", style="B", size=15)
        # Calculating width of title and setting cursor position:
        width = self.get_string_width(self.title) + 6
        self.set_x((210 - width) / 2)
        # Setting colors for frame, background and text:
        self.set_draw_color(0, 80, 180)
        self.set_fill_color(230, 230, 0)
        self.set_text_color(220, 50, 50)
        # Setting thickness of the frame (1 mm)
        self.set_line_width(1)
        # Printing title:
        self.cell(
            width,
            9,
            self.title,
            border=1,
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
            fill=True,
        )
        # Performing a line break:
        self.ln(10)

    def footer(self):
        # Setting position at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", style="I", size=8)
        # Setting text color to gray:
        self.set_text_color(128)
        # Printing page number
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def chapter_title(self, num, label):
        # Setting font: helvetica 12
        self.set_font("helvetica", size=20)
        # Printing chapter name:
        self.cell(
            0,
            6,
            f"Chapter {num} : {label}",
            new_x="LMARGIN",
            new_y="NEXT",
            align="L",
            fill=True,
        )
        # Performing a line break:
        self.ln(4)

    def chapter_body(self, issue: ConsolidatedIssue):
        # Setting font: Times 12
        self.set_font("Times", size=12)
        # Printing justified text:
        self.multi_cell(0, 5, issue.body)
        # Performing a line break:
        self.ln()
        # Final mention in italics:
        self.set_font(style="I")
        self.cell(0, 5, "(end of excerpt)")

    def print_chapter(self, num, issue: ConsolidatedIssue):
        self.add_page()
        self.chapter_title(num, issue.title)
        self.chapter_body(issue)


# pylint: disable=too-many-instance-attributes, too-few-public-methods
# class PDFExporter(Exporter):
#     def __init__(self, output_path: str):
#         self._output_path = output_path
#         # self.pdf_writer = PdfWriter()
#         # self.pdf = FPDF()
#         # self.pdf.add_page()
#         # self.pdf.set_font('helvetica', size=12)
#
#     def export(self, **kwargs) -> bool:
#         logger.info("PDF generation - started.")
#
#         issues: dict[str, ConsolidatedIssue] = kwargs.get("issues", {})
#         logger.debug("Exporting %d issues...", len(issues))
#         # self.pdf_writer.add_blank_page(width=8.27 * 72, height=11.7 * 72)
#         # self.pdf_writer.write(self._output_path)
#         # self.pdf.cell(text="hello world number of issues is: " + str(len(issues)), ln=True)
#         # self.pdf.output(self._output_path)
#
#         pdf = PDF()
#         pdf.set_title("Documentation for project XYZ")
#         pdf.set_author("Pdf exporter")
#         for num, issue in  enumerate(issues.values()):
#             pdf.print_chapter(num, issue)
#         pdf.output(self._output_path)
#
#
#         logger.info("PDF generation - finished.")
#         return True

class PDFExporter(Exporter):
    def __init__(self, output_path: str):
        self.issues = None
        self._output_path = output_path

    def __fill_sections(self):
        sections = {"User Stories": [], "Features": [], "Functionalities": []}

        for issue in self.issues.values():
            title = issue.title.lower()
            if "story" in title:
                sections["User Stories"].append(issue)
            elif "feature" in title:
                sections["Features"].append(issue)
            else:
                sections["Functionalities"].append(issue)

        for issues_list in sections.values():
            issues_list.sort(key=lambda i: i.number)

        sections = {key: value for key, value in sections.items() if value}
        return sections

    def export(self, **kwargs) -> bool:
        """Generate a PDF file from a string of HTML."""
        self.issues: dict[str, ConsolidatedIssue] = kwargs.get("issues", {})

        for issue in self.issues.values():
            if issue.body:
                issue.set_body_html(markdown.markdown(issue.body))

        sections = self.__fill_sections()
        toc = [{"name": name, "issues": issues} for name, issues in sections.items()]


        base_dir = Path(__file__).parent
        html_path = base_dir / "templates"

        environment = Environment(loader=FileSystemLoader(html_path))
        report = environment.get_template("template1.html")

        html = HTML(string=report.render(
            project_name="Demo name project",
            generation_date=datetime.now().strftime("%Y-%m-%d"),
            abstract="This is Auto generated abstract." + lorem_ipsum,
            author="QA Squad",
            sections=sections,
            toc=toc
        ))

        css = CSS(html_path / "styles.css")
        html.write_pdf(self._output_path + "demo_output.pdf", stylesheets=[css])
        return True

