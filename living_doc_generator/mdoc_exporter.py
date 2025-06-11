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
This module contains the MDoc Output Factory class, which is responsible
for generating outputs in the MDoc format.
"""

import logging
import os

from datetime import datetime
from pathlib import Path
from typing import Optional, TypeVar, Sequence

from living_doc_utilities.exporter.exporter import Exporter
from living_doc_utilities.model.feature_issue import FeatureIssue
from living_doc_utilities.model.functionality_issue import FunctionalityIssue
from living_doc_utilities.model.issue import Issue
from living_doc_utilities.model.issues import Issues
from living_doc_utilities.model.user_story_issue import UserStoryIssue

from action_inputs import ActionInputs
from utils.utils import make_absolute_path, generate_root_level_index_page, load_template, sanitize_filename
from utils.constants import (
    REPORT_PAGE_HEADER,
    TABLE_HEADER_WITH_PROJECT_DATA,
    TABLE_HEADER_WITHOUT_PROJECT_DATA,
    LINKED_TO_PROJECT_TRUE,
    LINKED_TO_PROJECT_FALSE,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Issue)


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
        self._us_issue_page_detail_template: str = ""
        self._feat_issue_page_detail_template: str = ""
        self._func_issue_page_detail_template: str = ""
        self._us_index_root_level_template_page: str = ""
        self._feat_index_root_level_template_page: str = ""
        self._index_org_level_template: str = ""
        self._report_page_template: str = ""
        self._us_index_no_struct_template_file: str = ""
        self._feat_index_no_struct_template_file: str = ""
        self._report_page_content: dict[str, str] = {}

        self.project_statuses_included: bool = False

    def export(self, **kwargs) -> bool:
        logger.info("MDoc page generation - started.")

        issues: Issues = kwargs.get("issues", Issues())
        self.project_statuses_included = issues.project_states_included
        logger.debug("Exporting %d issues...", issues.count())

        # Load the template files for generating the MDoc pages
        if not self._load_all_templates():
            return False

        # Generate an MDoc page for every issue in the expected path
        self._generate_page_per_issue(issues)

        # Generate all the structure of the index pages
        self._generate_output_structure(issues)

        # Generate a report page
        if ActionInputs.is_report_page_generation_enabled():
            self._generate_report_page()

        logger.info("MDoc page generation - finished.")
        return True

    def _generate_report_page(self):
        def write_report_page(group: str, parent_dir: str, content: str) -> None:
            header, divider, *error_rows = content.strip().split("\n")  # pylint: disable=unused-variable
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

    def _generate_page_per_issue(self, issues: Issues) -> None:
        logger.info("Generating MDoc pages ...")
        for issue in issues.issues.values():
            if isinstance(issue, UserStoryIssue):
                self._generate_md_issue_page_for_us(issue)
                self._update_error_page(issue, self.REPORT_PAGE_US_GROUP)

            if isinstance(issue, FeatureIssue):
                self._generate_md_issue_page_for_feat(issue)
                self._update_error_page(issue, self.REPORT_PAGE_FEAT_GROUP)

            if isinstance(issue, FunctionalityIssue):
                # get associated feature ID
                feature_issue = None
                feature_ids = issue.get_related_feature_ids()
                if feature_ids:
                    feature_key = f"{issue.repository_id}/{feature_ids[0]}"
                    possible_feature = issues.get_issue(feature_key)
                    if isinstance(possible_feature, FeatureIssue):
                        feature_issue = possible_feature

                self._generate_md_issue_page_for_func(issue, feature_issue)
                self._update_error_page(issue, self.REPORT_PAGE_FEAT_GROUP)

        logger.info("MDoc page generation - generated `%i` issue pages.", issues.count())

    def _generate_output_structure(self, issues: Issues) -> None:
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
        us_issues: list[UserStoryIssue] = [
            issue for issue in issues.issues.values() if isinstance(issue, UserStoryIssue)
        ]
        self._generate_index_page(self._us_index_no_struct_template_file, "user_stories", us_issues)
        logger.info("MDoc page generation - generated User Stories `_index.md`.")

        # Generate an index page with a summary table about all Features
        feat_issues: list[FeatureIssue] = [issue for issue in issues.issues.values() if isinstance(issue, FeatureIssue)]
        self._generate_index_page(self._feat_index_no_struct_template_file, "features", feat_issues)
        logger.info("MDoc page generation - generated Features `_index.md`.")

    def _generate_md_issue_page_for_us(self, issue: Issue) -> None:
        """
        Generates an MDoc page for a User Story ticket or GitHub issue from a template and saves
        it to the output directory.

        @param issue: The source Issue object containing the issue data.
        @return: None
        """
        # Initialize dictionary with replacements
        # TODO - add support for - planned in Issue https://github.com/AbsaOSS/living-doc-generator/issues/111
        #   - GH State badge
        #   - GH Project State badge
        #   - GH Priority
        #   - GH Icon link
        replacements = {
            "title": issue.title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issue_content": issue.body,
        }

        # Run through all replacements and update template keys with adequate content
        issue_md_page_content = self._us_issue_page_detail_template.format(**replacements)

        # Create a directory structure path for the issue page
        assert issue.repository_id is not None
        page_directory_path: str = self._generate_directory_path_us(self.PARENT_PATH_US, issue.repository_id)
        os.makedirs(page_directory_path, exist_ok=True)

        # Save the single issue MDoc page
        page_filename = self.generate_page_filename(issue)
        with open(os.path.join(page_directory_path, page_filename), "w", encoding="utf-8") as f:
            f.write(issue_md_page_content)

        logger.debug("Generated MDoc page: %s.", page_filename)

    def _generate_md_issue_page_for_feat(self, issue: Issue) -> None:
        """
        Generates an MDoc page for a Feature ticket/GH issue from a template and saves it to the output directory.

        @param issue: The source Issue object containing the issue data.
        @return: None
        """
        # Initialize dictionary with replacements
        # TODO - add support for - planned in Issue https://github.com/AbsaOSS/living-doc-generator/issues/111
        #   - GH State badge
        #   - GH Project State badge
        #   - GH Priority
        #   - GH Icon link

        replacements = {
            "title": issue.title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issue_content": issue.body,
        }

        # Run through all replacements and update template keys with adequate content
        issue_md_page_content = self._feat_issue_page_detail_template.format(**replacements)

        # Create a directory structure path for the issue page
        assert issue.repository_id is not None
        page_directory_path: str = self._generate_directory_path_feat(
            self.PARENT_PATH_FEAT, issue.repository_id, issue.title if issue.title else ""
        )
        os.makedirs(page_directory_path, exist_ok=True)

        # Save the single issue MDoc page
        page_filename = self.generate_page_filename(issue)
        with open(os.path.join(page_directory_path, page_filename), "w", encoding="utf-8") as f:
            f.write(issue_md_page_content)

        logger.debug("Generated MDoc page: %s.", page_filename)

    def _generate_md_issue_page_for_func(
        self, issue: FunctionalityIssue, feature_issue: Optional[FeatureIssue] = None
    ) -> None:
        """
        Generates an MDoc page for a Functionality ticket or GitHub issue from a template and saves
        it to the output directory.

        @param issue: The source Issue object containing the issue data.
        @param feature_issue: The FeatureIssue object associated with the FunctionalityIssue, if any.
        @return: None
        """
        # Initialize dictionary with replacements
        # TODO - add support for - planned in Issue https://github.com/AbsaOSS/living-doc-generator/issues/111
        #   - GH State badge
        #   - GH Project State badge
        #   - GH Priority
        #   - GH Icon link

        title = issue.title
        feature_title = feature_issue.title if feature_issue and feature_issue.title else "no_feature"

        replacements = {
            "title": title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issue_content": issue.body,
        }

        # Run through all replacements and update template keys with adequate content
        issue_md_page_content = self._func_issue_page_detail_template.format(**replacements)

        # Create a directory structure path for the issue page
        assert issue.repository_id is not None
        page_directory_path: str = self._generate_directory_path_func(
            self.PARENT_PATH_FEAT, issue.repository_id, feature_title
        )
        os.makedirs(page_directory_path, exist_ok=True)

        # Save the single issue MDoc page
        page_filename = self.generate_page_filename(issue)
        with open(os.path.join(page_directory_path, page_filename), "w", encoding="utf-8") as f:
            f.write(issue_md_page_content)

        logger.debug("Generated MDoc page: %s.", page_filename)

    def generate_page_filename(self, issue: Issue) -> str:
        """
        Generate a filename page naming based on the issue number and title.

        @return: The generated page filename.
        """
        title = issue.title if issue.title else ""
        if isinstance(issue, (UserStoryIssue, FunctionalityIssue)):
            md_filename_base = f"{issue.issue_number}_{title.lower()}.md"
            page_filename = sanitize_filename(md_filename_base)
        elif isinstance(issue, FeatureIssue):
            page_filename = "_index.md"
        else:
            page_filename = f"{issue.issue_number}.md"

        return page_filename

    # pylint: disable=too-many-arguments
    def _generate_structured_index_pages(self, issues: Issues, group_name: str) -> None:
        """
        Generates a set of index pages due to a structured output feature.

        @param issues: A dictionary containing all source issues.
        @return: None
        """
        # Group issues by repository for structured index page content
        issues_by_repository: dict[str, list[Issue]] = {}
        for issue in issues.issues.values():
            assert issue.repository_id is not None
            if issue.repository_id not in issues_by_repository:
                issues_by_repository[issue.repository_id] = []
            issues_by_repository[issue.repository_id].append(issue)

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

    def _generate_index_page(self, issue_index_page_template: str, group_name: str, issues: Sequence[T]) -> None:
        """
        Generates an index page that summarizes all issues and saves it to the output directory.

        @param issue_index_page_template: The template string for generating the index mdoc page.
        @param issues: A dictionary containing all source issues.
        @param repository_id: The repository ID used if the structured output is generated.
        @return: None
        """
        # Initializing the issue table header based on the project mining state
        issue_table = (
            TABLE_HEADER_WITH_PROJECT_DATA if self.project_statuses_included else TABLE_HEADER_WITHOUT_PROJECT_DATA
        )

        # Create an issue summary table for every issue
        for issue in issues:
            issue_table += self._generate_mdoc_line(issue)

        # Prepare issues replacement for the index page
        replacement = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issue_overview_table": issue_table,
        }

        if len(issues) > 0:
            repository_id = issues[0].repository_id
        else:
            logger.info("No source issues found for group: %s.", group_name)
            return

        if ActionInputs.is_structured_output_enabled():
            replacement["data_level_name"] = repository_id.split("/")[1]

        # Replace the issue placeholders in the index template
        index_page: str = issue_index_page_template.format(**replacement)

        # Generate a directory structure path for the index page
        # Note: repository_id is used only if the structured output is generated
        index_directory_path: str = self._generate_index_directory_path(group_name, repository_id)

        # Create an index page file
        with open(os.path.join(index_directory_path, "_index.md"), "w", encoding="utf-8") as f:
            f.write(index_page)

    def _generate_sub_level_index_page(self, index_template: str, repository_id: str, group_name) -> None:
        """
        Generates an index page for the structured output based on the level.

        @param index_template: The template string for generating the index MDoc page.
        @param repository_id: The repository ID of a repository that stores the issues.
        @return: None
        """
        replacement = {
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        organization_name = repository_id.split("/")[0]
        replacement["organization_name"] = organization_name

        # Replace the issue placeholders in the index template
        sub_level_index_page = index_template.format(**replacement)

        # Create a sub-index page file
        output_path = os.path.join(make_absolute_path(self._output_path), group_name, organization_name)
        os.makedirs(output_path, exist_ok=True)
        with open(os.path.join(output_path, "_index.md"), "w", encoding="utf-8") as f:
            f.write(sub_level_index_page)

    def _generate_mdoc_line(self, issue: Issue) -> str:
        """
        Generates an MDoc summary line for a single issue.

        @param issue: The source Issue object containing the issue data.
        @return: The MDoc line for the issue.
        """
        organization_name = issue.organization_name
        repository_name = issue.repository_name
        number = issue.issue_number
        title = issue.title
        title = title.replace("|", " _ ")
        issue_link_base = issue.title.replace(" ", "-").lower()
        issue_mdoc_link = f"features#{issue_link_base}"
        url = issue.html_url
        state = issue.state

        status_list = [project_status.status for project_status in issue.project_statuses]
        status = ", ".join(status_list) if status_list else "---"

        # Change the bool values to more user-friendly characters
        if self.project_statuses_included:
            if issue.linked_to_project:
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

    def _generate_issue_summary_table(self, issue: Issue) -> str:
        """
        Generates a string representation of feature info in a table format.

        @param issue: The source Issue object containing the issue data.
        @return: The string representation of the issue info in a table format.
        """
        # Join issue labels into one string
        issue_labels = issue.labels
        labels = ", ".join(issue_labels) if issue_labels else None

        # Format issue URL as an MDoc link
        issue_url_ = issue.html_url
        issue_url = f"<a href='{issue_url_}' target='_blank'>GitHub link</a> " if issue_url_ else None

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
            issue.organization_name,
            issue.repository_name,
            issue.issue_number,
            issue.title,
            issue.state.lower() if issue.state else None,
            issue_url,
            issue.created_at,
            issue.updated_at,
            issue.closed_at,
            labels,
        ]

        # Update the summary table based on the project data mining situation
        if self.project_statuses_included:
            project_statuses = issue.project_statuses

            if issue.linked_to_project:
                project_data_header = [
                    "Project title",
                    "Status",
                    "Priority",
                    "Size",
                    "MoSCoW",
                ]

                for project_status in project_statuses:
                    # Update the summary data table for every project attached to the repository issue
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
        Generates a directory path based on whether structured output is required.

        @param repository_id: The repository ID.
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
        project_root = Path(__file__).resolve().parent.parent
        templates_base_path = os.path.join(project_root, "templates")

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

        _us_issue_page_detail_template: Optional[str] = load_template(
            us_issue_detail_page_template,
            "User Story detail page template file was not successfully loaded.",
        )
        _feat_issue_page_detail_template: Optional[str] = load_template(
            feat_issue_detail_page_template,
            "Feature detail page template file was not successfully loaded.",
        )
        _func_issue_page_detail_template: Optional[str] = load_template(
            func_issue_detail_page_template,
            "Functionality detail page template file was not successfully loaded.",
        )

        _us_index_no_struct_template_file: Optional[str] = load_template(
            us_index_no_struct_template_file,
            "User Story index page template file was not successfully loaded.",
        )
        _feat_index_no_struct_template_file: Optional[str] = load_template(
            feat_index_no_struct_template_file,
            "Feature index page template file was not successfully loaded.",
        )
        _us_index_root_level_template_page: Optional[str] = load_template(
            us_index_root_level_template_file,
            "Structured User Story index page template file for root level was not successfully loaded.",
        )
        _feat_index_root_level_template_page: Optional[str] = load_template(
            feat_index_root_level_template_file,
            "Structured Feature index page template file for root level was not successfully loaded.",
        )
        _index_org_level_template_file = load_template(
            index_org_level_template_file,
            "Structured index page template file for organization level was not successfully loaded.",
        )

        _report_page_template: Optional[str] = load_template(
            report_page_template_file,
            "Report page template file was not successfully loaded.",
        )

        if (
            _us_issue_page_detail_template is None
            or _feat_issue_page_detail_template is None
            or _func_issue_page_detail_template is None
            or _us_index_no_struct_template_file is None
            or _feat_index_no_struct_template_file is None
            or _us_index_root_level_template_page is None
            or _feat_index_root_level_template_page is None
            or _index_org_level_template_file is None
            or _report_page_template is None
        ):
            logger.error("MDoc page generation - failed to load all templates.")
            return False

        self._us_issue_page_detail_template = _us_issue_page_detail_template
        self._feat_issue_page_detail_template = _feat_issue_page_detail_template
        self._func_issue_page_detail_template = _func_issue_page_detail_template
        self._us_index_no_struct_template_file = _us_index_no_struct_template_file
        self._feat_index_no_struct_template_file = _feat_index_no_struct_template_file
        self._us_index_root_level_template_page = _us_index_root_level_template_page
        self._feat_index_root_level_template_page = _feat_index_root_level_template_page
        self._index_org_level_template = _index_org_level_template_file
        self._report_page_template = _report_page_template

        return True

    def _update_error_page(self, issue: Issue, group: str) -> None:
        if ActionInputs.is_report_page_generation_enabled() and issue.errors:
            keys = self._report_page_content.keys()
            if group not in keys:
                self._report_page_content[group] = REPORT_PAGE_HEADER

            repository_id: str = issue.repository_id
            number: int = issue.issue_number
            if issue.html_url is None:
                html_url: str = f"https://github.com/{repository_id}/issues/{number}"
            else:
                html_url = issue.html_url

            for error_type, error_message in issue.errors.items():
                self._report_page_content[
                    group
                ] += f"| {error_type} | [{repository_id}#{number}]({html_url}) | {error_message} |\n"

    def _generate_directory_path_us(self, parent_path: str, repository_id: str) -> str:
        """
        Generate a list of directory paths based on enabled features.

        @return: The list of generated directory paths.
        """
        # If structured output is enabled, create a directory path based on the repository
        if ActionInputs.is_structured_output_enabled() and repository_id:
            organization_name, repository_name = repository_id.split("/")
            output_path = os.path.join(self._output_path, parent_path, organization_name, repository_name)
        else:
            # If structured output is not enabled, create a directory path based on the parent path
            output_path = os.path.join(self._output_path, parent_path)

        return output_path

    def _generate_directory_path_feat(self, parent_path: str, repository_id: str, feature_title: str) -> str:
        """
        Generate a list of directory paths based on enabled features.

        @return: The list of generated directory paths.
        """
        # If structured output is enabled, create a directory path based on the repository
        if ActionInputs.is_structured_output_enabled() and repository_id:
            organization_name, repository_name = repository_id.split("/")
            output_path = os.path.join(
                self._output_path, parent_path, organization_name, repository_name, feature_title
            )
        else:
            # If structured output is not enabled, create a directory path based on the parent path
            output_path = os.path.join(self._output_path, parent_path, feature_title)

        return output_path

    def _generate_directory_path_func(self, parent_path: str, repository_id: str, feature_title: str) -> str:
        """
        Generate a list of directory paths based on enabled features.

        @return: The list of generated directory paths.
        """
        # If structured output is enabled, create a directory path based on the repository
        if ActionInputs.is_structured_output_enabled() and repository_id:
            organization_name, repository_name = repository_id.split("/")
            output_path = os.path.join(
                self._output_path, parent_path, organization_name, repository_name, feature_title
            )
        else:
            # If structured output is not enabled, create a directory path based on the parent path
            output_path = os.path.join(self._output_path, parent_path, feature_title)

        return output_path
