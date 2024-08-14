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
This module contains the ProjectStatus class which is responsible for access and change project issue status specifics.
"""

from living_documentation_generator.utils.constants import NO_PROJECT_DATA


class ProjectStatus:
    """
    A class representing the project status of an issue.

    Attributes:
        __project_title (str): The title of the project.
        __status (str): The status of the issue in the project.
        __priority (str): The priority of the issue in the project.
        __size (str): The difficulty of the issue in the project.
        __moscow (str): The MoSCoW prioritization of the issue in the project.
    """
    def __init__(self):
        self.__project_title: str = ""
        self.__status: str = NO_PROJECT_DATA
        self.__priority: str = NO_PROJECT_DATA
        self.__size: str = NO_PROJECT_DATA
        self.__moscow: str = NO_PROJECT_DATA

    @property
    def project_title(self) -> str:
        return self.__project_title

    @project_title.setter
    def project_title(self, value: str):
        self.__project_title = value

    @property
    def status(self) -> str:
        return self.__status

    @status.setter
    def status(self, value: str):
        self.__status = value

    @property
    def priority(self) -> str:
        return self.__priority

    @priority.setter
    def priority(self, value: str):
        self.__priority = value

    @property
    def size(self) -> str:
        return self.__size

    @size.setter
    def size(self, value: str):
        self.__size = value

    @property
    def moscow(self) -> str:
        return self.__moscow

    @moscow.setter
    def moscow(self, value: str):
        self.__moscow = value
