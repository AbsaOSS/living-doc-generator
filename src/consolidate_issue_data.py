"""Consolidate Feature Data

This script is used to consolidate feature data with additional project data.
After merging datasets the output is one JSON file containing features with
additional project information.

The script can be run from the command line also with optional arguments:
    * python3 consolidate_issue_data.py
    * python3 consolidate_issue_data.py -c config.json
"""

import logging
import json
import os

from action.action_inputs import ActionInputs
from github_integration.model.consolidated_issue import ConsolidatedIssue
from utils import make_string_key, save_to_json_file, ensure_folder_exists

FETCHED_ISSUE_DIRECTORY = "../data/fetched_data/issue_data"
PROJECT_ISSUES_DATA_FILE = "../data/fetched_data/project_data/issues.projects.json"
CONSOLIDATED_OUTPUT_DIRECTORY = "../data/issue_consolidation"


def main() -> None:
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Script for consolidating issue data started.")

    # Load action inputs from the environment
    action_inputs = ActionInputs().load_from_environment()
    is_project_state_mining_enabled = action_inputs.is_project_state_mining_enabled

    # Check if the output directory exists and create it if not
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(CONSOLIDATED_OUTPUT_DIRECTORY, current_dir)

    consolidated_issues = {}

    # Load project issue data json and convert it into a dict with unique string key
    with open(PROJECT_ISSUES_DATA_FILE, 'r', encoding='utf-8') as project_issues_data_file:
        project_issues_data = json.load(project_issues_data_file)

    project_issues = {make_string_key(project_issue): project_issue for project_issue in project_issues_data}

    # Load every issue data file from fetched issue data directory
    for issue_file_name in os.listdir(FETCHED_ISSUE_DIRECTORY):
        logging.info(f"Loading issue data from: {issue_file_name}.")

        issue_file_path = os.path.join(FETCHED_ISSUE_DIRECTORY, issue_file_name)
        with open(issue_file_path, 'r', encoding='utf-8') as issue_data_file:
            issue_data = json.load(issue_data_file)

        if is_project_state_mining_enabled:
            consolidated_issues = {make_string_key(issue): ConsolidatedIssue().load_issue(issue)
                                   for issue in issue_data}

            # Update issues with project data
            for key in consolidated_issues.keys():
                if key in project_issues:
                    consolidated_issues[key].update_with_project_data(project_issues[key])

        else:
            consolidated_issues = {make_string_key(issue): ConsolidatedIssue().load_issue(issue).no_project_mining()
                                   for issue in issue_data}

    # Convert consolidated issues into dictionaries because they cannot be serialized to JSON directly
    consolidated_issues_to_save = [consolidated_issue.to_dict() for consolidated_issue in consolidated_issues.values()]
    logging.info(f"Consolidated `{len(consolidated_issues_to_save)}` issues in total and are ready to be saved.")

    # Save consolidated issues into one JSON file
    output_file_name = save_to_json_file(consolidated_issues_to_save, "consolidation", CONSOLIDATED_OUTPUT_DIRECTORY, "issue")
    logging.info(f"Consolidated issues saved into file: {output_file_name}.")

    logging.info("Script for consolidating issue data ended.")


if __name__ == '__main__':
    main()
