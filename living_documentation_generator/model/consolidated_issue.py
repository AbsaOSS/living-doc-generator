from typing import Optional

from github.Issue import Issue

from living_documentation_generator.utils.utils import sanitize_filename
from living_documentation_generator.model.project_status import ProjectStatus


class ConsolidatedIssue:
    """
    A class representing a consolidated issue from the repository and project data.

    Attributes:
        __issue (Issue): The issue from the repository.
        __organization_name (str): The name of the organization that owns the repository.
        __repository_name (str): The name of the repository.
        __linked_to_project (bool): Switch indicating if the issue is linked to a project.
        __project_status (ProjectStatus): The status of the project issue in the project.
        __error (Optional[str]): Any error that occurred while processing the issue.
    """
    def __init__(self, repository_id: str, repository_issue: Issue = None):
        # save issue from repository (got from GitHub library & keep connection to repository for lazy loading)
        # Warning: several issue properties requires additional API calls - use wisely to keep low API usage
        self.__issue = repository_issue

        parts = repository_id.split("/")
        self.__organization_name: str = parts[0] if len(parts) == 2 else ""
        self.__repository_name: str = parts[1] if len(parts) == 2 else ""

        # Extra project data (optionally provided from GithubProjects class)
        self.__linked_to_project: bool = False
        self.__project_status: ProjectStatus = ProjectStatus()

        self.__error: Optional[str] = None

    # Issue properties
    @property
    def number(self) -> int:
        return self.__issue.number if self.__issue else 0

    @property
    def organization_name(self) -> str:
        return self.__organization_name

    @property
    def repository_name(self) -> str:
        return self.__repository_name

    @property
    def title(self) -> str:
        return self.__issue.title if self.__issue else ""

    @property
    def state(self) -> str:
        return self.__issue.state if self.__issue else ""

    @property
    def created_at(self) -> str:
        return self.__issue.created_at if self.__issue else ""

    @property
    def updated_at(self) -> str:
        return self.__issue.updated_at if self.__issue else ""

    @property
    def closed_at(self) -> str:
        return self.__issue.closed_at if self.__issue else ""

    @property
    def html_url(self) -> str:
        return self.__issue.html_url if self.__issue else ""

    @property
    def body(self) -> str:
        return self.__issue.body if self.__issue else ""

    @property
    def labels(self) -> list[str]:
        if self.__issue:
            return [label.name for label in self.__issue.labels]
        return []

    # Project properties
    @property
    def linked_to_project(self) -> bool:
        return self.__linked_to_project

    @property
    def project_status(self) -> ProjectStatus:
        return self.__project_status

    # Error property
    @property
    def error(self) -> Optional[str]:
        return self.__error

    def update_with_project_data(self, project_status: ProjectStatus):
        self.__linked_to_project = True
        self.__project_status.project_title = project_status.project_title
        self.__project_status.status = project_status.status
        self.__project_status.priority = project_status.priority
        self.__project_status.size = project_status.size
        self.__project_status.moscow = project_status.moscow

    def generate_page_filename(self):
        md_filename_base = f"{self.number}_{self.title.lower()}.md"
        page_filename = sanitize_filename(md_filename_base)

        return page_filename
