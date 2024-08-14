#
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
This module contains the ConsolidatedIssue class which represents a consolidated issue from a GitHub repository.
The class provides methods for updating project data and generating page filenames, along with properties to access
consolidated issue details.
"""

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
        """Getter of the issue number."""
        return self.__issue.number if self.__issue else 0

    @property
    def organization_name(self) -> str:
        """Getter of the organization where the issue was fetched from."""
        return self.__organization_name

    @property
    def repository_name(self) -> str:
        """Getter of the repository name where the issue was fetched from."""
        return self.__repository_name

    @property
    def title(self) -> str:
        """Getter of the issue title."""
        return self.__issue.title if self.__issue else ""

    @property
    def state(self) -> str:
        """Getter of the issue state."""
        return self.__issue.state if self.__issue else ""

    @property
    def created_at(self) -> str:
        """Getter of the info when issue was created."""
        return self.__issue.created_at if self.__issue else ""

    @property
    def updated_at(self) -> str:
        """Getter of the info when issue was updated"""
        return self.__issue.updated_at if self.__issue else ""

    @property
    def closed_at(self) -> str:
        """Getter of the info when issue was closed."""
        return self.__issue.closed_at if self.__issue else ""

    @property
    def html_url(self) -> str:
        """Getter of the issue GitHub html URL."""
        return self.__issue.html_url if self.__issue else ""

    @property
    def body(self) -> str:
        """Getter of the issue description."""
        return self.__issue.body if self.__issue else ""

    @property
    def labels(self) -> list[str]:
        """Getter of the issue labels."""
        if self.__issue:
            return [label.name for label in self.__issue.labels]
        return []

    # Project properties
    @property
    def linked_to_project(self) -> bool:
        """Getter of the info if the issue is linked to a project."""
        return self.__linked_to_project

    @property
    def project_status(self) -> ProjectStatus:
        """Getter of the project status."""
        return self.__project_status

    # Error property
    @property
    def error(self) -> Optional[str]:
        """Getter of the error message."""
        return self.__error

    def update_with_project_data(self, project_status: ProjectStatus) -> None:
        """
        Update the consolidated issue with attached project data.

        Args:
            project_status (ProjectStatus): The extra issue project data.
        """
        self.__linked_to_project = True
        self.__project_status.project_title = project_status.project_title
        self.__project_status.status = project_status.status
        self.__project_status.priority = project_status.priority
        self.__project_status.size = project_status.size
        self.__project_status.moscow = project_status.moscow

    def generate_page_filename(self) -> str:
        """Generate a filename page naming based on the issue number and title."""
        md_filename_base = f"{self.number}_{self.title.lower()}.md"
        page_filename = sanitize_filename(md_filename_base)

        return page_filename
