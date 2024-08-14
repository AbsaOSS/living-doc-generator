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
This module contains the ProjectIssue class which is responsible for correct loading issue data,
along with properties to access project issue specifics.
"""

from living_documentation_generator.model.github_project import GithubProject
from living_documentation_generator.model.project_status import ProjectStatus


class ProjectIssue:
    """
    A class representing a Project Issue.

    Attributes:
        __number (int): The number of the project issue.
        __organization_name (str): The name of the repo organization where the issue is located.
        __repository_name (str): The name of the repository where the issue is located.
        __project_status (ProjectStatus): The status of the project issue in the project.
    """
    def __init__(self):
        self.__number: int = 0
        self.__organization_name: str = ""
        self.__repository_name: str = ""
        self.__project_status: ProjectStatus = ProjectStatus()

    @property
    def number(self) -> int:
        return self.__number

    @property
    def organization_name(self) -> str:
        return self.__organization_name

    @property
    def repository_name(self) -> str:
        return self.__repository_name

    @property
    def project_status(self) -> ProjectStatus:
        return self.__project_status

    def load_from_json(self, issue_json: dict, project: GithubProject):
        self.__number = issue_json["content"]["number"]
        self.__organization_name = issue_json["content"]["repository"]["owner"]["login"]
        self.__repository_name = issue_json["content"]["repository"]["name"]
        self.__project_status.project_title = project.title

        field_types = []
        if "fieldValues" in issue_json:
            for node in issue_json["fieldValues"]["nodes"]:
                if node["__typename"] == "ProjectV2ItemFieldSingleSelectValue":
                    field_types.append(node["name"])

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
