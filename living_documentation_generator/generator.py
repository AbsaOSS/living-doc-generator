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
This module contains the LivingDocumentationGenerator class which is responsible for generating
the Living Documentation output.

The class uses several helper methods to fetch required data from GitHub, consolidate the data
and generate the markdown pages as the output of Living Documentation action.
"""

import logging
import os
import shutil

from datetime import datetime

from github import Github, Auth
from github.Issue import Issue


from living_documentation_generator.github_projects import GithubProjects
from living_documentation_generator.model.github_project import GithubProject
from living_documentation_generator.model.config_repository import ConfigRepository
from living_documentation_generator.model.consolidated_issue import ConsolidatedIssue
from living_documentation_generator.model.project_issue import ProjectIssue
from living_documentation_generator.utils.decorators import safe_call_decorator
from living_documentation_generator.utils.github_rate_limiter import GithubRateLimiter
from living_documentation_generator.utils.utils import make_issue_key
from living_documentation_generator.utils.constants import (
    ISSUES_PER_PAGE_LIMIT,
    ISSUE_STATE_ALL,
    LINKED_TO_PROJECT_TRUE,
    LINKED_TO_PROJECT_FALSE,
)

logger = logging.getLogger(__name__)


class LivingDocumentationGenerator:
    """
    A class representing the Living Documentation Generator.

    Attributes:
        __github_instance (GitHub): The GitHub instance used for authentication and requests.
        __github_projects_instance (GithubProjects): The GithubProjects instance used for project related operations.
        __rate_limiter (GithubRateLimiter): The rate limiter used to control the rate of API calls.
        __repositories (list[ConfigRepository]): List of config repositories to fetch from.
        __project_state_mining_enabled (bool): Switch indicating if project state mining is enabled.
        __output_path (str): The directory where the markdown pages will be stored.
    """

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    ISSUE_PAGE_TEMPLATE_FILE = os.path.join(PROJECT_ROOT, "..", "templates", "issue_detail_page_template.md")
    INDEX_PAGE_TEMPLATE_FILE = os.path.join(PROJECT_ROOT, "..", "templates", "_index_page_template.md")

    def __init__(
            self,
            github_token: str,
            repositories: list[ConfigRepository],
            project_state_mining_enabled: bool,
            output_path: str,
    ):

        self.__github_instance = Github(auth=Auth.Token(token=github_token), per_page=ISSUES_PER_PAGE_LIMIT)
        self.__github_projects_instance = GithubProjects(token=github_token)
        self.__rate_limiter = GithubRateLimiter(self.__github_instance)
        self.__safe_call = safe_call_decorator(self.__rate_limiter)

        # data
        self.__repositories: list[ConfigRepository] = repositories

        # features control
        self.__project_state_mining_enabled: bool = project_state_mining_enabled

        # paths
        self.__output_path: str = output_path

    @property
    def github_instance(self) -> Github:
        """Getter of the GitHub instance."""
        return self.__github_instance

    @property
    def repositories(self) -> list[ConfigRepository]:
        """Getter of the list of config repositories objects to fetch from."""
        return self.__repositories

    @property
    def project_state_mining_enabled(self) -> bool:
        """Getter of the project state mining switch."""
        return self.__project_state_mining_enabled

    @property
    def output_path(self) -> str:
        """Getter of the output directory."""
        return self.__output_path

    def generate(self) -> None:
        """Generate the Living Documentation markdown pages output."""
        self._clean_output_directory()
        logger.debug("Output directory cleaned.")

        # Data mine GitHub issues with defined labels from all repositories
        logger.info("Fetching repository GitHub issues - started.")
        repository_issues: dict[str, list[Issue]] = self._fetch_github_issues()
        # Note: got dict of list of issues for each repository (key is repository id)
        logger.info("Fetching repository GitHub issues - finished.")

        # Data mine GitHub project's issues
        logger.info("Fetching GitHub project data - started.")
        project_issues: dict[str, ProjectIssue] = self._fetch_github_project_issues()
        # Note: got dict of project issues with unique string key defying the issue
        logger.info("Fetching GitHub project data - finished.")

        # Consolidate all issue data together
        logger.info("Issue and project data consolidation - started.")
        consolidated_issues = self._consolidate_issues_data(repository_issues, project_issues)
        logger.info("Issue and project data consolidation - finished.")

        # Generate markdown pages
        logger.info("Markdown page generation - started.")
        self._generate_markdown_pages(consolidated_issues)
        logger.info("Markdown page generation - finished.")

    def _clean_output_directory(self) -> None:
        """Clean the output directory from the previous run."""
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)
        os.makedirs(self.output_path)

    def _fetch_github_issues(self) -> dict[str, list[Issue]]:
        """
        Fetch GitHub repository issues using the GitHub library. Only issues with correct labels are fetched,
        if no labels are defined in the configuration, all repository issues are fetched.
        """
        issues = {}
        total_issues_number = 0

        # Run the fetching logic for every config repository
        for config_repository in self.repositories:
            repository_id = f"{config_repository.organization_name}/{config_repository.repository_name}"

            repository = self.__safe_call(self.github_instance.get_repo)(repository_id)
            if repository is None:
                return {}

            logger.info("Fetching repository GitHub issues - from `%s`.", repository.full_name)

            # If the query labels are not defined, fetch all issues from the repository
            if not config_repository.query_labels:
                logger.debug("Fetching all issues in the repository")
                issues[repository_id] = self.__safe_call(repository.get_issues)(state=ISSUE_STATE_ALL)
                amount_of_issues_per_repo = len(issues[repository_id])
                logger.debug(
                    "Fetched `%s` repository issues (%s)`.",
                    amount_of_issues_per_repo, repository.full_name,
                )
            else:
                # Fetch only issues with required labels from configuration
                issues[repository_id] = []
                logger.debug("Labels to be fetched from: %s.", config_repository.query_labels)
                for label in config_repository.query_labels:
                    logger.debug("Fetching issues with label `%s`.", label)
                    issues[repository_id].extend(
                        self.__safe_call(repository.get_issues)(state=ISSUE_STATE_ALL, labels=[label])
                    )
                amount_of_issues_per_repo = len(issues[repository_id])

            # Accumulate the count of issues
            total_issues_number += amount_of_issues_per_repo
            logger.info(
                "Fetching repository GitHub issues - fetched `%s` repository issues (%s).",
                amount_of_issues_per_repo, repository.full_name,
            )

        logger.info(
            "Fetching repository GitHub issues - loaded `%s` repository issues in total.",
            total_issues_number,
        )
        return issues

    def _fetch_github_project_issues(self) -> dict[str, ProjectIssue]:
        """Fetch GitHub project issues using the GraphQL API."""
        if not self.project_state_mining_enabled:
            logger.info("Fetching GitHub project data - project mining is not allowed.")
            return {}

        logger.debug("Project data mining allowed.")

        # Mine project issues for every repository
        all_project_issues: dict[str, ProjectIssue] = {}

        for config_repository in self.repositories:
            repository_id = f"{config_repository.organization_name}/{config_repository.repository_name}"
            projects_title_filter = config_repository.projects_title_filter
            logger.debug("Filtering projects: %s. If filter is empty, fetching all.", projects_title_filter)

            repository = self.__safe_call(self.github_instance.get_repo)(repository_id)
            if repository is None:
                return {}

            # Fetch all projects_buffer attached to the repository
            logger.info("Fetching GitHub project data - looking for repository `%s` projects.", repository_id)
            projects: list[GithubProject] = self.__safe_call(
                self.__github_projects_instance.get_repository_projects)(
                repository=repository,
                projects_title_filter=projects_title_filter,
            )

            # Update every project with project issue related data
            for project in projects:
                logger.info("Fetching GitHub project data - from `%s`.", project.title)
                project_issues: list[ProjectIssue] = self.__safe_call(
                    self.__github_projects_instance.get_project_issues)(
                    project=project,
                )

                for project_issue in project_issues:
                    key = make_issue_key(
                        project_issue.organization_name,
                        project_issue.repository_name,
                        project_issue.number,
                    )
                    all_project_issues[key] = project_issue
                logger.info(
                    "Fetching GitHub project data - fetched project data (%s).",
                    project.title,
                )

        return all_project_issues

    @staticmethod
    def _consolidate_issues_data(
        repository_issues: dict[str, list[Issue]],
        projects_issues: dict[str, ProjectIssue],
    ) -> dict[str, ConsolidatedIssue]:
        """
        Consolidate the fetched issues and extra project data into a one consolidated object.

        Args:
            repository_issues (dict): A dictionary containing repository issue objects with unique key.
            projects_issues (dict): A dictionary containing project issue objects with unique key.
        """

        consolidated_issues = {}

        # Create a ConsolidatedIssue object for each repository issue
        for repository_id in repository_issues.keys():
            for repository_issue in repository_issues[repository_id]:
                repo_id_parts = repository_id.split("/")
                unique_key = make_issue_key(
                    repo_id_parts[0], repo_id_parts[1], repository_issue.number
                )
                consolidated_issues[unique_key] = ConsolidatedIssue(
                    repository_id=repository_id, repository_issue=repository_issue
                )

        # Update consolidated issue structures with project data
        logger.debug("Updating consolidated issue structure with project data.")
        for key, consolidated_issue in consolidated_issues.items():
            if key in projects_issues:
                consolidated_issue.update_with_project_data(projects_issues[key].project_status)

        logging.info(
            "Issue and project data consolidation - consolidated `%s` repository issues"
            " with extra project data.",
            len(consolidated_issues),
        )
        return consolidated_issues

    def _generate_markdown_pages(self, issues: dict[str, ConsolidatedIssue]) -> None:
        """
        Generate the Markdown pages for all consolidated issues, create a summary index page and
        save it all to the output directory.

        Args:
            issues (dict): A dictionary containing all consolidated issues.
        """
        with open(LivingDocumentationGenerator.ISSUE_PAGE_TEMPLATE_FILE, "r", encoding="utf-8") as f:
            issue_page_detail_template = f.read()

        with open(LivingDocumentationGenerator.INDEX_PAGE_TEMPLATE_FILE, "r", encoding="utf-8") as f:
            issue_index_page_template = f.read()

        # Generate a markdown page for every issue
        for consolidated_issue in issues.values():
            self._generate_md_issue_page(issue_page_detail_template, consolidated_issue)
        logger.info("Markdown page generation - generated `%s` issue pages.", len(issues))

        # Generate an index page with a summary table about all issues
        self._generate_index_page(issue_index_page_template, issues)

    def _generate_md_issue_page(self, issue_page_template: str, consolidated_issue: ConsolidatedIssue) -> None:
        """
        Generates a single issue Markdown page from a template and save to the output directory.

        Args:
            issue_page_template (str): The template string for generating the single markdown issue page.
            consolidated_issue (ConsolidatedIssue): The ConsolidatedIssue object containing the issue data.
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
        issue_md_page_content = issue_page_template.format(**replacements)

        # Save the single issue Markdown page
        page_filename = consolidated_issue.generate_page_filename()
        with open(os.path.join(self.output_path, page_filename), "w", encoding="utf-8") as f:
            f.write(issue_md_page_content)

        logger.debug("Generated Markdown page: %s.", page_filename)

    def _generate_index_page(
            self,
            issue_index_page_template: str,
            consolidated_issues: dict[str, ConsolidatedIssue],
    ) -> None:
        """
        Generates an index page with a summary of all issues and save it to the output directory.

        Args:
            issue_index_page_template (str): The template string for generating the index markdown page.
            consolidated_issues (dict): A dictionary containing all consolidated issues.
        """

        # Initializing the issue table header based on the project mining state
        if self.__project_state_mining_enabled:
            issue_table = (
                "| Organization name | Repository name | Issue 'Number - Title' |"
                " Linked to project | Project status | Issue URL |\n"
                "|-------------------|-----------------|------------------------|"
                "-------------------|----------------|-----------|\n"
            )
        else:
            issue_table = """| Organization name | Repository name | Issue 'Number - Title' | Issue state | Issue URL |
                             |-------------------|-----------------|------------------------|-------------|-----------|
                          """

        # Create an issue summary table for every issue
        for consolidated_issue in consolidated_issues.values():
            issue_table += self._generate_markdown_line(consolidated_issue)

        # Prepare issues replacement for the index page
        replacement = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issues": issue_table,
        }

        # Replace the issue placeholders in the index template
        index_page = issue_index_page_template.format(**replacement)

        # Create an index page file
        with open(os.path.join(self.output_path, "_index.md"), "w", encoding="utf-8") as f:
            f.write(index_page)

        logger.info("Markdown page generation - generated `_index.md`.")

    def _generate_markdown_line(self, consolidated_issue: ConsolidatedIssue) -> str:
        """Generates a markdown summary line for a single issue."""
        organization_name = consolidated_issue.organization_name
        repository_name = consolidated_issue.repository_name
        number = consolidated_issue.number
        title = consolidated_issue.title
        title = title.replace("|", " _ ")
        page_filename = consolidated_issue.generate_page_filename()
        status = consolidated_issue.project_status.status
        url = consolidated_issue.html_url
        state = consolidated_issue.state

        # Change the bool values to more user-friendly characters
        if self.__project_state_mining_enabled:
            if consolidated_issue.linked_to_project:
                linked_to_project = LINKED_TO_PROJECT_TRUE
            else:
                linked_to_project = LINKED_TO_PROJECT_FALSE

            # Generate the Markdown issue line WITH extra project data
            md_issue_line = (
                f"|{organization_name} | {repository_name} | [#{number} - {title}]({page_filename}) |"
                f" {linked_to_project} | {status} |[GitHub link]({url}) |\n"
            )
        else:
            # Generate the Markdown issue line WITHOUT project data
            md_issue_line = (
                f"|{organization_name} | {repository_name} | [#{number} - {title}]({page_filename}) |"
                f" {state} |[GitHub link]({url}) |\n"
            )

        return md_issue_line

    def _generate_issue_summary_table(self, consolidated_issue: ConsolidatedIssue) -> str:
        """Generates a string representation of feature info in a table format."""
        # Join issue labels into one string
        labels = consolidated_issue.labels
        labels = ", ".join(labels) if labels else None

        # Format issue URL as a Markdown link
        issue_url = consolidated_issue.html_url
        issue_url = f"[GitHub link]({issue_url})" if issue_url else None

        # Define the header for the issue summary table
        headers = [
            "Organization name",
            "Repository name",
            "Issue number",
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
            consolidated_issue.state.lower(),
            issue_url,
            consolidated_issue.created_at,
            consolidated_issue.updated_at,
            consolidated_issue.closed_at,
            labels,
        ]

        # Update the summary table, based on the project data mining situation
        if self.__project_state_mining_enabled:
            project_status = consolidated_issue.project_status

            if consolidated_issue.linked_to_project:
                headers.extend(["Project title", "Status", "Priority", "Size", "MoSCoW"])

                values.extend(
                    [
                        project_status.project_title,
                        project_status.status,
                        project_status.priority,
                        project_status.size,
                        project_status.moscow,
                    ]
                )
            else:
                headers.append("Linked to project")
                linked_to_project = (LINKED_TO_PROJECT_TRUE
                                     if consolidated_issue.linked_to_project
                                     else LINKED_TO_PROJECT_FALSE)
                values.append(linked_to_project)

        # Initialize the Markdown table
        issue_info = "| Attribute | Content |\n|---|---|\n"

        # Add together all the attributes from the summary table in Markdown format
        for attribute, content in zip(headers, values):
            issue_info += f"| {attribute} | {content} |\n"

        return issue_info
