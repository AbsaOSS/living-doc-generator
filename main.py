import logging
import os

from typing import Optional

from github import Github, Auth

from living_documentation_generator.action.action_inputs import ActionInputs
from living_documentation_generator.generator import LivingDocumentationGenerator
from living_documentation_generator.github_integration.gh_action import set_action_output
from living_documentation_generator.github_integration.github_manager import GithubManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ISSUES_PER_PAGE_LIMIT = 100


def run():
    action_inputs = ActionInputs().load_from_environment()
    output_path = f"../{action_inputs.output_directory}"

    GithubManager().initialize_github_instance(action_inputs.github_token, ISSUES_PER_PAGE_LIMIT)
    if action_inputs.is_project_state_mining_enabled:
        GithubManager().initialize_request_session(action_inputs.github_token)

    (ldg := LivingDocumentationGenerator(
        repositories=action_inputs.repositories,
        projects_title_filter=action_inputs.projects_title_filter,
        project_state_mining_enabled=action_inputs.is_project_state_mining_enabled,
        output_path=output_path
    )).generate()

    # Set the output for the GitHub Action
    set_action_output('release-notes', ldg.output_path)


if __name__ == '__main__':
    print("Starting Living Documentation generation.")
    run()
    print("Living Documentation generation completed.")
