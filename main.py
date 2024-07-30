import logging

from github import Github, Auth

from living_documentation_generator.action_inputs import ActionInputs
from living_documentation_generator.generator import LivingDocumentationGenerator
from living_documentation_generator.github_projects import GithubProjects
from living_documentation_generator.utils.utils import set_action_output

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ISSUES_PER_PAGE_LIMIT = 100


def run():
    action_inputs = ActionInputs().load_from_environment()

    github = Github(auth=Auth.Token(token=action_inputs.github_token), per_page=ISSUES_PER_PAGE_LIMIT)
    github_projects = GithubProjects(token=action_inputs.github_token)

    generator = LivingDocumentationGenerator(
        github_instance=github,
        github_projects_instance=github_projects,
        repositories=action_inputs.repositories,
        projects_title_filter=action_inputs.projects_title_filter,
        project_state_mining_enabled=action_inputs.is_project_state_mining_enabled,
        output_path=action_inputs.output_directory
    )

    generator.generate()

    # Set the output for the GitHub Action
    set_action_output('output-path', generator.output_path)


if __name__ == '__main__':
    print("Starting Living Documentation generation.")
    run()
    print("Living Documentation generation completed.")
