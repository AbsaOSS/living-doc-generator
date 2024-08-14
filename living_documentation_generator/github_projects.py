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
This module contains the GithubProjects class which is responsible for mining data for GitHub Projects.

The GithubProjects class handles the logic of initializing request session, sending GraphQL queries
and processes the responses.
"""

import logging
from typing import Optional
import requests

from github.Repository import Repository

from living_documentation_generator.model.github_project import GithubProject
from living_documentation_generator.model.project_issue import ProjectIssue
from living_documentation_generator.utils.github_project_queries import (
    GithubProjectQueries,
)

logger = logging.getLogger(__name__)


class GithubProjects:
    """
    A class representing all the logic for mining data for GitHub Projects.

    Attributes:
        __token (str): The GitHub token used for authentication.
        __session (requests.Session): The session for making graphQL requests.
    """
    def __init__(self, token: str):
        self.__token = token
        self.__session = None

    def __initialize_request_session(self):
        """
        Initializes the request Session and updates the headers.

        @param github_token: The GitHub user token for authentication.

        @return: A configured request session.
        """

        self.__session = requests.Session()
        headers = {
            "Authorization": f"Bearer {self.__token}",
            "User-Agent": "IssueFetcher/1.0",
        }
        self.__session.headers.update(headers)

        return self.__session

    def __send_graphql_query(self, query: str) -> Optional[dict[str, dict]]:
        """
        Sends a GraphQL query to the GitHub API and returns the response.
        If an HTTP error occurs, it prints the error and returns an empty dictionary.

        @param query: The GraphQL query to be sent in f string format.

        @return: The response from the GitHub GraphQL API in a dictionary format.
        """
        try:
            if self.__session is None:
                self.__initialize_request_session()

            # Fetch the response from the API
            response = self.__session.post("https://api.github.com/graphql", json={"query": query})
            # Check if the request was successful
            response.raise_for_status()

            return response.json()["data"]

        # Specific error handling for HTTP errors
        except requests.HTTPError as http_err:
            logger.error("HTTP error occurred: %s.", http_err, exc_info=True)

        except requests.RequestException as req_err:
            logger.error("An error occurred: %s.", req_err, exc_info=True)

        return None

    def get_repository_projects(
            self, repository: Repository, projects_title_filter: list[str]) -> list[GithubProject]:
        projects = []

        # Fetch the project response from the GraphQL API
        projects_from_repo_query = GithubProjectQueries.get_projects_from_repo_query(
            organization_name=repository.owner.login, repository_name=repository.name
        )

        projects_from_repo_response = self.__send_graphql_query(projects_from_repo_query)

        if projects_from_repo_response is None:
            logger.warning(
                "Project response is None for repository `%s`.", repository.full_name
            )
            return projects

        # If response is not None, parse the project response
        if projects_from_repo_response["repository"] is not None:
            projects_from_repo_nodes = projects_from_repo_response["repository"]["projectsV2"]["nodes"]

            for project_json in projects_from_repo_nodes:
                # Check if the project is required based on the configuration filter
                project_title = project_json["title"]
                project_number = project_json["number"]

                # If no filter is provided, all projects are required
                is_project_required = (
                    True
                    if not projects_title_filter
                    else project_title in projects_title_filter
                )

                # Main project structure is loaded and added to the projects list
                if is_project_required:
                    # Fetch the project field options from the GraphQL API
                    project_field_options_query = (
                        GithubProjectQueries.get_project_field_options_query(
                            organization_name=repository.owner.login,
                            repository_name=repository.name,
                            project_number=project_number,
                        )
                    )
                    field_option_response = self.__send_graphql_query(project_field_options_query)

                    project = GithubProject().load_from_json(project_json, repository, field_option_response)

                    if project not in projects:
                        projects.append(project)

        else:
            logger.warning("'repository' key is None in response: %s.", projects_from_repo_response)

        if not projects:
            logger.info(
                "Fetching GitHub project data - no project data for repository `%s`.",
                repository.full_name,
            )

        return projects

    def get_project_issues(self, project: GithubProject) -> list[ProjectIssue]:
        """
        Fetches all issues from a given project using a GraphQL query.
        The issues are fetched supported by pagination.

        @return: The list of all issues in the project.
        """
        project_issues_raw = []
        cursor = None

        while True:
            # Add the after argument to the query if a cursor is provided
            after_argument = f'after: "{cursor}"' if cursor else ""

            # Fetch project issues via GraphQL query
            issues_from_project_query = (GithubProjectQueries.get_issues_from_project_query(
                project_id=project.id, after_argument=after_argument
                )
            )

            project_issues_response = self.__send_graphql_query(issues_from_project_query)

            # Return empty list, if project has no issues attached
            if not project_issues_response:
                return []

            general_response_structure = project_issues_response["node"]["items"]
            project_issue_data = general_response_structure["nodes"]
            page_info = general_response_structure["pageInfo"]

            # Extend project issues list per every page during pagination
            project_issues_raw.extend(project_issue_data)
            logger.debug(
                "Loaded `%s` issues from project: %s.",
                len(project_issue_data),
                project.title
            )

            # Check for closing the pagination process
            if not page_info["hasNextPage"]:
                break
            cursor = page_info["endCursor"]

        project_issues = [
            ProjectIssue().load_from_json(issue_json, project)
            for issue_json in project_issues_raw
        ]

        return project_issues
