import logging

from living_documentation_generator.action_inputs import ActionInputs
from living_documentation_generator.generator import LivingDocumentationGenerator
from living_documentation_generator.utils.utils import set_action_output
from living_documentation_generator.utils.logging_config import setup_logging


def run():
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting Living Documentation generation.")
    action_inputs = ActionInputs().load_from_environment()

    generator = LivingDocumentationGenerator(
        github_token=action_inputs.github_token,
        repositories=action_inputs.repositories,
        project_state_mining_enabled=action_inputs.is_project_state_mining_enabled,
        output_path=action_inputs.output_directory,
    )

    generator.generate()

    # Set the output for the GitHub Action
    set_action_output("output-path", generator.output_path)
    logger.info(
        "Living Documentation generation - output path set to `%s`.",
        generator.output_path,
    )

    logger.info("Living Documentation generation completed.")


if __name__ == "__main__":
    run()
