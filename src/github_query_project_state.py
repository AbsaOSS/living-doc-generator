"""
GitHub Query Project State

This script is used to fetch and process project state data from GitHub.
It queries GitHub's GraphQL API to get the data, and then processes and generate
project output JSON file/s.
"""

import os
import logging

from action.action_inputs import ActionInputs
from github_integration.github_manager import GithubManager
from utils import ensure_folder_exists, save_to_json_file

ISSUES_PER_PAGE_LIMIT = 100
OUTPUT_DIRECTORY = "../data/fetched_data/project_data"


def main() -> None:
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Script for downloading project data from GitHub GraphQL started.")

    # Load action inputs from the environment
    action_inputs = ActionInputs().load_from_environment()

    # Check if the output directory exists and create it if not
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(OUTPUT_DIRECTORY, current_dir)

    # Check if project mining is allowed and exit the script if necessary
    if not action_inputs.is_project_state_mining_enabled:
        logging.info("Project data mining is not allowed. The process will not start.")
        exit()

    logging.info("Project data mining allowed, starting the process.")

    # Initialize GitHub instance
    GithubManager().initialize_github_instance(action_inputs.github_token, ISSUES_PER_PAGE_LIMIT)

    # Initialize the request session
    GithubManager().initialize_request_session(action_inputs.github_token)

    # Mine project issues for every repository
    projects = []
    project_issues = []
    config_repositories = action_inputs.repositories
    for config_repository in config_repositories:
        repository_id = f"{config_repository.owner}/{config_repository.name}"

        if GithubManager().store_repository(repository_id) is None:
            return None

        # Fetch all projects attached to the repository
        projects_title_filter = action_inputs.projects_title_filter
        projects.extend(prjts := GithubManager().fetch_repository_projects(projects_title_filter))

        # Update every project with project issue related data
        for project in prjts:
            project_issues.extend(GithubManager().fetch_project_issues(project))

    # Convert issue objects back into dictionary, so it can be serialized to JSON directly
    project_issues_to_save = [project_issue.to_dict() for project_issue in project_issues]
    logging.info(f"`{len(project_issues_to_save)}` project issues in total fetched and ready to be saved.")

    # Save project state into unique JSON file
    output_file_name = save_to_json_file(project_issues_to_save, "projects", OUTPUT_DIRECTORY, "issues")
    logging.info(f"Project Issue state saved into file: {output_file_name}.")

    logging.info("Script for downloading project data from GitHub GraphQL ended.")


if __name__ == "__main__":
    main()

