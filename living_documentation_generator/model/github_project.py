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
This module contains the GithubProject class which is responsible for loading JSON format data,
fetching project field options, along with properties to access project specifics.
"""

import logging

from github.Repository import Repository

logger = logging.getLogger(__name__)


class GithubProject:
    """
    A class representing GitHub Project in the Living Documentation.

    Attributes:
        __id (str): The ID of the project.
        __number (int): The number of the project.
        __title (str): The title of the project.
        __organization_name (str): The name of the organization that owns the project.
        __field_options (dict[str, str]): Field options, that can be used to describe a project issue.
    """
    def __init__(self):
        self.__id: str = ""
        self.__number: int = 0
        self.__title: str = ""
        self.__organization_name: str = ""
        self.__field_options: dict[str, str] = {}

    @property
    def id(self) -> str:
        """Getter of the project ID."""
        return self.__id

    @property
    def number(self) -> int:
        """Getter of the project number."""
        return self.__number

    @property
    def title(self) -> str:
        """Getter of the project title."""
        return self.__title

    @property
    def organization_name(self) -> str:
        """Getter of the organization name."""
        return self.__organization_name

    @property
    def field_options(self) -> dict[str, str]:
        """Getter of the project field options."""
        return self.__field_options

    def loads(self,
              project_json: dict,
              repository: Repository,
              field_option_response: dict) -> 'GithubProject':
        """
        Load the project data from several inputs.

        Args:
            project_json (dict): The JSON object containing the data about the project.
            repository (Repository): The GH repository object where the project is located.
            field_option_response (dict): The response containing the field options for the project.
        """
        self.__id = project_json["id"]
        self.__number = project_json["number"]
        self.__title = project_json["title"]
        self.__organization_name = repository.owner.login

        logger.debug("Updating field options for projects in repository `%s`.", repository.full_name)
        self.__update_field_options(field_option_response)

        return self

    def __update_field_options(self, field_option_response: dict):
        """Parse and update the field options of the project from a JSON response."""
        try:
            field_options_nodes = field_option_response["repository"]["projectV2"]["fields"]["nodes"]
        except KeyError:
            logger.error("There is no expected response structure for field options fetched from project: %s",
                         self.title,
                         exc_info=True
                         )
            return

        for field_option in field_options_nodes:
            if "name" in field_option and "options" in field_option:
                field_name = field_option["name"]
                options = [option["name"] for option in field_option["options"]]

                # Update the project structure with field options
                self.field_options.update({field_name: options})
