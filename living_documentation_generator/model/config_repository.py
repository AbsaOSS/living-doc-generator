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
This module contains a data container for Config Repository, which holds all the essential logic.
"""

from typing import Optional


class ConfigRepository:
    """
    A class representing the configuration for a GH repository to fetch data from.
    The class provides loading logic and properties to access all the details.
    """

    def __init__(self):
        self.__organization_name: str = ""
        self.__repository_name: str = ""
        self.__query_labels: list[Optional[str]] = [None]
        self.__projects_title_filter: list[Optional[str]] = [None]

    @property
    def organization_name(self) -> str:
        """Getter of the repository organization name."""
        return self.__organization_name

    @property
    def repository_name(self) -> str:
        """Getter of the repository name."""
        return self.__repository_name

    @property
    def query_labels(self) -> list[str]:
        """Getter of the query labels."""
        return self.__query_labels

    @property
    def projects_title_filter(self) -> list[str]:
        """Getter of the project title filter."""
        return self.__projects_title_filter

    def load_from_json(self, repository_json: dict) -> None:
        """
        Load the configuration from a JSON object.

        @param repository_json: The JSON object containing the repository configuration.
        @return: None
        """
        self.__organization_name = repository_json["organization-name"]
        self.__repository_name = repository_json["repository-name"]
        self.__query_labels = repository_json["query-labels"]
        self.__projects_title_filter = repository_json["projects-title-filter"]
