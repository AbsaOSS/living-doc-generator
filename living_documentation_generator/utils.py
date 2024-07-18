"""Utility Functions

This script contains helper functions that are used across multiple living_documentation_generator in this project.

These functions can be imported and used in other living_documentation_generator as needed.
"""

import os
import json
import re
import requests

from action.model.config_repository import ConfigRepository
from github_integration.model.issue import Issue


def initialize_request_session(github_token: str) -> requests.sessions.Session:
    """
    Initializes the request Session and updates the headers.

    @param github_token: The GitHub user token for authentication.

    @return: A configured request session.
    """

    session = requests.Session()
    headers = {
        "Authorization": f"Bearer {github_token}",
        "User-Agent": "IssueFetcher/1.0"
    }
    session.headers.update(headers)

    return session


def ensure_folder_exists(folder_name: str, current_dir: str) -> None:
    """
    Ensures that given folder exists. Creates it if it doesn't.

    @param folder_name: The name of the folder to check.
    @param current_dir: The directory of the current script.

    @return: None
    """

    # Path to the folder in the same directory as this script
    folder_path = os.path.join(current_dir, folder_name)

    # Create the folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        print(f"The '{folder_path}' folder has been created.")


def save_to_json_file(items_to_save: list, object_type: str, output_directory: str, context_name: str) -> str:
    """
    Saves a list state to a JSON file.

    @param items_to_save: The list to be saved.
    @param object_type: The object type of the state (e.g., 'feature', 'project').
    @param output_directory: The directory, where the file will be saved.
    @param context_name: The naming of the state.

    @return: The name of the output file.
    """
    # Prepare the sanitized filename of the output file
    sanitized_name = context_name.lower().replace(" ", "_").replace("-", "_")
    output_file_name = f"{sanitized_name}.{object_type}.json"
    output_file_path = f"{output_directory}/{output_file_name}"

    # Save items to generated output file
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(
            items_to_save,
            json_file,
            ensure_ascii=False,
            indent=4)

    return output_file_name


def issue_to_dict(issue: Issue, config_repository: ConfigRepository):
    return {
        "number": issue.number,
        "organization_name": config_repository.owner,
        "repository_name": config_repository.name,
        "title": issue.title,
        "state": issue.state,
        "url": issue.url,
        "body": issue.body,
        # "created_at": issue.created_at,
        # "updated_at": issue.updated_at,
        # "closed_at": issue.closed_at,
        # "milestone_number": issue.milestone.number,
        # "milestone_title": issue.milestone.title,
        # "milestone_html_url": issue.milestone.html_url,
        "labels": issue.labels
        }

def make_issue_key(organization_name: str, repository_name: str, issue_number: int) -> str:
    """
       Creates a unique 3way string key for identifying every unique feature.

       @return: The unique string key for the feature.
    """
    return f"{organization_name}/{repository_name}/{issue_number}"


def make_string_key(issue: Issue) -> str:
    """
       Creates a unique 3way string key for identifying every unique feature.

       @return: The unique string key for the feature.
    """
    repository_id = issue.
    organization_name = issue.get("organization_name")
    repository_name = issue.get("repository_name")
    number = issue.get("number")

    string_key = f"{organization_name}/{repository_name}/{number}"

    return string_key


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes the provided filename by removing invalid characters and replacing spaces with underscores.

    @param filename: The filename to be sanitized.

    @return: The sanitized filename.
    """
    # Remove invalid characters for Windows filenames
    sanitized_name = re.sub(r'[<>:"/|?*`]', '', filename)
    # Reduce consecutive periods
    sanitized_name = re.sub(r'\.{2,}', '.', sanitized_name)
    # Reduce consecutive spaces to a single space
    sanitized_name = re.sub(r' {2,}', ' ', sanitized_name)
    # Replace space with '_'
    sanitized_name = sanitized_name.replace(' ', '_')

    return sanitized_name
