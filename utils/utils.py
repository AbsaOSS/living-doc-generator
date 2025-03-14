#
# Copyright 2024 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
This module contains utility functions used across the project.
"""

import os
import re
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def make_issue_key(organization_name: str, repository_name: str, issue_number: int) -> str:
    """
    Create a unique string key for identifying the issue.

    @param organization_name: The name of the organization where issue is located at.
    @param repository_name: The name of the repository where issue is located at.
    @param issue_number: The number of the issue.
    @return: The unique string key for the issue.
    """
    return f"{organization_name}/{repository_name}/{issue_number}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize the provided filename by removing invalid characters.

    @param filename: The filename to sanitize.
    @return: The sanitized filename
    """
    # Remove invalid characters for Windows filenames
    sanitized_name = re.sub(r'[<>:"/|?*#{}()`]', "", filename)
    # Reduce consecutive periods
    sanitized_name = re.sub(r"\.{2,}", ".", sanitized_name)
    # Reduce consecutive spaces to a single space
    sanitized_name = re.sub(r" {2,}", " ", sanitized_name)
    # Replace space with '_'
    sanitized_name = sanitized_name.replace(" ", "_")

    return sanitized_name


def make_absolute_path(path: str) -> str:
    """
    Convert the provided path to an absolute path.

    @param path: The path to convert.
    @return: The absolute path.
    """
    # If the path is already absolute, return it as is
    if os.path.isabs(path):
        return path
    # Otherwise, convert the relative path to an absolute path
    return os.path.abspath(path)


def validate_query_format(query_string, expected_placeholders) -> None:
    """
    Validate the placeholders in the query string.
    Check if all the expected placeholders are present in the query and exit if not.

    @param query_string: The query string to validate.
    @param expected_placeholders: The set of expected placeholders in the query.
    @return: None
    """
    actual_placeholders = set(re.findall(r"\{(\w+)\}", query_string))
    missing = expected_placeholders - actual_placeholders
    extra = actual_placeholders - expected_placeholders
    if missing or extra:
        missing_message = f"Missing placeholders: {missing}. " if missing else ""
        extra_message = f"Extra placeholders: {extra}." if extra else ""
        logger.error("%s%s\nFor the query: %s", missing_message, extra_message, query_string)
        sys.exit(1)


def generate_root_level_index_page(index_root_level_page: str, output_path: str) -> None:
    """
    Generate the root level index page for the output living documentation.

    @param index_root_level_page: The content of the root level index page.
    @param output_path: The path to the output directory.
    @return: None
    """
    with open(os.path.join(output_path, "_index.md"), "w", encoding="utf-8") as f:
        f.write(index_root_level_page)


def load_template(file_path: str, error_message: str) -> Optional[str]:
    """
    Load the content of the template file.

    @param file_path: The path to the template file.
    @param error_message: The error message to log if the file cannot be read.
    @return: The content of the template file or None if the file cannot be read.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except IOError:
        logger.error(error_message, exc_info=True)
        return None


# GitHub action utils
def get_action_input(name: str, default: Optional[str] = None) -> str:
    """
    Get the input value from the environment variables.

    @param name: The name of the input parameter.
    @param default: The default value to return if the environment variable is not set.
    @return: The value of the specified input parameter, or an empty string
    """
    logger.debug(f"XXX all os envs: {os.environ}")

    return os.getenv(f'INPUT_{name.replace("-", "_").upper()}', default=default)


def set_action_output(name: str, value: str, default_output_path: str = "default_output.txt") -> None:
    """
    Write an action output to a file in the format expected by GitHub Actions.

    This function writes the output in a specific format that includes the name of the
    output and its value. The output is appended to the specified file.

    @param name: The name of the output parameter.
    @param value: The value of the output parameter.
    @param default_output_path: The default file path to which the output is written if the
    @return: None
    """
    output_file = os.getenv("GITHUB_OUTPUT", default_output_path)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(f"{name}={value}\n")


def set_action_failed(message: str) -> None:
    """
    Set the action as failed with the provided message.

    @param message: The error message to display.
    @return: None
    """
    print(f"::error::{message}")
    sys.exit(1)
