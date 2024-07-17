"""Clean environment before mining

This script is used to clean up the environment before mining data. It removes
files, links, and content from specified directories.

The script can be run from the command line:
    * python3 clean_env_before_mining.py
"""
import logging
import os
import shutil

from action.action_inputs import ActionInputs

DATA_DIRECTORY = "../data"
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_directory_content(script_dir: str, directory: str) -> None:
    """
        Deletes all content from the specified directory.

        @param script_dir: The directory of the current script.
        @param directory: The directory to be cleaned.

        @return: None
    """

    # Get the absolute path of the directory
    directory_path = os.path.join(script_dir, directory)
    logging.info(f"Cleaning path: {directory_path}")

    # Check if the directory exists
    if os.path.exists(directory_path):
        # Delete all content from the directory
        shutil.rmtree(directory_path)


def main() -> None:
    logging.info("Cleaning environment for the Living Doc Generator")

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load action inputs from the environment
    action_inputs = ActionInputs().load_from_environment()
    output_directory = action_inputs.output_directory

    # Clean the directory content for generated data and output
    clean_directory_content(script_dir, DATA_DIRECTORY)
    clean_directory_content(script_dir, output_directory)

    logging.info("Cleaning environment for Living Documentation ended")


if __name__ == "__main__":
    main()
