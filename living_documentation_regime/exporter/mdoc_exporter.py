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
This module contains the MDoc Output Factory class which is responsible
for generating outputs in the MDoc format.
"""

import logging
import os

from datetime import datetime
from pathlib import Path
from typing import Optional

from exporter.exporter import Exporter
from action_inputs import ActionInputs
from living_documentation_regime.model.consolidated_issue import ConsolidatedIssue
from utils.utils import make_absolute_path, generate_root_level_index_page, load_template
from utils.constants import (
    REPORT_PAGE_HEADER,
    TABLE_HEADER_WITH_PROJECT_DATA,
    TABLE_HEADER_WITHOUT_PROJECT_DATA,
    LINKED_TO_PROJECT_TRUE,
    LINKED_TO_PROJECT_FALSE,
)

logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class MdocExporter(Exporter):
    """A class representing the MDoc format generation exporter."""

    def __init__(self, output_path: str):
        self._output_path = output_path
        self._issue_page_detail_template: Optional[str] = None
        self._index_page_template: Optional[str] = None
        self._index_root_level_page: Optional[str] = None
        self._index_org_level_template: Optional[str] = None
        self._index_repo_page_template: Optional[str] = None
        self._index_data_level_template: Optional[str] = None
        self._report_page_template: Optional[str] = None

        self._report_page_content = REPORT_PAGE_HEADER

    def export(self, **kwargs) -> bool:
        logger.info("MDoc page generation - started.")

        issues: dict[str, ConsolidatedIssue] = kwargs.get("issues", {})
        logger.debug("Exporting %d issues...", len(issues))

        # Load the template files for generating the MDoc pages
        if not self._load_all_templates():
            return False

        # Generate a MDoc page for every issue
        topics = self._generate_page_per_issue(issues)

        # Generate all structure of the index pages
        self._generate_output_structure(issues, topics)

        # Generate a report page
        if ActionInputs.is_report_page_generation_enabled():
            self._generate_report_page()

        logger.info("MDoc page generation - finished.")
        return True

    def _generate_report_page(self):
        header, divider, *error_rows = self._report_page_content.strip().split("\n")
        if error_rows:
            report_page_content = "\n".join([header, divider] + error_rows)
            report_page = self._report_page_template.format(
                date=datetime.now().strftime("%Y-%m-%d"), livdoc_report_page_content=report_page_content
            )
            with open(
                os.path.join(make_absolute_path(self._output_path), "report_page.md"), "w", encoding="utf-8"
            ) as f:
                f.write(report_page)

            logger.warning("MDoc page generation - Report page generated.")

    def _generate_page_per_issue(self, issues: dict[str, ConsolidatedIssue]) -> set[str]:
        topics: set[str] = set()
        for consolidated_issue in issues.values():
            self._generate_md_issue_page(consolidated_issue)
            if ActionInputs.is_report_page_generation_enabled() and consolidated_issue.errors:
                repository_id: str = consolidated_issue.repository_id
                number: int = consolidated_issue.number
                html_url: str = consolidated_issue.html_url

                for error_type, error_message in consolidated_issue.errors.items():
                    self._report_page_content += (
                        f"| {error_type} | [{repository_id}#{number}]({html_url}) | {error_message} |\n"
                    )

            for topic in consolidated_issue.topics:
                topics.add(topic)

        logger.info("MDoc page generation - generated `%i` issue pages.", len(issues))
        logger.info("Identified `%i` unique topics.", len(topics))
        return topics

    def _generate_output_structure(self, issues: dict[str, ConsolidatedIssue], topics: set[str]) -> None:
        regime_output_path = make_absolute_path(self._output_path)
        if ActionInputs.is_structured_output_enabled():
            generate_root_level_index_page(self._index_root_level_page, regime_output_path)
            self._generate_structured_index_pages(
                topics,
                issues,
            )

        # Generate an index page with a summary table about all issues grouped by topics
        elif ActionInputs.is_grouping_by_topics_enabled():
            issues: list[ConsolidatedIssue] = list(issues.values())
            generate_root_level_index_page(self._index_root_level_page, regime_output_path)

            for topic in topics:
                self._generate_index_page(self._index_data_level_template, issues, grouping_topic=topic)

        # Generate an index page with a summary table about all issues
        else:
            issues: list[ConsolidatedIssue] = list(issues.values())
            self._generate_index_page(self._index_page_template, issues)
            logger.info("MDoc page generation - generated `_index.md`.")

    def _generate_md_issue_page(self, consolidated_issue: ConsolidatedIssue) -> None:
        """
        Generates a single issue MDoc page from a template and save to the output directory.

        @param issue_page_template: The template string for generating the single MDoc issue page.
        @param consolidated_issue: The ConsolidatedIssue object containing the issue data.
        @return: None
        """

        # Get all replacements for generating single issue page from a template
        title = consolidated_issue.title
        date = datetime.now().strftime("%Y-%m-%d")
        issue_content = consolidated_issue.body

        # Generate a summary table for the issue
        issue_table = self._generate_issue_summary_table(consolidated_issue)

        # Initialize dictionary with replacements
        replacements = {
            "title": title,
            "date": date,
            "page_issue_title": title,
            "issue_summary_table": issue_table,
            "issue_content": issue_content,
        }

        # Run through all replacements and update template keys with adequate content
        issue_md_page_content = self._issue_page_detail_template.format(**replacements)

        # Create a directory structure path for the issue page
        page_directory_paths: list[str] = consolidated_issue.generate_directory_path(issue_table)
        for page_directory_path in page_directory_paths:
            os.makedirs(page_directory_path, exist_ok=True)

            # Save the single issue MDoc page
            page_filename = consolidated_issue.generate_page_filename()
            with open(os.path.join(page_directory_path, page_filename), "w", encoding="utf-8") as f:
                f.write(issue_md_page_content)

            logger.debug("Generated MDoc page: %s.", page_filename)

    # pylint: disable=too-many-arguments
    def _generate_structured_index_pages(
        self,
        topics: set[str],
        consolidated_issues: dict[str, ConsolidatedIssue],
    ) -> None:
        """
        Generates a set of index pages due to a structured output feature.

        @param index_data_level_template: The template string for generating the data level index MDoc page.
        @param index_repo_level_template: The template string for generating the repository level index MDoc page.
        @param index_org_level_template: The template string for generating the organization level index MDoc page.
        @param topics: A set of topics used for grouping issues.
        @param consolidated_issues: A dictionary containing all consolidated issues.
        @return: None
        """
        # Group issues by repository for structured index page content
        issues_by_repository = {}
        for consolidated_issue in consolidated_issues.values():
            repository_id = consolidated_issue.repository_id
            if repository_id not in issues_by_repository:
                issues_by_repository[repository_id] = []
            issues_by_repository[repository_id].append(consolidated_issue)

        # Generate an index page for each repository
        for repository_id, issues in issues_by_repository.items():
            organization_name, repository_name = repository_id.split("/")

            self._generate_sub_level_index_page(self._index_org_level_template, "org", repository_id)
            logger.debug(
                "Generated organization level `_index.md` for %s.",
                organization_name,
            )

            # Generate an index pages for the documentation based on the grouped issues by topics
            if ActionInputs.is_grouping_by_topics_enabled():
                self._generate_sub_level_index_page(self._index_repo_page_template, "repo", repository_id)
                logger.debug(
                    "Generated repository level _index.md` for repository: %s.",
                    repository_name,
                )

                for topic in topics:
                    self._generate_index_page(self._index_data_level_template, issues, repository_id, topic)
                    logger.debug(
                        "Generated data level `_index.md` with topic: %s for %s.",
                        topic,
                        repository_id,
                    )
            else:
                self._generate_index_page(self._index_data_level_template, issues, repository_id)
                logger.debug(
                    "Generated data level `_index.md` for %s",
                    repository_id,
                )

            logger.info("MDoc page generation - generated `_index.md` pages for %s.", repository_id)

    def _generate_index_page(
        self,
        issue_index_page_template: str,
        consolidated_issues: list[ConsolidatedIssue],
        repository_id: str = None,
        grouping_topic: str = None,
    ) -> None:
        """
        Generates an index page with a summary of all issues and save it to the output directory.

        @param issue_index_page_template: The template string for generating the index mdoc page.
        @param consolidated_issues: A dictionary containing all consolidated issues.
        @param repository_id: The repository id used if the structured output is generated.
        @param grouping_topic: The topic used if the grouping issues by topics is enabled.
        @return: None
        """
        # Initializing the issue table header based on the project mining state
        issue_table = (
            TABLE_HEADER_WITH_PROJECT_DATA
            if ActionInputs.is_project_state_mining_enabled()
            else TABLE_HEADER_WITHOUT_PROJECT_DATA
        )

        # Create an issue summary table for every issue
        for consolidated_issue in consolidated_issues:
            if ActionInputs.is_grouping_by_topics_enabled():
                for topic in consolidated_issue.topics:
                    if grouping_topic == topic:
                        issue_table += self._generate_mdoc_line(consolidated_issue)
            else:
                issue_table += self._generate_mdoc_line(consolidated_issue)

        # Prepare issues replacement for the index page
        replacement = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issue_overview_table": issue_table,
        }

        if ActionInputs.is_grouping_by_topics_enabled():
            replacement["data_level_name"] = grouping_topic
        elif ActionInputs.is_structured_output_enabled():
            replacement["data_level_name"] = repository_id.split("/")[1]

        # Replace the issue placeholders in the index template
        index_page: str = issue_index_page_template.format(**replacement)

        # Generate a directory structure path for the index page
        # Note: repository_id is used only, if the structured output is generated
        index_directory_path: str = self._generate_index_directory_path(repository_id, grouping_topic)

        # Create an index page file
        with open(os.path.join(index_directory_path, "_index.md"), "w", encoding="utf-8") as f:
            f.write(index_page)

    def _generate_sub_level_index_page(self, index_template: str, level: str, repository_id: str) -> None:
        """
        Generates an index page for the structured output based on the level.

        @param index_template: The template string for generating the index MDoc page.
        @param level: The level of the index page. Enum for "org" or "repo".
        @param repository_id: The repository id of a repository that stores the issues.
        @return: None
        """
        index_level_dir = ""
        replacement = {
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        # Set correct behaviour based on the level
        if level == "org":
            organization_name = repository_id.split("/")[0]
            index_level_dir = organization_name
            replacement["organization_name"] = organization_name
        elif level == "repo":
            repository_name = repository_id.split("/")[1]
            index_level_dir = repository_id
            replacement["repository_name"] = repository_name

        # Replace the issue placeholders in the index template
        sub_level_index_page = index_template.format(**replacement)

        # Create a sub index page file
        output_path = os.path.join(make_absolute_path(self._output_path), index_level_dir)
        os.makedirs(output_path, exist_ok=True)
        with open(os.path.join(output_path, "_index.md"), "w", encoding="utf-8") as f:
            f.write(sub_level_index_page)

    @staticmethod
    def _generate_mdoc_line(consolidated_issue: ConsolidatedIssue) -> str:
        """
        Generates a MDoc summary line for a single issue.

        @param consolidated_issue: The ConsolidatedIssue object containing the issue data.
        @return: The MDoc line for the issue.
        """
        organization_name = consolidated_issue.organization_name
        repository_name = consolidated_issue.repository_name
        number = consolidated_issue.number
        title = consolidated_issue.title
        title = title.replace("|", " _ ")
        issue_link_base = consolidated_issue.title.replace(" ", "-").lower()
        issue_mdoc_link = f"features#{issue_link_base}"
        url = consolidated_issue.html_url
        state = consolidated_issue.state

        status_list = [project_status.status for project_status in consolidated_issue.project_issue_statuses]
        status = ", ".join(status_list) if status_list else "---"

        # Change the bool values to more user-friendly characters
        if ActionInputs.is_project_state_mining_enabled():
            if consolidated_issue.linked_to_project:
                linked_to_project = LINKED_TO_PROJECT_TRUE
            else:
                linked_to_project = LINKED_TO_PROJECT_FALSE

            # Generate the MDoc issue line WITH extra project data
            md_issue_line = (
                f"| {organization_name} | {repository_name} | [#{number} - {title}]({issue_mdoc_link}) |"
                f" {linked_to_project} | {status} |<a href='{url}' target='_blank'>GitHub link</a> |\n"
            )
        else:
            # Generate the MDoc issue line WITHOUT project data
            md_issue_line = (
                f"| {organization_name} | {repository_name} | [#{number} - {title}]({issue_mdoc_link}) |"
                f" {state} |<a href='{url}' target='_blank'>GitHub link</a> |\n"
            )

        return md_issue_line

    @staticmethod
    def _generate_issue_summary_table(consolidated_issue: ConsolidatedIssue) -> str:
        """
        Generates a string representation of feature info in a table format.

        @param consolidated_issue: The ConsolidatedIssue object containing the issue data.
        @return: The string representation of the issue info in a table format.
        """
        # Join issue labels into one string
        labels = consolidated_issue.labels
        labels = ", ".join(labels) if labels else None

        # Format issue URL as a MDoc link
        issue_url = consolidated_issue.html_url
        issue_url = f"<a href='{issue_url}' target='_blank'>GitHub link</a> " if issue_url else None

        # Define the header for the issue summary table
        headers = [
            "Organization name",
            "Repository name",
            "Issue number",
            "Title",
            "State",
            "Issue URL",
            "Created at",
            "Updated at",
            "Closed at",
            "Labels",
        ]

        # Define the values for the issue summary table
        values = [
            consolidated_issue.organization_name,
            consolidated_issue.repository_name,
            consolidated_issue.number,
            consolidated_issue.title,
            consolidated_issue.state.lower(),
            issue_url,
            consolidated_issue.created_at,
            consolidated_issue.updated_at,
            consolidated_issue.closed_at,
            labels,
        ]

        # Update the summary table, based on the project data mining situation
        if ActionInputs.is_project_state_mining_enabled():
            project_statuses = consolidated_issue.project_issue_statuses

            if consolidated_issue.linked_to_project:
                project_data_header = [
                    "Project title",
                    "Status",
                    "Priority",
                    "Size",
                    "MoSCoW",
                ]

                for project_status in project_statuses:
                    # Update the summary data table for every project attached to repository issue
                    project_data_values = [
                        project_status.project_title,
                        project_status.status,
                        project_status.priority,
                        project_status.size,
                        project_status.moscow,
                    ]

                    headers.extend(project_data_header)
                    values.extend(project_data_values)
            else:
                headers.append("Linked to project")
                linked_to_project = LINKED_TO_PROJECT_FALSE
                values.append(linked_to_project)

        # Initialize the MDoc table
        issue_info = "| Attribute | Content |\n|---|---|\n"

        # Add together all the attributes from the summary table in MDoc format
        for attribute, content in zip(headers, values):
            issue_info += f"| {attribute} | {content} |\n"

        return issue_info

    def _generate_index_directory_path(self, repository_id: Optional[str], topic: Optional[str]) -> str:
        """
        Generates a directory path based on if structured output is required.

        @param repository_id: The repository id.
        @param topic: The topic used for grouping issues.
        @return: The generated directory path.
        """
        output_path: str = make_absolute_path(self._output_path)

        if ActionInputs.is_structured_output_enabled() and repository_id:
            organization_name, repository_name = repository_id.split("/")
            output_path = os.path.join(output_path, organization_name, repository_name)

        if ActionInputs.is_grouping_by_topics_enabled() and topic:
            output_path = os.path.join(output_path, topic)

        os.makedirs(output_path, exist_ok=True)

        return output_path

    def _load_all_templates(self) -> bool:
        """
        Load all template files for generating the MDoc pages.

        @return: A tuple containing all loaded template files.
        """
        project_root = Path(__file__).resolve().parent.parent.parent
        # project_root = os.path.dirname(os.path.abspath(__file__))
        templates_base_path = os.path.join(project_root, "templates", "living_documentation_regime")

        issue_page_template_file = os.path.join(templates_base_path, "issue_detail_page_template.md")
        index_no_struct_template_file = os.path.join(templates_base_path, "_index_no_struct_page_template.md")
        index_root_level_template_file = os.path.join(templates_base_path, "_index_root_level_page_template.md")
        index_org_level_template_file = os.path.join(templates_base_path, "_index_org_level_page_template.md")
        index_data_level_template_file = os.path.join(templates_base_path, "_index_data_level_page_template.md")
        index_topic_page_template_file = os.path.join(templates_base_path, "_index_repo_page_template.md")
        report_page_template_file = os.path.join(templates_base_path, "report_page_template.md")

        self._issue_page_detail_template: Optional[str] = load_template(
            issue_page_template_file,
            "Issue page template file was not successfully loaded.",
        )
        self._index_page_template: Optional[str] = load_template(
            index_no_struct_template_file,
            "Index page template file was not successfully loaded.",
        )
        self._index_root_level_page: Optional[str] = load_template(
            index_root_level_template_file,
            "Structured index page template file for root level was not successfully loaded.",
        )
        self._index_org_level_template: Optional[str] = load_template(
            index_org_level_template_file,
            "Structured index page template file for organization level was not successfully loaded.",
        )
        self._index_repo_page_template: Optional[str] = load_template(
            index_topic_page_template_file,
            "Structured index page template file for repository level was not successfully loaded.",
        )
        self._index_data_level_template: Optional[str] = load_template(
            index_data_level_template_file,
            "Structured index page template file for data level was not successfully loaded.",
        )
        self._report_page_template: Optional[str] = load_template(
            report_page_template_file,
            "Report page template file was not successfully loaded.",
        )

        if not all(
            [
                self._issue_page_detail_template,
                self._index_page_template,
                self._index_root_level_page,
                self._index_org_level_template,
                self._index_repo_page_template,
                self._index_data_level_template,
                self._report_page_template,
            ]
        ):
            logger.error("MDoc page generation - failed to load all templates.")
            return False

        return True
