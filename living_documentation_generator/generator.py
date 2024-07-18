import logging
import os
import shutil
from datetime import datetime

from living_documentation_generator.action.model.config_repository import ConfigRepository
from living_documentation_generator.github_integration.github_manager import GithubManager
from living_documentation_generator.github_integration.model.consolidated_issue import ConsolidatedIssue
from living_documentation_generator.github_integration.model.issue import Issue
from living_documentation_generator.github_integration.model.project_issue import ProjectIssue
from living_documentation_generator.utils import make_issue_key


class LivingDocumentationGenerator:

    ISSUE_PAGE_TEMPLATE_FILE = "../templates/issue_page_template.md"
    INDEX_PAGE_TEMPLATE_FILE = "../templates/_index_page_template.md"

    def __init__(self, repositories: list[ConfigRepository],
                 projects_title_filter: list[str] = None,
                 project_state_mining_enabled: bool = False,
                 output_path: str = "../output"):

        # data
        self._repositories: list[ConfigRepository] = repositories
        self._projects_title_filter: list[str] = projects_title_filter      # TODO - this could be part of repository config ???

        # features control
        self._project_state_mining_enabled: bool = project_state_mining_enabled

        # paths
        self._output_path: str = output_path

    @property
    def repositories(self) -> list[ConfigRepository]:
        return self._repositories

    @property
    def projects_title_filter(self) -> list[str]:
        return self._projects_title_filter

    @property
    def project_state_mining_enabled(self) -> bool:
        return self._project_state_mining_enabled

    @property
    def output_path(self) -> str:
        return self._output_path

    def generate(self):
        self._clean_output_directory()

        # Data mine GitHub issues with defined labels from repository
        gh_repo_issues: dict[str, list[Issue]] = self._mine_github_issues()
        # Note: got dict of list of issues for each repository (key is repository id)

        # Data mine GitHub project's issues
        gh_project_issues = self._mine_github_project_issues()

        # Consolidate all issues data together
        projects_issues = self._consolidate_issues_data(gh_repo_issues, gh_project_issues)

        # Generate markdown pages
        self._generate_markdown_pages(projects_issues)

    def _clean_output_directory(self):
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)
        os.makedirs(self.output_path)

    def _mine_github_issues(self) -> dict[str, list[Issue]]:
        issues = {}

        # Mine issues from every config repository
        for config_repository in self.repositories:
            repository_id = f"{config_repository.owner}/{config_repository.name}"

            if GithubManager().store_repository(repository_id) is None:
                return {}

            logging.info(f"Downloading issues from repository `{config_repository.owner}/{config_repository.name}`.")

            # Load all issues from one repository (unique for each repository)
            repo_issues = GithubManager().fetch_issues(labels=config_repository.query_labels)
            for repo_issue in repo_issues:
                repo_issue.repository = repository_id

            # save list of repository issue under its repository id
            # Note: not creating OOP object instead if this dict as Issue type will be replaced in next PR
            issues[repository_id] = repo_issues

        return issues

    def _mine_github_project_issues(self) -> dict[str, ProjectIssue]:
        if not self.project_state_mining_enabled:
            logging.info("Project data mining is not allowed. The process will not start.")
            return {}

        logging.info("Project data mining allowed, starting the process.")

        # Mine project issues for every repository
        project_issues = {}

        for config_repository in self.repositories:
            repository_id = f"{config_repository.owner}/{config_repository.name}"

            if GithubManager().store_repository(repository_id) is None:
                return {}

            # Fetch all projects_buffer attached to the repository
            projects = GithubManager().fetch_repository_projects(self.projects_title_filter)

            # Update every project with project issue related data
            for project in projects:
                for prj_issue in GithubManager().fetch_project_issues(project):
                    key = make_issue_key(prj_issue.organization_name, prj_issue.repository_name, prj_issue.number)
                    project_issues[key] = prj_issue

        return project_issues

    @staticmethod
    def _consolidate_issues_data(gh_repo_issues: dict[str, list[Issue]],
                                 gh_projects_issues: dict[str, ProjectIssue]) -> dict[str, ConsolidatedIssue]:

        consolidated_issues = {}

        # Create a ConsolidatedIssue object for each repository issue
        for repository_id in gh_repo_issues.keys():
            for repo_issue in gh_repo_issues[repository_id]:
                repo_id_parts = repository_id.split("/")
                unique_key = make_issue_key(repo_id_parts[0], repo_id_parts[1], repo_issue.number)
                consolidated_issues[unique_key] = ConsolidatedIssue(repository_id=repository_id, repo_issue=repo_issue)

        # Update issues with project data
        for key in consolidated_issues.keys():
            if key in gh_projects_issues:
                consolidated_issues[key].update_with_project_data(gh_projects_issues[key])

        return consolidated_issues

    def _generate_markdown_pages(self, issues: dict[str, ConsolidatedIssue]):
        with open(self.ISSUE_PAGE_TEMPLATE_FILE, 'r', encoding='utf-8') as issue_page_template_file:
            issue_page_template = issue_page_template_file.read()

        with open(self.INDEX_PAGE_TEMPLATE_FILE, 'r', encoding='utf-8') as idx_page_template_file:
            index_page_template = idx_page_template_file.read()

        # Process consolidated issues and generate markdown pages
        issue_markdown_content = self._process_consolidated_issues(issues, issue_page_template)

        # Generate index page
        self._generate_index_page(issue_markdown_content, index_page_template)

    def _process_consolidated_issues(self, consolidated_issues: dict[str, ConsolidatedIssue],
                                     issue_page_template: str) -> str:

        issue_markdown_content = ""
        table_header = """| Organization name     | Repository name | Issue 'Number - Title'  | Linked to project | Project status  |Issue URL   |
               |-----------------------|-----------------|---------------------------|---------|------|-----|
               """

        # Create an issue summary table for every issue
        issue_markdown_content += "\n" + table_header

        for consolidated_issue_data in consolidated_issues:
            consolidated_issue = ConsolidatedIssue().load_consolidated_issue(consolidated_issue_data)
            issue_markdown_content += self._generate_markdown_line(consolidated_issue)

            # Generate a single issue Markdown page
            self.generate_md_issue_page(issue_page_template, consolidated_issue)

        return issue_markdown_content

    def _generate_index_page(self, issue_markdown_content: str, template_index_page: str) -> None:
        """
            Generates an index summary markdown page for all features.

            @param issue_markdown_content: A string containing all the generated markdown blocks for the features.
            @param template_index_page: The string template for the index markdown page.
            @param output_directory: The directory where the index page will be saved.

            @return: None
        """

        # Prepare issues replacement for the index page
        replacement = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "issues": issue_markdown_content
        }

        # Replace the issue placeholders in the index template
        index_page = self.replace_template_placeholders(template_index_page, replacement)

        # Create an index page file
        with open(os.path.join(self.output_path, "_index.md"), 'w', encoding='utf-8') as index_file:
            index_file.write(index_page)

        logging.info("Generated _index.md.")

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
        if consolidated_issue.linked_to_project:
            linked_to_project = "🟢"
        else:
            linked_to_project = "🔴"

        # Generate the markdown line for the issue
        md_issue_line = (f"|{organization_name} | {repository_name} | [#{number} - {title}]({page_filename}) |"
                         f" {linked_to_project} | {status} |[GitHub link]({url}) |\n")

        return md_issue_line

    def generate_md_issue_page(self, issue_page_template: str, consolidated_issue: ConsolidatedIssue) -> None:
        """
            Generates a markdown file for a given feature using a specified template.

            @param issue_page_template: The string template for the single page markdown file.
            @param consolidated_issue: The dictionary containing feature data.
            @param output_directory: The directory where the markdown file will be saved.

            @return: None
        """

        # Get all replacements for generating single issue page from a template
        title = consolidated_issue.title
        date = datetime.now().strftime("%Y-%m-%d")
        issue_content = consolidated_issue.body

        # Generate a summary table for the issue
        issue_table = self.generate_issue_summary_table(consolidated_issue)

        # Initialize dictionary with replacements
        replacements = {
            "title": title,
            "date": date,
            "page_issue_title": title,
            "issue_summary_table": issue_table,
            "issue_content": issue_content
        }

        # Run through all replacements and update template keys with adequate content
        issue_md_page = self.replace_template_placeholders(issue_page_template, replacements)

        # Get the page filename for naming single issue output correctly
        page_filename = consolidated_issue.generate_page_filename()

        # Save the single issue Markdown page
        with open(os.path.join(self.output_path, page_filename), 'w', encoding='utf-8') as issue_file:
            issue_file.write(issue_md_page)

        print(f"Generated {page_filename}.")

    def replace_template_placeholders(self, template: str, replacement: dict[str, str]) -> str:
        """
            Replaces placeholders in a template ({replacement}) with corresponding values from a dictionary.

            @param template: The string template containing placeholders.
            @param replacement: The dictionary containing keys and values for replacing placeholders.

            @return: The updated template string with replaced placeholders.
        """

        # Update template with values from replacement dictionary
        for key, value in replacement.items():
            if value is not None:
                template = template.replace(f"{{{key}}}", value)
            else:
                template = template.replace(f"{{{key}}}", "")

        return template

    def generate_issue_summary_table(self, consolidated_issue: ConsolidatedIssue) -> str:
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
        issue_info = f"| Attribute | Content |\n|---|---|\n"

        # Add together all the attributes from the summary table in Markdown format
        for attribute, content in zip(headers, values):
            issue_info += f"| {attribute} | {content} |\n"

        return issue_info
