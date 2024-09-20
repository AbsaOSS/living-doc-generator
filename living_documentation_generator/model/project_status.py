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
This module contains a data container for issue Project Status.
"""
from typing import Union

from living_documentation_generator.utils.constants import NO_PROJECT_DATA


class ProjectStatus:
    """
    A class representing the project status of an issue is responsible for access
    and change project issue status specifics.
    """

    def __init__(self):
        self.__project_title = [NO_PROJECT_DATA]
        self.__status = [NO_PROJECT_DATA]
        self.__priority = [NO_PROJECT_DATA]
        self.__size = [NO_PROJECT_DATA]
        self.__moscow = [NO_PROJECT_DATA]

    @property
    def project_title(self) -> list:
        return self.__project_title

    @project_title.setter
    def project_title(self, value: Union[str, list]):
        if self.__project_title == [NO_PROJECT_DATA]:
            self.__project_title = [value]
        else:
            self.__project_title.append(value)

    @property
    def status(self) -> list:
        return self.__status

    @status.setter
    def status(self, value: Union[str, list]):
        if self.__status == [NO_PROJECT_DATA]:
            self.__status = [value]
        else:
            self.__status.append(value)

    @property
    def priority(self) -> list:
        return self.__priority

    @priority.setter
    def priority(self, value: Union[str, list]):
        if self.__priority == [NO_PROJECT_DATA]:
            self.__priority = [value]
        else:
            self.__priority.append(value)

    @property
    def size(self) -> list:
        return self.__size

    @size.setter
    def size(self, value: Union[str, list]):
        if self.__size == [NO_PROJECT_DATA]:
            self.__size = [value]
        else:
            self.__size.append(value)

    @property
    def moscow(self) -> list:
        return self.__moscow

    @moscow.setter
    def moscow(self, value: Union[str, list]):
        if self.__moscow == [NO_PROJECT_DATA]:
            self.__moscow = [value]
        else:
            self.__moscow.append(value)
