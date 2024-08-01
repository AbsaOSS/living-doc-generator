import logging
import os
import shutil

from datetime import datetime

from github import Github
from github.Issue import Issue

from living_documentation_generator.github_projects import GithubProjects
from living_documentation_generator.model.config_repository import ConfigRepository
from living_documentation_generator.model.consolidated_issue import ConsolidatedIssue
from living_documentation_generator.model.project_issue import ProjectIssue
from living_documentation_generator.utils.constants import Constants
from living_documentation_generator.utils.decorators import safe_call_decorator
from living_documentation_generator.utils.github_rate_limiter import GithubRateLimiter
from living_documentation_generator.utils.utils import make_issue_key

logger = logging.getLogger(__name__)


class LivingDocumentationGenerator:

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    ISSUE_PAGE_TEMPLATE_FILE = os.path.join(PROJECT_ROOT, "..", "templates", "issue_detail_page_template.md")
    INDEX_PAGE_TEMPLATE_FILE = os.path.join(PROJECT_ROOT, "..", "templates", "_index_page_template.md")

    def __init__(self, github_instance: Github, github_projects_instance: GithubProjects,
                 repositories: list[ConfigRepository], projects_title_filter: list[str],
                 project_state_mining_enabled: bool, output_path: str):

        self.github_instance = github_instance
        self.github_projects_instance = github_projects_instance
        self.rate_limiter = GithubRateLimiter(self.github_instance)
        self.safe_call = safe_call_decorator(self.rate_limiter)

        # data
        self.__repositories: list[ConfigRepository] = repositories
        self.__projects_title_filter: list[str] = projects_title_filter      # TODO - this could be part of repository config ???

        # features control
        self.__project_state_mining_enabled: bool = project_state_mining_enabled

        # paths
        self.__output_path: str = output_path

    @property
    def repositories(self) -> list[ConfigRepository]:
        return self.__repositories

    @property
    def projects_title_filter(self) -> list[str]:
        return self.__projects_title_filter

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
        logger.info("Starting: Fetching repository GitHub issues.")
        repository_issues: dict[str, list[Issue]] = self._fetch_github_issues()
        # Note: got dict of list of issues for each repository (key is repository id)
        logger.info("Finished: Fetching repository GitHub issues.")

        # Data mine GitHub project's issues
        logger.info("Starting: Fetching GitHub project issue data.")
        project_issues: dict[str, ProjectIssue] = self._fetch_github_project_issues()
        # Note: got dict of project issues with unique string key defying the issue
        logger.info("Finished: Fetching GitHub project issue data.")

        # Consolidate all issues data together
        logger.info("Starting: Issue data consolidation.")
        projects_issues = self._consolidate_issues_data(repository_issues, project_issues)
        logger.info("Finished: Issue data consolidation.")

        # Generate markdown pages
        logger.info("Starting: Markdown pages generation.")
        self._generate_markdown_pages(projects_issues)
        logger.info("Finished: Markdown pages generation.")

    def _clean_output_directory(self):
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)
        os.makedirs(self.output_path)

    def _fetch_github_issues(self) -> dict[str, list[Issue]]:
        issues = {}

        # Mine issues from every config repository
        for config_repository in self.repositories:
            repository_id = f"{config_repository.owner}/{config_repository.name}"

            repository = self.safe_call(self.github_instance.get_repo)(repository_id)
            if repository is None:
                return {}

            logger.info("Fetching repository issues for `%s`.", repository.full_name)

            # Load all issues from one repository (unique for each repository) and save it under repository id
            if not config_repository.query_labels:
                logger.info("Fetching all issues in the repository")
                issues[repository_id] = self.safe_call(repository.get_issues)(state=Constants.ISSUE_STATE_ALL)
                logger.info("Loaded `%s` repository issues.", len(issues[repository_id]))
            else:
                issues[repository_id] = []
                for label in config_repository.query_labels:
                    logger.info("Fetching issues with label: `%s`.", label)
                    issues[repository_id].extend(self.safe_call(repository.get_issues)(state=Constants.ISSUE_STATE_ALL,
                                                                                       labels=[label]))
                logger.info("Loaded `%s` repository issues.", len(issues[repository_id]))

        return issues

    def _fetch_github_project_issues(self) -> dict[str, ProjectIssue]:
        if not self.project_state_mining_enabled:
            logger.info("Project data mining is not allowed.")
            return {}

        logger.debug("Project data mining allowed.")

        # Mine project issues for every repository
        all_project_issues: dict[str, ProjectIssue] = {}

        for config_repository in self.repositories:
            repository_id = f"{config_repository.owner}/{config_repository.name}"

            repository = self.safe_call(self.github_instance.get_repo)(repository_id)
            if repository is None:
                return {}

            # Fetch all projects_buffer attached to the repository
            projects = self.safe_call(self.github_projects_instance.get_repository_projects)(
                repository=repository, projects_title_filter=self.projects_title_filter)

            # Update every project with project issue related data
            for project in projects:
                logger.info("Fetching project issues for `%s`.", project.title)
                project_issues: list[ProjectIssue] = self.safe_call(self.github_projects_instance.get_project_issues)(project=project)
                for project_issue in project_issues:
                    key = make_issue_key(project_issue.organization_name, project_issue.repository_name,
                                         project_issue.number)
                    all_project_issues[key] = project_issue

        return all_project_issues

    def _consolidate_issues_data(self, repository_issues: dict[str, list[Issue]],
                                 projects_issues: dict[str, ProjectIssue]) -> dict[str, ConsolidatedIssue]:

        consolidated_issues = {}

        # Create a ConsolidatedIssue object for each repository issue
        for repository_id in repository_issues.keys():
            for repository_issue in repository_issues[repository_id]:
                repo_id_parts = repository_id.split("/")
                unique_key = make_issue_key(repo_id_parts[0], repo_id_parts[1], repository_issue.number)
                consolidated_issues[unique_key] = ConsolidatedIssue(repository_id=repository_id,
                                                                    repository_issue=repository_issue)
                if not self.project_state_mining_enabled:
                    logger.debug("Updating consolidated issues with project data is not allowed information.")
                    consolidated_issues[unique_key].no_project_mining()

        # Update issues with project data
        logger.debug("Updating consolidated issue structure with project data.")
        for key in consolidated_issues.keys():
            if key in projects_issues:
                consolidated_issues[key].update_with_project_data(projects_issues[key])

        return consolidated_issues

    def _generate_markdown_pages(self, issues: dict[str, ConsolidatedIssue]):
        with open(LivingDocumentationGenerator.ISSUE_PAGE_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            issue_page_detail_template = f.read()

        with open(LivingDocumentationGenerator.INDEX_PAGE_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            issue_index_page_template = f.read()

        for key, consolidated_issue in issues.items():
            self._generate_md_issue_page(issue_page_detail_template, consolidated_issue)

        self._generate_index_page(issue_index_page_template, issues)

    def _generate_md_issue_page(self, issue_page_template: str, consolidated_issue: ConsolidatedIssue) -> None:
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
            "issue_content": issue_content
        }

        # Run through all replacements and update template keys with adequate content
        issue_md_page_content = issue_page_template.format(**replacements)

        # Save the single issue Markdown page
        page_filename = consolidated_issue.generate_page_filename()
        with open(os.path.join(self.output_path, page_filename), 'w', encoding='utf-8') as f:
            f.write(issue_md_page_content)

        logger.info("Generated: %s.", page_filename)

    def _generate_index_page(self, issue_index_page_template: str, consolidated_issues: dict[str, ConsolidatedIssue]) -> None:
        """
        Generates an index page with a summary of all issues and save it to the output directory.

        :param issue_index_page_template: The template string for generating the index page.
        :param consolidated_issues: The dictionary containing all issues data.
        """

        issue_table = """| Organization name     | Repository name | Issue 'Number - Title'  | Linked to project | Project status  |Issue URL   |
               |-----------------------|-----------------|---------------------------|---------|------|-----|
               """

        # Create an issue summary table for every issue
        for key, consolidated_issue in consolidated_issues.items():
            issue_table += self._generate_markdown_line(consolidated_issue)

        # Prepare issues replacement for the index page
        replacement = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issues": issue_table
        }

        # Replace the issue placeholders in the index template
        index_page = issue_index_page_template.format(**replacement)

        # Create an index page file
        with open(os.path.join(self.output_path, "_index.md"), 'w', encoding='utf-8') as f:
            f.write(index_page)

        logger.info("Generated: _index.md.")

    def _generate_markdown_line(self, consolidated_issue) -> str:
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
        status = consolidated_issue.status
        url = consolidated_issue.url

        # Change the bool values to more user-friendly characters
        if self.__project_state_mining_enabled:
            if consolidated_issue.linked_to_project:
                linked_to_project = "🟢"
            else:
                linked_to_project = "🔴"
        else:
            linked_to_project = "❌"

        # Generate the markdown line for the issue
        md_issue_line = (f"|{organization_name} | {repository_name} | [#{number} - {title}]({page_filename}) |"
                         f" {linked_to_project} | {status} |[GitHub link]({url}) |\n")

        return md_issue_line

    @staticmethod
    def _generate_issue_summary_table(consolidated_issue: ConsolidatedIssue) -> str:
        """
            Generates a string representation of feature info in a table format.

            @param consolidated_issue: The dictionary containing feature data.

            @return: A string representing the feature information in a table format.
        """
        # Join issue labels into one string
        labels = consolidated_issue.labels
        labels = ', '.join(labels) if labels else None

        # Format issue URL as a Markdown link
        issue_url = consolidated_issue.url
        issue_url = f"[GitHub link]({issue_url})" if issue_url else None

        # Define the header for the issue summary table
        # TODO: Does not support all the fields for now, have to update later
        headers = [
            "Organization name",
            "Repository name",
            "Issue number",
            "State",
            "Issue URL",
            # "Created at",
            # "Updated at",
            # "Closed at",
            "Labels"
        ]

        # Define the values for the issue summary table
        values = [
            consolidated_issue.organization_name,
            consolidated_issue.repository_name,
            consolidated_issue.number,
            consolidated_issue.state.lower(),
            issue_url,
            # consolidated_issue.created_at,
            # consolidated_issue.updated_at,
            # consolidated_issue.closed_at,
            labels
        ]

        # Update the summary table, if issue is linked to the project
        if consolidated_issue.linked_to_project:
            headers.extend([
                "Project title",
                "Status",
                "Priority",
                "Size",
                "MoSCoW"
            ])

            values.extend([
                consolidated_issue.project_name,
                consolidated_issue.status,
                consolidated_issue.priority,
                consolidated_issue.size,
                consolidated_issue.moscow
            ])
        else:
            headers.append("Linked to project")
            values.append(consolidated_issue.linked_to_project)

        # Initialize the Markdown table
        issue_info = "| Attribute | Content |\n|---|---|\n"

        # Add together all the attributes from the summary table in Markdown format
        for attribute, content in zip(headers, values):
            issue_info += f"| {attribute} | {content} |\n"

        return issue_info
