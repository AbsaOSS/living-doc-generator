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
    DOC_USER_STORY_LABEL,
    LIV_DOC_OUTPUT_PATH,
    DOC_FEATURE_LABEL,
    DOC_FUNCTIONALITY_LABEL,
)

logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class MdocExporter(Exporter):
    """A class representing the MDoc format generation exporter."""

    REPORT_PAGE_US_GROUP = "User Story"
    REPORT_PAGE_FEAT_GROUP = "Feature"

    PARENT_PATH_US = "user_stories"
    PARENT_PATH_FEAT = "features"

    def __init__(self, output_path: str):
        self._output_path = output_path

        # templates
        self._us_issue_page_detail_template: Optional[str] = None
        self._feat_issue_page_detail_template: Optional[str] = None
        self._func_issue_page_detail_template: Optional[str] = None

        self._us_index_no_struct_template_file: Optional[str] = None
        self._feat_index_no_struct_template_file: Optional[str] = None

        self._us_index_root_level_template_page: Optional[str] = None
        self._feat_index_root_level_template_page: Optional[str] = None
        self._index_org_level_template: Optional[str] = None

        self._report_page_template: Optional[str] = None

        self._report_page_content: dict[str, str] = {}

    def export(self, **kwargs) -> bool:
        logger.info("MDoc page generation - started.")

        issues: dict[str, ConsolidatedIssue] = kwargs.get("issues", {})
        logger.debug("Exporting %d issues...", len(issues))

        # Load the template files for generating the MDoc pages
        if not self._load_all_templates():
            return False

        # Generate a MDoc page for every issue in expected path
        self._generate_page_per_issue(issues)

        # Generate all structure of the index pages
        self._generate_output_structure(issues)

        # Generate a report page
        if ActionInputs.is_report_page_generation_enabled():
            self._generate_report_page()

        logger.info("MDoc page generation - finished.")
        return True

    def _generate_report_page(self):
        def write_report_page(group: str, parent_dir: str, content: str) -> None:
            header, divider, *error_rows = content.strip().split("\n")
            if error_rows:
                report_page = self._report_page_template.format(
                    date=datetime.now().strftime("%Y-%m-%d"),
                    livdoc_report_page_content=content,
                    group=group,
                )
                with open(
                    os.path.join(make_absolute_path(self._output_path), parent_dir, "report_page.md"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(report_page)

            logger.warning("MDoc page generation - Report page '%s' generated.", group)

        for group, content in self._report_page_content.items():
            parent_dir = self.PARENT_PATH_US if group == self.REPORT_PAGE_US_GROUP else self.PARENT_PATH_FEAT
            write_report_page(group, parent_dir, content)

    def _generate_page_per_issue(self, issues: dict[str, ConsolidatedIssue]) -> None:
        logger.info("Generating MDoc pages for User Stories ...")
        for consolidated_issue in issues.values():
            # self._generate_md_issue_page(consolidated_issue)
            if DOC_USER_STORY_LABEL in consolidated_issue.labels:
                self._generate_md_issue_page_for_us(consolidated_issue)
                self._update_error_page(consolidated_issue, self.REPORT_PAGE_US_GROUP)

        logger.info("Generating MDoc pages for Features ...")
        for consolidated_issue in issues.values():
            if DOC_FEATURE_LABEL in consolidated_issue.labels:
                self._generate_md_issue_page_for_feat(consolidated_issue)
                self._update_error_page(consolidated_issue, self.REPORT_PAGE_FEAT_GROUP)

        logger.info("Generating MDoc pages for Functionalities ...")
        for consolidated_issue in issues.values():
            if DOC_FUNCTIONALITY_LABEL in consolidated_issue.labels:
                # get associated feature ID
                feature_key = None
                feature_id = consolidated_issue.get_feature_id()
                if feature_id is not None:
                    feature_key = f"{consolidated_issue.repository_id}/{feature_id}"

                self._generate_md_issue_page_for_func(consolidated_issue, issues[feature_key] if feature_key else None)
                self._update_error_page(consolidated_issue, self.REPORT_PAGE_FEAT_GROUP)

        logger.info("MDoc page generation - generated `%i` issue pages.", len(issues))

    def _generate_output_structure(self, issues: dict[str, ConsolidatedIssue]) -> None:
        if ActionInputs.is_structured_output_enabled():
            regime_output_path = make_absolute_path(self._output_path)

            # User Story
            generate_root_level_index_page(
                self._us_index_root_level_template_page, os.path.join(regime_output_path, "user_stories")
            )
            self._generate_structured_index_pages(issues, "user_stories")

            # Features
            generate_root_level_index_page(
                self._feat_index_root_level_template_page, os.path.join(regime_output_path, "features")
            )
            self._generate_structured_index_pages(issues, "features")

        # Generate an index page with a summary table about all User Stories
        us_issues: list[ConsolidatedIssue] = [
            issue for issue in issues.values() if DOC_USER_STORY_LABEL in issue.labels
        ]
        self._generate_index_page(self._us_index_no_struct_template_file, "user_stories", us_issues)
        logger.info("MDoc page generation - generated User Stories `_index.md`.")

        # Generate an index page with a summary table about all Features
        feat_issues: list[ConsolidatedIssue] = [issue for issue in issues.values() if DOC_FEATURE_LABEL in issue.labels]
        self._generate_index_page(self._feat_index_no_struct_template_file, "features", feat_issues)
        logger.info("MDoc page generation - generated Features `_index.md`.")

    def _generate_md_issue_page_for_us(self, consolidated_issue: ConsolidatedIssue) -> None:
        """
        Generates a MDoc page for User Story ticket/GH issue from a template and save to the output directory.

        @param consolidated_issue: The ConsolidatedIssue object containing the issue data.
        @return: None
        """
        # Initialize dictionary with replacements
        # TODO - add support for - planned in Issue https://github.com/AbsaOSS/living-doc-generator/issues/111
        #   - GH State badge
        #   - GH Project State badge
        #   - GH Priority
        #   - GH Icon link
        replacements = {
            "title": consolidated_issue.title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issue_content": consolidated_issue.body,
        }

        # Run through all replacements and update template keys with adequate content
        issue_md_page_content = self._us_issue_page_detail_template.format(**replacements)

        # Create a directory structure path for the issue page
        page_directory_path: str = self._generate_directory_path_us(
            self.PARENT_PATH_US, consolidated_issue.repository_id
        )
        os.makedirs(page_directory_path, exist_ok=True)

        # Save the single issue MDoc page
        page_filename = consolidated_issue.generate_page_filename()
        with open(os.path.join(page_directory_path, page_filename), "w", encoding="utf-8") as f:
            f.write(issue_md_page_content)

        logger.debug("Generated MDoc page: %s.", page_filename)

    def _generate_md_issue_page_for_feat(self, consolidated_issue: ConsolidatedIssue) -> None:
        """
        Generates a MDoc page for Feature ticket/GH issue from a template and save to the output directory.

        @param consolidated_issue: The ConsolidatedIssue object containing the issue data.
        @return: None
        """
        # Initialize dictionary with replacements
        # TODO - add support for - planned in Issue https://github.com/AbsaOSS/living-doc-generator/issues/111
        #   - GH State badge
        #   - GH Project State badge
        #   - GH Priority
        #   - GH Icon link

        replacements = {
            "title": consolidated_issue.title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issue_content": consolidated_issue.body,
        }

        # Run through all replacements and update template keys with adequate content
        issue_md_page_content = self._feat_issue_page_detail_template.format(**replacements)

        # Create a directory structure path for the issue page
        page_directory_path: str = self._generate_directory_path_feat(
            self.PARENT_PATH_FEAT, consolidated_issue.repository_id, consolidated_issue.title
        )
        os.makedirs(page_directory_path, exist_ok=True)

        # Save the single issue MDoc page
        page_filename = consolidated_issue.generate_page_filename()
        with open(os.path.join(page_directory_path, page_filename), "w", encoding="utf-8") as f:
            f.write(issue_md_page_content)

        logger.debug("Generated MDoc page: %s.", page_filename)

    def _generate_md_issue_page_for_func(
        self, consolidated_issue: ConsolidatedIssue, feature_consolidated_issue: Optional[ConsolidatedIssue] = None
    ) -> None:
        """
        Generates a MDoc page for Functionality ticket/GH issue from a template and save to the output directory.

        @param consolidated_issue: The ConsolidatedIssue object containing the issue data.
        @return: None
        """
        # Initialize dictionary with replacements
        # TODO - add support for - planned in Issue https://github.com/AbsaOSS/living-doc-generator/issues/111
        #   - GH State badge
        #   - GH Project State badge
        #   - GH Priority
        #   - GH Icon link

        title = consolidated_issue.title
        feature_title = "no_feature"
        if feature_consolidated_issue is not None:
            feature_title = feature_consolidated_issue.title

        replacements = {
            "title": title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issue_content": consolidated_issue.body,
        }

        # Run through all replacements and update template keys with adequate content
        issue_md_page_content = self._func_issue_page_detail_template.format(**replacements)

        # Create a directory structure path for the issue page
        page_directory_path: str = self._generate_directory_path_func(
            self.PARENT_PATH_FEAT, consolidated_issue.repository_id, feature_title
        )
        os.makedirs(page_directory_path, exist_ok=True)

        # Save the single issue MDoc page
        page_filename = consolidated_issue.generate_page_filename()
        with open(os.path.join(page_directory_path, page_filename), "w", encoding="utf-8") as f:
            f.write(issue_md_page_content)

        logger.debug("Generated MDoc page: %s.", page_filename)

    # pylint: disable=too-many-arguments
    def _generate_structured_index_pages(
        self, consolidated_issues: dict[str, ConsolidatedIssue], group_name: str
    ) -> None:
        """
        Generates a set of index pages due to a structured output feature.

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
        repository_ids = issues_by_repository.keys()
        for repository_id in repository_ids:
            self._generate_sub_level_index_page(self._index_org_level_template, repository_id, group_name)
            logger.debug(
                "Generated '%s' organization level `_index.md` for %s.",
                group_name,
                repository_id.split("/")[0],
            )

            logger.info("MDoc page generation - generated `_index.md` pages for %s.", repository_id)

    def _generate_index_page(
        self, issue_index_page_template: str, group_name: str, consolidated_issues: list[ConsolidatedIssue]
    ) -> None:
        """
        Generates an index page with a summary of all issues and save it to the output directory.

        @param issue_index_page_template: The template string for generating the index mdoc page.
        @param consolidated_issues: A dictionary containing all consolidated issues.
        @param repository_id: The repository id used if the structured output is generated.
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
            issue_table += self._generate_mdoc_line(consolidated_issue)

        # Prepare issues replacement for the index page
        replacement = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issue_overview_table": issue_table,
        }

        if len(consolidated_issues) > 0:
            repository_id = consolidated_issues[0].repository_id
        else:
            logger.info("No consolidated issues found for group: %s.", group_name)
            return

        if ActionInputs.is_structured_output_enabled():
            replacement["data_level_name"] = repository_id.split("/")[1]

        # Replace the issue placeholders in the index template
        index_page: str = issue_index_page_template.format(**replacement)

        # Generate a directory structure path for the index page
        # Note: repository_id is used only, if the structured output is generated
        index_directory_path: str = self._generate_index_directory_path(group_name, repository_id)

        # Create an index page file
        with open(os.path.join(index_directory_path, "_index.md"), "w", encoding="utf-8") as f:
            f.write(index_page)

    def _generate_sub_level_index_page(self, index_template: str, repository_id: str, group_name) -> None:
        """
        Generates an index page for the structured output based on the level.

        @param index_template: The template string for generating the index MDoc page.
        @param repository_id: The repository id of a repository that stores the issues.
        @return: None
        """
        replacement = {
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        organization_name = repository_id.split("/")[0]
        replacement["organization_name"] = organization_name

        # Replace the issue placeholders in the index template
        sub_level_index_page = index_template.format(**replacement)

        # Create a sub index page file
        output_path = os.path.join(make_absolute_path(self._output_path), group_name, organization_name)
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

    def _generate_index_directory_path(self, group_name: str, repository_id: Optional[str]) -> str:
        """
        Generates a directory path based on if structured output is required.

        @param repository_id: The repository id.
        @return: The generated directory path.
        """
        output_path: str = os.path.join(make_absolute_path(self._output_path), group_name)

        if ActionInputs.is_structured_output_enabled() and repository_id:
            organization_name, repository_name = repository_id.split("/")
            output_path = os.path.join(output_path, organization_name, repository_name)

        os.makedirs(output_path, exist_ok=True)

        return output_path

    def _load_all_templates(self) -> bool:
        """
        Load all template files for generating the MDoc pages.

        @return: A tuple containing all loaded template files.
        """
        project_root = Path(__file__).resolve().parent.parent.parent

        templates_base_path = os.path.join(project_root, "templates", "living_documentation_regime")

        us_issue_detail_page_template = os.path.join(templates_base_path, "us_issue_detail_page_template.md")
        feat_issue_detail_page_template = os.path.join(templates_base_path, "feat_issue_detail_page_template.md")
        func_issue_detail_page_template = os.path.join(templates_base_path, "func_issue_detail_page_template.md")

        us_index_no_struct_template_file = os.path.join(templates_base_path, "_us_index_no_struct_page_template.md")
        feat_index_no_struct_template_file = os.path.join(templates_base_path, "_feat_index_no_struct_page_template.md")

        us_index_root_level_template_file = os.path.join(templates_base_path, "_us_index_root_level_page_template.md")
        feat_index_root_level_template_file = os.path.join(
            templates_base_path, "_feat_index_root_level_page_template.md"
        )
        index_org_level_template_file = os.path.join(templates_base_path, "_index_org_level_page_template.md")

        report_page_template_file = os.path.join(templates_base_path, "report_page_template.md")

        self._us_issue_page_detail_template: Optional[str] = load_template(
            us_issue_detail_page_template,
            "User Story detail page template file was not successfully loaded.",
        )
        self._feat_issue_page_detail_template: Optional[str] = load_template(
            feat_issue_detail_page_template,
            "Feature detail page template file was not successfully loaded.",
        )
        self._func_issue_page_detail_template: Optional[str] = load_template(
            func_issue_detail_page_template,
            "Functionality detail page template file was not successfully loaded.",
        )

        self._us_index_no_struct_template_file: Optional[str] = load_template(
            us_index_no_struct_template_file,
            "User Story index page template file was not successfully loaded.",
        )
        self._feat_index_no_struct_template_file: Optional[str] = load_template(
            feat_index_no_struct_template_file,
            "Feature index page template file was not successfully loaded.",
        )
        self._us_index_root_level_template_page: Optional[str] = load_template(
            us_index_root_level_template_file,
            "Structured User Story index page template file for root level was not successfully loaded.",
        )
        self._feat_index_root_level_template_page: Optional[str] = load_template(
            feat_index_root_level_template_file,
            "Structured Feature index page template file for root level was not successfully loaded.",
        )
        self._index_org_level_template: Optional[str] = load_template(
            index_org_level_template_file,
            "Structured index page template file for organization level was not successfully loaded.",
        )

        self._report_page_template: Optional[str] = load_template(
            report_page_template_file,
            "Report page template file was not successfully loaded.",
        )

        if not all(
            [
                self._us_issue_page_detail_template,
                self._feat_issue_page_detail_template,
                self._func_issue_page_detail_template,
                self._us_index_no_struct_template_file,
                self._feat_index_no_struct_template_file,
                self._us_index_root_level_template_page,
                self._feat_index_root_level_template_page,
                self._index_org_level_template,
                self._report_page_template,
            ]
        ):
            logger.error("MDoc page generation - failed to load all templates.")
            return False

        return True

    def _update_error_page(self, ci: ConsolidatedIssue, group: str) -> None:
        if ActionInputs.is_report_page_generation_enabled() and ci.errors:
            keys = self._report_page_content.keys()
            if group not in keys:
                self._report_page_content[group] = REPORT_PAGE_HEADER

            repository_id: str = ci.repository_id
            number: int = ci.number
            html_url: str = ci.html_url

            for error_type, error_message in ci.errors.items():
                self._report_page_content[
                    group
                ] += f"| {error_type} | [{repository_id}#{number}]({html_url}) | {error_message} |\n"

    @staticmethod
    def _generate_directory_path_us(parent_path: str, repository_id: str) -> str:
        """
        Generate a list of directory paths based on enabled features.

        @return: The list of generated directory paths.
        """
        output_path: str = make_absolute_path(LIV_DOC_OUTPUT_PATH)

        # If structured output is enabled, create a directory path based on the repository
        if ActionInputs.is_structured_output_enabled() and repository_id:
            organization_name, repository_name = repository_id.split("/")
            output_path = os.path.join(output_path, parent_path, organization_name, repository_name)
        else:
            # If structured output is not enabled, create a directory path based on the parent path
            output_path = os.path.join(output_path, parent_path)

        return output_path

    @staticmethod
    def _generate_directory_path_feat(parent_path: str, repository_id: str, feature_title: str) -> str:
        """
        Generate a list of directory paths based on enabled features.

        @return: The list of generated directory paths.
        """
        output_path: str = make_absolute_path(LIV_DOC_OUTPUT_PATH)

        # If structured output is enabled, create a directory path based on the repository
        if ActionInputs.is_structured_output_enabled() and repository_id:
            organization_name, repository_name = repository_id.split("/")
            output_path = os.path.join(output_path, parent_path, organization_name, repository_name, feature_title)
        else:
            # If structured output is not enabled, create a directory path based on the parent path
            output_path = os.path.join(output_path, parent_path, feature_title)

        return output_path

    @staticmethod
    def _generate_directory_path_func(parent_path: str, repository_id: str, feature_title: str) -> str:
        """
        Generate a list of directory paths based on enabled features.

        @return: The list of generated directory paths.
        """
        output_path: str = make_absolute_path(LIV_DOC_OUTPUT_PATH)

        # If structured output is enabled, create a directory path based on the repository
        if ActionInputs.is_structured_output_enabled() and repository_id:
            organization_name, repository_name = repository_id.split("/")
            output_path = os.path.join(output_path, parent_path, organization_name, repository_name, feature_title)
        else:
            # If structured output is not enabled, create a directory path based on the parent path
            output_path = os.path.join(output_path, parent_path, feature_title)

        return output_path
