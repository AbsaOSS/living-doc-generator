import logging
import os
import shutil

from datetime import datetime

from github import Github, Auth
from github.Issue import Issue


from living_documentation_generator.github_projects import GithubProjects
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

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    ISSUE_PAGE_TEMPLATE_FILE = os.path.join(
        PROJECT_ROOT, "..", "templates", "issue_detail_page_template.md"
    )
    INDEX_PAGE_TEMPLATE_FILE = os.path.join(
        PROJECT_ROOT, "..", "templates", "_index_page_template.md"
    )

    def __init__(
        self,
        github_token: str,
        repositories: list[ConfigRepository],
        project_state_mining_enabled: bool,
        output_path: str,
    ):

        self.github_instance = Github(
            auth=Auth.Token(token=github_token), per_page=ISSUES_PER_PAGE_LIMIT
        )
        self.github_projects_instance = GithubProjects(token=github_token)
        self.rate_limiter = GithubRateLimiter(self.github_instance)
        self.safe_call = safe_call_decorator(self.rate_limiter)

        # data
        self.__repositories: list[ConfigRepository] = repositories

        # features control
        self.__project_state_mining_enabled: bool = project_state_mining_enabled

        # paths
        self.__output_path: str = output_path

    @property
    def repositories(self) -> list[ConfigRepository]:
        return self.__repositories

    @property
    def project_state_mining_enabled(self) -> bool:
        return self.__project_state_mining_enabled

    @property
    def output_path(self) -> str:
        return self.__output_path

    def generate(self):
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

        # Consolidate all issues data together
        logger.info("Issue and project data consolidation - started.")
        projects_issues = self._consolidate_issues_data(
            repository_issues, project_issues
        )
        logger.info("Issue and project data consolidation - finished.")

        # Generate markdown pages
        logger.info("Markdown page generation - started.")
        self._generate_markdown_pages(projects_issues)
        logger.info("Markdown page generation - finished.")

    def _clean_output_directory(self):
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)
        os.makedirs(self.output_path)

    def _fetch_github_issues(self) -> dict[str, list[Issue]]:
        issues = {}
        total_issues_number = 0

        # Mine issues from every config repository
        for config_repository in self.repositories:
            repository_id = f"{config_repository.organization_name}/{config_repository.repository_name}"

            repository = self.safe_call(self.github_instance.get_repo)(repository_id)
            if repository is None:
                return {}

            logger.info(
                "Fetching repository GitHub issues - from `%s`.", repository.full_name
            )

            # Load all issues from one repository (unique for each repository) and save it under repository id
            if not config_repository.query_labels:
                logger.debug("Fetching all issues in the repository")
                issues[repository_id] = self.safe_call(repository.get_issues)(
                    state=ISSUE_STATE_ALL
                )
                amount_of_issues_per_repo = len(issues[repository_id])
                logger.debug(
                    "Fetched `%s` repository issues (%s)`.",
                    amount_of_issues_per_repo,
                    repository.full_name,
                )
            else:
                issues[repository_id] = []
                logger.debug(
                    "Labels to be fetched from: %s.", config_repository.query_labels
                )
                for label in config_repository.query_labels:
                    logger.debug("Fetching issues with label `%s`.", label)
                    issues[repository_id].extend(
                        self.safe_call(repository.get_issues)(
                            state=ISSUE_STATE_ALL, labels=[label]
                        )
                    )
                amount_of_issues_per_repo = len(issues[repository_id])

            # Accumulate the count of issues
            total_issues_number += amount_of_issues_per_repo
            logger.info(
                "Fetching repository GitHub issues - fetched `%s` repository issues (%s).",
                amount_of_issues_per_repo,
                repository.full_name,
            )

        logger.info(
            "Fetching repository GitHub issues - loaded `%s` repository issues in total.",
            total_issues_number,
        )
        return issues

    def _fetch_github_project_issues(self) -> dict[str, ProjectIssue]:
        if not self.project_state_mining_enabled:
            logger.info("Fetching GitHub project data - project mining is not allowed.")
            return {}

        logger.debug("Project data mining allowed.")

        # Mine project issues for every repository
        all_project_issues: dict[str, ProjectIssue] = {}

        for config_repository in self.repositories:
            repository_id = f"{config_repository.organization_name}/{config_repository.repository_name}"
            projects_title_filter = config_repository.projects_title_filter
            logger.debug(
                "Filtering projects: %s. If filter is empty, fetching all.",
                projects_title_filter,
            )

            repository = self.safe_call(self.github_instance.get_repo)(repository_id)
            if repository is None:
                return {}

            # Fetch all projects_buffer attached to the repository
            logger.info(
                "Fetching GitHub project data - looking for repository `%s` projects.",
                repository_id,
            )
            projects = self.safe_call(
                self.github_projects_instance.get_repository_projects
            )(repository=repository, projects_title_filter=projects_title_filter)

            # Update every project with project issue related data
            for project in projects:
                logger.info("Fetching GitHub project data - from `%s`.", project.title)
                project_issues: list[ProjectIssue] = self.safe_call(
                    self.github_projects_instance.get_project_issues
                )(project=project)

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
                consolidated_issue.update_with_project_data(
                    projects_issues[key].project_status
                )

        logging.info(
            "Issue and project data consolidation - consolidated `%s` repository issues"
            " with extra project data.",
            len(consolidated_issues),
        )
        return consolidated_issues

    def _generate_markdown_pages(self, issues: dict[str, ConsolidatedIssue]):
        with open(
            LivingDocumentationGenerator.ISSUE_PAGE_TEMPLATE_FILE, "r", encoding="utf-8"
        ) as f:
            issue_page_detail_template = f.read()

        with open(
            LivingDocumentationGenerator.INDEX_PAGE_TEMPLATE_FILE, "r", encoding="utf-8"
        ) as f:
            issue_index_page_template = f.read()

        for consolidated_issue in issues.values():
            self._generate_md_issue_page(issue_page_detail_template, consolidated_issue)
        logger.info(
            "Markdown page generation - generated `%s` issue pages.", len(issues)
        )

        self._generate_index_page(issue_index_page_template, issues)

    def _generate_md_issue_page(
        self, issue_page_template: str, consolidated_issue: ConsolidatedIssue
    ) -> None:
        """
        Generates a single issue Markdown page from a template and save to the output directory.

        @param issue_page_template: The template string for generating a single issue page.
        @param consolidated_issue: The dictionary containing issue data.
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
        with open(
            os.path.join(self.output_path, page_filename), "w", encoding="utf-8"
        ) as f:
            f.write(issue_md_page_content)

        logger.debug("Generated Markdown page: %s.", page_filename)

    def _generate_index_page(
        self,
        issue_index_page_template: str,
        consolidated_issues: dict[str, ConsolidatedIssue],
    ) -> None:
        """
        Generates an index page with a summary of all issues and save it to the output directory.

        :param issue_index_page_template: The template string for generating the index page.
        :param consolidated_issues: The dictionary containing all issues data.
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
        with open(
            os.path.join(self.output_path, "_index.md"), "w", encoding="utf-8"
        ) as f:
            f.write(index_page)

        logger.info("Markdown page generation - generated `_index.md`.")

    def _generate_markdown_line(self, consolidated_issue: ConsolidatedIssue) -> str:
        """
        Generates a markdown summary line for a given feature.

        @param consolidated_issue: The dictionary containing feature data.

        @return: A string representing the markdown line for the feature.
        """

        # Extract issue details from the consolidated issue object
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

    def _generate_issue_summary_table(
        self, consolidated_issue: ConsolidatedIssue
    ) -> str:
        """
        Generates a string representation of feature info in a table format.

        @param consolidated_issue: The dictionary containing feature data.

        @return: A string representing the feature information in a table format.
        """
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
                headers.extend(
                    ["Project title", "Status", "Priority", "Size", "MoSCoW"]
                )

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
                linked_to_project = (
                    LINKED_TO_PROJECT_TRUE
                    if consolidated_issue.linked_to_project
                    else LINKED_TO_PROJECT_FALSE
                )
                values.append(linked_to_project)

        # Initialize the Markdown table
        issue_info = "| Attribute | Content |\n|---|---|\n"

        # Add together all the attributes from the summary table in Markdown format
        for attribute, content in zip(headers, values):
            issue_info += f"| {attribute} | {content} |\n"

        return issue_info
