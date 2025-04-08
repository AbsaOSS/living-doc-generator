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
import os
import re
from typing import Optional

from github.Issue import Issue

from living_documentation_regime.model.project_status import ProjectStatus
from utils.constants import DOC_USER_STORY_LABEL, DOC_FUNCTIONALITY_LABEL
from utils.utils import sanitize_filename

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
        # self.__topics: list[str] = []

        # Extra project data (optionally provided from GithubProjects class)
        self.__linked_to_project: bool = False
        self.__project_issue_statuses: list[ProjectStatus] = []

        self.__errors: dict = {}

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
        parts = self.__repository_id.split("/")
        return parts[0] if len(parts) == 2 else ""

    @property
    def repository_name(self) -> str:
        """Getter of the repository name where the issue was fetched from."""
        parts = self.__repository_id.split("/")
        return parts[1] if len(parts) == 2 else ""

    @property
    def topics(self) -> list:
        """Getter of the issue topics."""
        return self.__topics

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
    def project_issue_statuses(self) -> list[ProjectStatus]:
        """Getter of the project issue statuses."""
        return self.__project_issue_statuses

    # Error property
    @property
    def errors(self) -> dict[str, str]:
        """Getter of the errors that occurred during the issue processing."""
        return self.__errors

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
            if DOC_USER_STORY_LABEL in self.labels or DOC_FUNCTIONALITY_LABEL in self.labels:
                md_filename_base = f"{self.number}_{self.title.lower()}.md"
                page_filename = sanitize_filename(md_filename_base)
            else:
                # covers the case of DOC_FEATURE_LABEL
                page_filename = "_index.md"
        except AttributeError:
            self.__errors.update(
                {"AttributeError": "Issue page filename generation failed (issue does not have a title)."}
            )
            return f"{self.number}.md"

        return page_filename

    def validate_labels(
        self, documentation_labels: list[str], topic_labels: list[str], output_path: str
    ) -> Optional[list[str]]:
        """
        Validate the topic and documentation labels, update errors accordingly,
        and return a fallback directory path if no topic label is found.

        @param documentation_labels: List of documentation labels.
        @param topic_labels: List of topic labels.
        @param output_path: Base output path to construct a fallback directory.
        @return: A list containing the fallback directory path if no topic label is found,
                 otherwise None.
        """
        # Fallback if there are no topic labels
        if not topic_labels:
            self.__topics = ["NoTopic"]
            self.__errors.update({"TopicError": "No Topic label found."})
            no_topic_path = os.path.join(output_path, "NoTopic")
            return [no_topic_path]

        if len(documentation_labels) > 1:
            self.__errors.update({"DocumentationError": "More than one Documentation label found."})

        if len(topic_labels) > 1:
            self.__errors.update({"TopicError": "More than one Topic label found."})

        # If a topic label exists without any documentation label, update the error
        if not documentation_labels:
            self.__errors.update({"DocumentationError": "Topic label found without Documentation one."})

        return None

    def get_feature_id(self) -> Optional[str]:
        """
        Get the feature ID from the issue body.

        @return: The feature ID if found, otherwise None.
        """
        if self.body:
            match = re.search(r"(?<=### Associated Feature\n- #)\d+", self.body)
            if match:
                return match.group(0)
        return None
