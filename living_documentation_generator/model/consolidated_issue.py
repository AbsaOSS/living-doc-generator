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
This module contains a data container for Consolidated Issue, which holds all the essential logic.
"""
import logging
from typing import Optional

from github.Issue import Issue

from living_documentation_generator.utils.utils import sanitize_filename
from living_documentation_generator.model.project_status import ProjectStatus

logger = logging.getLogger(__name__)


class ConsolidatedIssue:
    """
    A class representing a consolidated issue from the repository and project data.
    It provides methods for updating project data and generating page filenames,
    along with properties to access consolidated issue details.
    """

    def __init__(self, repository_id: str, repository_issue: Issue = None):
        # save issue from repository (got from GitHub library & keep connection to repository for lazy loading)
        # Warning: several issue properties requires additional API calls - use wisely to keep low API usage
        self.__issue: Issue = repository_issue

        self.__repository_id: str = repository_id
        parts = repository_id.split("/")
        self.__organization_name: str = parts[0] if len(parts) == 2 else ""
        self.__repository_name: str = parts[1] if len(parts) == 2 else ""

        # Extra project data (optionally provided from GithubProjects class)
        self.__linked_to_project: bool = False
        self.__project_issue_statuses: list[ProjectStatus] = []

        self.__error: Optional[str] = None

    # Issue properties
    @property
    def number(self) -> int:
        """Getter of the issue number."""
        return self.__issue.number if self.__issue else 0

    @property
    def repository_id(self) -> str:
        """Getter of the repository id."""
        return self.__repository_id

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
    def topics(self) -> list[str]:
        """Getter of the topics."""
        if self.__issue:
            return [topic.name for topic in self.__issue.labels]
        return []

    # Project properties
    @property
    def linked_to_project(self) -> bool:
        """Getter of the info if the issue is linked to a project."""
        return self.__linked_to_project

    @property
    def project_issue_statuses(self) -> list[ProjectStatus]:
        """Getter of the project issue statuses."""
        return self.__project_issue_statuses

    # Error property
    @property
    def error(self) -> Optional[str]:
        """Getter of the error message."""
        return self.__error

    def update_with_project_data(self, project_issue_status: ProjectStatus) -> None:
        """
        Update the consolidated issue with Project Status data.

        @param project_issue_status: The extra issue project data per one project.
        @return: None
        """
        self.__linked_to_project = True
        self.__project_issue_statuses.append(project_issue_status)

    def generate_page_filename(self) -> str:
        """
        Generate a filename page naming based on the issue number and title.

        @return: The generated page filename.
        """
        try:
            md_filename_base = f"{self.number}_{self.title.lower()}.md"
            page_filename = sanitize_filename(md_filename_base)
        except AttributeError:
            logger.error(
                "Issue page filename generation failed for Issue %s/%s (%s). Issue does not have a title.",
                self.organization_name,
                self.repository_name,
                self.number,
                exc_info=True,
            )
            return f"{self.number}.md"

        return page_filename
