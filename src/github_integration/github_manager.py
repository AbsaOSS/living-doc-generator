import logging
import time

from datetime import datetime
from typing import Optional

import requests
from github import Github, Auth
from github.GitRelease import GitRelease
from github.RateLimit import RateLimit
from github.Repository import Repository

from .github_project_queries import GithubProjectQueries
from .model.commit import Commit
from .model.issue import Issue
from .model.pull_request import PullRequest
from .model.github_project import GithubProject
from .model.project_issue import ProjectIssue


def singleton(cls):
    """
    A decorator for making a class a singleton.

    :param cls: The class to make a singleton.
    :return: The singleton instance of the class.
    """

    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class GithubManager:
    RATE_LIMIT_THRESHOLD_PERCENTAGE = 10  # Start sleeping logic when less than 10% of rate limit remains

    """
    A singleton class used to manage GitHub interactions.
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the GithubManager object.
        """
        self.__g = None
        self.__repository = None
        self.__git_release = None
        self.__session = None

    @property
    def github(self) -> Github:
        """
        Gets the g attribute.

        :return: The Github object.
        """
        return self.__g

    @github.setter
    def github(self, g: Github):
        """
        Sets the g attribute.

        :return: The Github object.
        """
        self.__g = g

    @property
    def repository(self) -> Optional[Repository]:
        """
        Gets the repository attribute.

        :return: The Repository object, or None if it is not set.
        """
        return self.__repository

    @property
    def git_release(self) -> Optional[GitRelease]:
        """
        Gets the git_release attribute.

        :return: The GitRelease object, or None if it is not set.
        """
        return self.__git_release

    # fetch method

    def store_repository(self, repository_id: str) -> Optional[Repository]:
        """
        Fetches a repository from GitHub using the provided repository ID.

        :param repository_id: The ID of the repository to fetch.
        :return: The fetched Repository object, or None if the repository could not be fetched.
        """
        try:
            logging.info(f"Fetching repository: {repository_id}")
            self.__repository = self.__g.get_repo(repository_id)
        except Exception as e:
            if "Not Found" in str(e):
                logging.error(f"Repository not found: {repository_id}")
                self.__repository = None
            else:
                logging.error(f"Fetching repository failed for {repository_id}: {str(e)}")
                self.__repository = None

        return self.__repository

    def fetch_latest_release(self) -> Optional[GitRelease]:
        """
        Fetches the latest release from a current repository.

        :return: The fetched GitRelease object representing the latest release, or None if there is no release or the fetch failed.
        """
        try:
            logging.info(f"Fetching latest release for {self.__repository.full_name}")
            release = self.__repository.get_latest_release()
            logging.debug(f"Found latest release: {release.tag_name}, created at: {release.created_at}, "
                          f"published at: {release.published_at}")
            self.__git_release = release

        except Exception as e:
            if "Not Found" in str(e):
                logging.error(f"Latest release not found for {self.__repository.full_name}. 1st release for repository!")
                self.__git_release = None
            else:
                logging.error(f"Fetching latest release failed for {self.__repository.full_name}: {str(e)}. "
                              f"Expected first release for repository.")
                self.__git_release = None

        return self.__git_release

    def fetch_issues(self, since: datetime = None, state: str = None, labels: list[str] = None) -> list[Issue]:
        """
        Fetches all issues from the current repository.
        If a since is set, fetches all issues since the defined time.

        :return: A list of Issue objects.
        """
        if labels is None:
            labels = []

        # TODO: issue here!
        # TODO: issue with saving repository issues, because we have to fetch extra labels, which is extra call and is late
        issues = []
        if not labels:
            logging.info(f"Fetching all issues for {self.__repository.full_name}")
            issues.extend(self.__repository.get_issues(state="all"))
        else:
            # We fetch issues for every config label, because we don't want to fetch all issues and filter afterward
            for label in labels:
                logging.info(f"Fetching issues with label {label} for {self.__repository.full_name}")
                issues.extend(self.__repository.get_issues(state="all", labels=[label]))

        parsed_issues = []
        issue_unique_numbers = []
        logging.info(f"Found {len(list(issues))} issues for {self.__repository.full_name}")
        for issue in list(issues):
            if issue.number not in issue_unique_numbers:
                parsed_issues.append(Issue(issue))
                issue_unique_numbers.append(issue.number)

        return parsed_issues

    def fetch_pull_requests(self, since: datetime = None) -> list[PullRequest]:
        """
        Fetches all pull requests from the current repository.
        If a 'since' datetime is provided, fetches all pull requests since that time.
        If a 'state' is provided, fetches pull requests with that state.

        :param since: The datetime to fetch pull requests since. If None, fetches all pull requests.
        :param state: The state of the pull requests to fetch. If None, fetches pull requests of all states.
        :return: A list of PullRequest objects.
        """
        logging.info(f"Fetching all closed PRs for {self.__repository.full_name}")
        pulls = self.__repository.get_pulls(state="closed")

        pull_requests = []
        logging.info(f"Found {len(list(pulls))} PRs for {self.__repository.full_name}")
        for pull in list(pulls):
            pull_requests.append(PullRequest(pull))

        return pull_requests

    def fetch_commits(self, since: datetime = None) -> list[Commit]:
        logging.info(f"Fetching all commits {self.__repository.full_name}")
        raw_commits = self.__repository.get_commits()

        commits = []
        for raw_commit in raw_commits:
            # for reference commit author - use raw_commit.author

            # logging.debug(f"Raw Commit: {raw_commit}, Author: {raw_commit.author}, Commiter: {raw_commit.committer}.")
            # logging.debug(f"Raw Commit.commit: Message: {raw_commit.commit.message}, Author: {raw_commit.commit.author}, Commiter: {raw_commit.commit.committer}.")

            commits.append(Commit(raw_commit))

        return commits

    # get methods

    def get_change_url(self, tag_name: str) -> str:
        if self.__git_release:
            # If there is a latest release, create a URL pointing to commits since the latest release
            changelog_url = f"https://github.com/{self.__repository.full_name}/compare/{self.__git_release.tag_name}...{tag_name}"

        else:
            # If there is no latest release, create a URL pointing to all commits
            changelog_url = f"https://github.com/{self.__repository.full_name}/commits/{tag_name}"

        return changelog_url

    def get_repository_full_name(self) -> Optional[str]:
        """
        Gets the full name of the repository.

        :return: The full name of the repository as a string, or None if the repository is not set.
        """
        if self.__repository is not None:
            return self.__repository.full_name
        return None

    # others

    def initialize_github_instance(self, github_token: str, per_page: int):
        auth = Auth.Token(token=github_token)
        self.github = Github(auth=auth, per_page=per_page)
        self.show_rate_limit()

    def show_rate_limit(self):
        if not logging.getLogger().isEnabledFor(logging.DEBUG):
            # save API Call when not in debug mode
            return

        if self.__g is None:
            logging.error("GitHub object is not set.")
            return

        rate_limit: RateLimit = self.__g.get_rate_limit()

        threshold = rate_limit.core.limit * self.RATE_LIMIT_THRESHOLD_PERCENTAGE / 100
        if rate_limit.core.remaining < threshold:
            reset_time = rate_limit.core.reset
            sleep_time = (reset_time - datetime.utcnow()).total_seconds() + 10
            logging.debug(f"Rate limit reached. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)
        else:
            logging.debug(f"Rate limit: {rate_limit.core.remaining} remaining of {rate_limit.core.limit}")

    def initialize_request_session(self, github_token: str):
        """
        Initializes the request Session and updates the headers.

        @param github_token: The GitHub user token for authentication.

        @return: A configured request session.
        """

        self.__session = requests.Session()
        headers = {
            "Authorization": f"Bearer {github_token}",
            "User-Agent": "IssueFetcher/1.0"
        }
        self.__session.headers.update(headers)

        return self.__session

    def fetch_repository_projects(self, projects_title_filter) -> list[GithubProject]:
        projects = []

        # Fetch the project response from the GraphQL API
        projects_from_repo_query = GithubProjectQueries.get_projects_from_repo_query(self.__repository.owner.login,
                                                                                     self.__repository.name)
        projects_from_repo_response = self.send_graphql_query(projects_from_repo_query)

        # If response is not None, parse the project response
        if projects_from_repo_response['repository'] is not None:
            projects_from_repo_nodes = projects_from_repo_response['repository']['projectsV2']['nodes']
            projects = []

            for project_json in projects_from_repo_nodes:
                # Check if the project is required based on the configuration filter
                project_title = project_json['title']
                # If no filter is provided, all projects are required
                is_project_required = (projects_title_filter == '[]') or (project_title in projects_title_filter)

                # Main project structure is loaded and added to the projects list
                if is_project_required:
                    project = GithubProject().load_from_json(project_json, self.__repository)
                    projects.append(project)

            # Add the field options to the main project structure
            # TODO: Put this into load from json
            projects = [self.update_field_options(project) for project in projects]

        else:
            logging.warning(f"'repository' key is None in response: {projects_from_repo_response}")

        if not projects:
            logging.info(f"No project attached for repository: {self.__repository.owner.login}/{self.__repository.name}")

        return projects

    def send_graphql_query(self, query: str) -> dict[str, dict]:
        """
        Sends a GraphQL query to the GitHub API and returns the response.
        If an HTTP error occurs, it prints the error and returns an empty dictionary.

        @param query: The GraphQL query to be sent in f string format.

        @return: The response from the GitHub GraphQL API in a dictionary format.
        """
        try:
            # Fetch the response from the API
            response = self.__session.post('https://api.github.com/graphql', json={'query': query})
            # Check if the request was successful
            response.raise_for_status()

            return response.json()["data"]

        # Specific error handling for HTTP errors
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")

        except Exception as e:
            print(f"An error occurred: {e}")

        return {}

    def update_field_options(self, project: GithubProject):
        # Fetch the project field options from the GraphQL API
        project_field_options_query = GithubProjectQueries.get_project_field_options_query(self.__repository.owner.login,
                                                                                           self.__repository.name,
                                                                                           project.number)
        field_option_response = self.send_graphql_query(project_field_options_query)

        if field_option_response is None:
            logging.warning(f"Field option response is None for query: {project_field_options_query}")

        # Parse the field options from the response
        field_options_nodes = field_option_response['repository']['projectV2']['fields']['nodes']
        for field_option in field_options_nodes:
            if "name" in field_option and "options" in field_option:
                field_name = field_option["name"]
                options = [option["name"] for option in field_option["options"]]

                # Update the project structure with field options
                project.field_options.update({field_name: options})

        return project

    def fetch_project_issues(self, project: GithubProject) -> list[ProjectIssue]:
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
            logging.info(f"Loaded `{len(project_issue_data)}` issues.")

            # Check for closing the pagination process
            if not page_info['hasNextPage']:
                break
            cursor = page_info['endCursor']

        project_issues = [ProjectIssue().load_from_json(issue_json, project) for issue_json in project_issues_raw]

        return project_issues
