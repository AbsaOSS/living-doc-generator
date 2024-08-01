import logging
import requests

from github.Repository import Repository

from living_documentation_generator.model.github_project import GithubProject
from living_documentation_generator.model.project_issue import ProjectIssue
from living_documentation_generator.github_project_queries import GithubProjectQueries

logger = logging.getLogger(__name__)


class GithubProjects:

    def __init__(self, token: str):
        self.__token = token
        self.__session = None

    def initialize_request_session(self):
        """
        Initializes the request Session and updates the headers.

        @param github_token: The GitHub user token for authentication.

        @return: A configured request session.
        """

        self.__session = requests.Session()
        headers = {
            "Authorization": f"Bearer {self.__token}",
            "User-Agent": "IssueFetcher/1.0"
        }
        self.__session.headers.update(headers)

        return self.__session

    def send_graphql_query(self, query: str) -> dict[str, dict]:
        """
        Sends a GraphQL query to the GitHub API and returns the response.
        If an HTTP error occurs, it prints the error and returns an empty dictionary.

        @param query: The GraphQL query to be sent in f string format.

        @return: The response from the GitHub GraphQL API in a dictionary format.
        """
        try:
            if self.__session is None:
                self.initialize_request_session()

            # Fetch the response from the API
            response = self.__session.post('https://api.github.com/graphql', json={'query': query})
            # Check if the request was successful
            response.raise_for_status()

            return response.json()["data"]

        # Specific error handling for HTTP errors
        except requests.HTTPError as http_err:
            logger.error("HTTP error occurred: %s.", http_err, exc_info=True)

        except Exception as e:
            logger.error("An error occurred: %s.", e, exc_info=True)

        return {}

    def get_repository_projects(self, repository: Repository, projects_title_filter: list[str]) -> list[GithubProject]:
        projects = []

        # Fetch the project response from the GraphQL API
        projects_from_repo_query = GithubProjectQueries.get_projects_from_repo_query(repository.owner.login,
                                                                                     repository.name)

        projects_from_repo_response = self.send_graphql_query(projects_from_repo_query)

        # If response is not None, parse the project response
        if projects_from_repo_response['repository'] is not None:
            projects_from_repo_nodes = projects_from_repo_response['repository']['projectsV2']['nodes']
            repository_projects = []

            for project_json in projects_from_repo_nodes:
                # Check if the project is required based on the configuration filter
                project_title = project_json['title']

                # If no filter is provided, all projects are required
                is_project_required = True if len(projects_title_filter) else project_title in projects_title_filter

                # Main project structure is loaded and added to the projects list
                if is_project_required:
                    project = GithubProject().load_from_json(project_json, repository)
                    repository_projects.append(project)

            # Add the field options to the main project structure
            # TODO: Put this into load from json
            projects.extend([self.update_field_options(repository, project) for project in repository_projects])

        else:
            logger.warning("'repository' key is None in response: %s.", projects_from_repo_response)

        if len(projects) == 0:
            logger.info("No project attached for repository: %s/%s.", repository.owner.login, repository.name)

        return projects

    def update_field_options(self, repository: Repository, project: GithubProject):
        # Fetch the project field options from the GraphQL API
        project_field_options_query = GithubProjectQueries.get_project_field_options_query(repository.owner.login,
                                                                                           repository.name,
                                                                                           project.number)
        field_option_response = self.send_graphql_query(project_field_options_query)

        if field_option_response is None:
            logger.warning("Field option response is None for query: %s.", project_field_options_query)

        # Parse the field options from the response
        field_options_nodes = field_option_response['repository']['projectV2']['fields']['nodes']
        for field_option in field_options_nodes:
            if "name" in field_option and "options" in field_option:
                field_name = field_option["name"]
                options = [option["name"] for option in field_option["options"]]

                # Update the project structure with field options
                project.field_options.update({field_name: options})

        return project

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
            after_argument = f'after: "{cursor}"' if cursor else ''

            # Fetch project issues via GraphQL query
            issues_from_project_query = GithubProjectQueries.get_issues_from_project_query(project.id,
                                                                                           after_argument)

            project_issues_response = self.send_graphql_query(issues_from_project_query)

            # Return empty list, if project has no issues attached
            if len(project_issues_response) == 0:
                return []

            general_response_structure = project_issues_response['node']['items']
            project_issue_data = general_response_structure['nodes']
            page_info = general_response_structure['pageInfo']

            # Extend project issues list per every page during pagination
            project_issues_raw.extend(project_issue_data)
            logger.debug("Loaded `%s` issues from project: %s.", len(project_issue_data), project.title)

            # Check for closing the pagination process
            if not page_info['hasNextPage']:
                break
            cursor = page_info['endCursor']

        project_issues = [ProjectIssue().load_from_json(issue_json, project) for issue_json in project_issues_raw]

        return project_issues
