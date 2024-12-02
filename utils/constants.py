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
This module contains all constants used across the project.
"""
# Default output path for the generated documentation
OUTPUT_PATH = "./output"

# Action inputs environment variables
GITHUB_TOKEN = "GITHUB_TOKEN"
PROJECT_STATE_MINING = "LIV_DOC_PROJECT_STATE_MINING"
REPOSITORIES = "LIV_DOC_REPOSITORIES"
STRUCTURED_OUTPUT = "LIV_DOC_STRUCTURED_OUTPUT"
GROUP_OUTPUT_BY_TOPICS = "LIV_DOC_GROUP_OUTPUT_BY_TOPICS"

# Mining Regimes
LIV_DOC_REGIME = "LIV_DOC_REGIME"
# CI_REGIME = "CI_REGIME"

# GitHub API constants
ISSUES_PER_PAGE_LIMIT = 100
ISSUE_STATE_ALL = "all"
PROJECTS_FROM_REPO_QUERY = """
                query {{
                  repository(owner: "{organization_name}", name: "{repository_name}") {{
                    projectsV2(first: 100) {{
                      nodes {{
                        id
                        number
                        title
                      }}
                    }}
                  }}
                }}
                """
ISSUES_FROM_PROJECT_QUERY = """
                query {{
                  node(id: "{project_id}") {{
                    ... on ProjectV2 {{
                      items(first: {issues_per_page}, {after_argument}) {{
                        pageInfo {{
                          endCursor
                          hasNextPage
                        }}
                        nodes {{
                          content {{
                              ... on Issue {{
                                title
                                state
                                number
                                repository {{
                                  name
                                  owner {{
                                    login
                                  }}
                                }}
                              }}
                            }}
                          fieldValues(first: 100) {{
                            nodes {{
                              __typename
                              ... on ProjectV2ItemFieldSingleSelectValue {{
                                name
                              }}
                            }}
                          }}
                        }}
                      }}
                    }}
                  }}
                }}
                """
PROJECT_FIELD_OPTIONS_QUERY = """
                query {{
                  repository(owner: "{organization_name}", name: "{repository_name}") {{
                    projectV2(number: {project_number}) {{
                      title
                      fields(first: 100) {{
                        nodes {{
                          ... on ProjectV2SingleSelectField {{
                            name
                            options {{
                              name
                            }}
                          }}
                        }}
                      }}
                    }}
                  }}
                }}
                """

# Table headers for Index page
TABLE_HEADER_WITH_PROJECT_DATA = """
| Organization name | Repository name | Issue 'Number - Title' |Linked to project | Project status | Issue URL |
|-------------------|-----------------|------------------------|------------------|----------------|-----------|
"""
TABLE_HEADER_WITHOUT_PROJECT_DATA = """
| Organization name | Repository name | Issue 'Number - Title' | Issue state | Issue URL |
|-------------------|-----------------|------------------------|-------------|-----------|
"""


# Symbol, when no project is attached to an issue
NO_PROJECT_DATA = "---"

# Constant to symbolize if issue is linked to a project
LINKED_TO_PROJECT_TRUE = "🟢"
LINKED_TO_PROJECT_FALSE = "🔴"
