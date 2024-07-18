"""Utility Functions

This script contains helper functions that are used across multiple living_documentation_generator in this project.

These functions can be imported and used in other living_documentation_generator as needed.
"""

import re


def make_issue_key(organization_name: str, repository_name: str, issue_number: int) -> str:
    """
       Creates a unique 3way string key for identifying every unique feature.

       @return: The unique string key for the feature.
    """
    return f"{organization_name}/{repository_name}/{issue_number}"


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
