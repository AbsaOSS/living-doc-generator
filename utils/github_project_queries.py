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
This module contains methods for formating the GitHub GraphQL queries.
"""
from utils.exceptions import InvalidQueryFormatError
from utils.utils import validate_query_format
from utils.constants import (
    PROJECTS_FROM_REPO_QUERY,
    ISSUES_FROM_PROJECT_QUERY,
    PROJECT_FIELD_OPTIONS_QUERY,
    ISSUES_PER_PAGE_LIMIT,
)

def validate_query_formats() -> bool:
    """
    Validate the format of the queries
    @return: True if the queries are in the correct format, False otherwise
    """
    try:
        validate_query_format(PROJECTS_FROM_REPO_QUERY, {"organization_name", "repository_name"})
        validate_query_format(ISSUES_FROM_PROJECT_QUERY, {"project_id", "issues_per_page", "after_argument"})
        validate_query_format(PROJECT_FIELD_OPTIONS_QUERY, {"organization_name", "repository_name", "project_number"})
    except InvalidQueryFormatError:
        return False
    return True

def get_projects_from_repo_query(organization_name: str, repository_name: str) -> str:
    """Update the placeholder values and formate the graphQL query"""
    return PROJECTS_FROM_REPO_QUERY.format(organization_name=organization_name, repository_name=repository_name)


def get_issues_from_project_query(project_id: str, after_argument: str) -> str:
    """Update the placeholder values and formate the graphQL query"""
    return ISSUES_FROM_PROJECT_QUERY.format(
        project_id=project_id, issues_per_page=ISSUES_PER_PAGE_LIMIT, after_argument=after_argument
    )


def get_project_field_options_query(organization_name: str, repository_name: str, project_number: int) -> str:
    """Update the placeholder values and formate the graphQL query"""
    return PROJECT_FIELD_OPTIONS_QUERY.format(
        organization_name=organization_name, repository_name=repository_name, project_number=project_number
    )
