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
This module contains a data container for Project Issue, which holds all the essential logic.
"""
import logging

from typing import Optional

from living_documentation_generator.model.github_project import GithubProject
from living_documentation_generator.model.project_status import ProjectStatus

logger = logging.getLogger(__name__)


class ProjectIssue:
    """
    A class representing a Project Issue and is responsible for receiving, managing
    response data, along with properties to access project issue specifics.
    """

    def __init__(self):
        self.__number: int = 0
        self.__organization_name: str = ""
        self.__repository_name: str = ""
        self.__project_status: ProjectStatus = ProjectStatus()

    @property
    def number(self) -> int:
        """Getter of the project issue number."""
        return self.__number

    @property
    def organization_name(self) -> str:
        """Getter of the organization where the issue was fetched from."""
        return self.__organization_name

    @property
    def repository_name(self) -> str:
        """Getter of the repository name where the issue was fetched from."""
        return self.__repository_name

    @property
    def project_status(self) -> ProjectStatus:
        """Getter of the project issue status."""
        return self.__project_status

    def loads(self, issue_json: dict, project: GithubProject) -> Optional["ProjectIssue"]:
        """
        Loads the project issue data from the provided JSON and GithubProject object.

        @param: issue_json: The JSON data of the project issue.
        @param: project: The GithubProject object representing the project the issue belongs to.
        @return: The ProjectIssue object with the loaded data.
        """
        if not issue_json["content"]:
            logger.debug("No issue data provided in received json.")
            logger.debug(issue_json)
            return None

        self.__number = issue_json["content"]["number"]
        self.__organization_name = issue_json["content"]["repository"]["owner"]["login"]
        self.__repository_name = issue_json["content"]["repository"]["name"]
        self.__project_status.project_title = project.title

        # Parse the field types from the response
        field_types = []
        if "fieldValues" in issue_json:
            for node in issue_json["fieldValues"]["nodes"]:
                if node["__typename"] == "ProjectV2ItemFieldSingleSelectValue":
                    field_types.append(node["name"])

        # Update the project status with the field type values
        for field_type in field_types:
            if field_type in project.field_options.get("Status", []):
                self.__project_status.status = field_type
            elif field_type in project.field_options.get("Priority", []):
                self.__project_status.priority = field_type
            elif field_type in project.field_options.get("Size", []):
                self.__project_status.size = field_type
            elif field_type in project.field_options.get("MoSCoW", []):
                self.__project_status.moscow = field_type

        return self
