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

import re

from living_documentation_generator.utils.constants import (
    PROJECTS_FROM_REPO_QUERY,
    ISSUES_FROM_PROJECT_QUERY,
    PROJECT_FIELD_OPTIONS_QUERY,
    ISSUES_PER_PAGE_LIMIT,
)
from living_documentation_generator.utils.github_project_queries import (
    get_projects_from_repo_query,
    get_issues_from_project_query,
    get_project_field_options_query,
)


# get_projects_from_repo_query


def test_get_projects_from_repo_query():
    organization_name = "test_org"
    repository_name = "test_repo"
    expected_query = PROJECTS_FROM_REPO_QUERY.format(
        organization_name=organization_name, repository_name=repository_name
    )

    actual_query = get_projects_from_repo_query(organization_name, repository_name)

    assert actual_query == expected_query
    leftover_placeholders = re.findall(r"\{\w+\}", actual_query)
    assert not leftover_placeholders


# get_issues_from_project_query


def test_get_issues_from_project_query():
    project_id = "test_project_id"
    after_argument = "test_after_argument"
    expected_query = ISSUES_FROM_PROJECT_QUERY.format(
        project_id=project_id, issues_per_page=ISSUES_PER_PAGE_LIMIT, after_argument=after_argument
    )

    actual_query = get_issues_from_project_query(project_id, after_argument)

    assert actual_query == expected_query
    leftover_placeholders = re.findall(r"\{\w+\}", actual_query)
    assert not leftover_placeholders


# get_project_field_options_query


def test_get_project_field_options_query():
    organization_name = "test_org"
    repository_name = "test_repo"
    project_number = 1
    expected_query = PROJECT_FIELD_OPTIONS_QUERY.format(
        organization_name=organization_name, repository_name=repository_name, project_number=project_number
    )

    actual_query = get_project_field_options_query(organization_name, repository_name, project_number)

    assert actual_query == expected_query
    leftover_placeholders = re.findall(r"\{\w+\}", actual_query)
    assert not leftover_placeholders
