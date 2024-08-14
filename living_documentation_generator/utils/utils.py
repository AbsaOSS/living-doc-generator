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

logger = logging.getLogger(__name__)


def make_issue_key(organization_name: str, repository_name: str, issue_number: int) -> str:
    """
    Create a unique string key for identifying the issue.

    Args:
        organization_name (str): The name of the organization where issue is located at.
        repository_name (str): The name of the repository where issue is located at.
        issue_number (int): The number of the issue.
    """
    return f"{organization_name}/{repository_name}/{issue_number}"


def sanitize_filename(filename: str) -> str:
    """Sanitize the provided filename by removing invalid characters."""
    # Remove invalid characters for Windows filenames
    sanitized_name = re.sub(r'[<>:"/|?*`]', "", filename)
    # Reduce consecutive periods
    sanitized_name = re.sub(r"\.{2,}", ".", sanitized_name)
    # Reduce consecutive spaces to a single space
    sanitized_name = re.sub(r" {2,}", " ", sanitized_name)
    # Replace space with '_'
    sanitized_name = sanitized_name.replace(" ", "_")

    return sanitized_name


def make_absolute_path(path: str) -> str:
    """Convert the provided path to an absolute path."""
    # If the path is already absolute, return it as is
    if os.path.isabs(path):
        return path
    # Otherwise, convert the relative path to an absolute path
    return os.path.abspath(path)


# Github
def get_action_input(name: str, default: str = None) -> str:
    """Get the input value from the environment variables."""
    return os.getenv(f"INPUT_{name}", default)


# pylint: disable=fixme
def set_action_output(name: str, value: str, default_output_path: str = "default_output.txt") -> None:
    """TODO: IDK"""
    output_file = os.getenv("GITHUB_OUTPUT", default_output_path)
    with open(output_file, "a", encoding="utf-8") as f:
        # Write the multiline output to the file
        f.write(f"{name}<<EOF\n")
        f.write(f"{value}")
        f.write("EOF\n")


def set_action_failed(message: str):
    """Set the action as failed with the provided message."""
    # TODO: might need a print value to work: check again at Integration testing
    logger.error("::error:: %s", message)
    sys.exit(1)
