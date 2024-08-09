import logging

from github import Github, Auth

from living_documentation_generator.action_inputs import ActionInputs
from living_documentation_generator.generator import LivingDocumentationGenerator
from living_documentation_generator.github_projects import GithubProjects
from living_documentation_generator.utils.utils import set_action_output
from living_documentation_generator.utils.logging_config import setup_logging
from living_documentation_generator.utils.constants import Constants


def run():
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting Living Documentation generation.")
    action_inputs = ActionInputs().load_from_environment()

    github = Github(auth=Auth.Token(token=action_inputs.github_token), per_page=Constants.ISSUES_PER_PAGE_LIMIT)
    github_projects = GithubProjects(token=action_inputs.github_token)

    generator = LivingDocumentationGenerator(
        github_instance=github,
        github_projects_instance=github_projects,
        repositories=action_inputs.repositories,
        project_state_mining_enabled=action_inputs.is_project_state_mining_enabled,
        output_path=action_inputs.output_directory
    )

    generator.generate()

    # Set the output for the GitHub Action
    set_action_output('output-path', generator.output_path)
    logger.info("Living Documentation generation - output path set to `%s`.", generator.output_path)

    logger.info("Living Documentation generation completed.")


if __name__ == '__main__':
    run()
