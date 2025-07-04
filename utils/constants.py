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
This module centralises all constants used across the project.
"""

# General Action inputs
GITHUB_TOKEN = "GITHUB_TOKEN"
REPORT_PAGE = "REPORT_PAGE"
VERBOSE_LOGGING = "VERBOSE_LOGGING"
RELEASE = "RELEASE"
SOURCE = "SOURCE"
STRUCTURED_OUTPUT = "STRUCTURED_OUTPUT"

# Regime output paths
GENERATOR_OUTPUT_PATH = "generator"

# GitHub API constants
ISSUES_PER_PAGE_LIMIT = 100
ISSUE_STATE_ALL = "all"

# Table headers for Index page
TABLE_HEADER_WITH_PROJECT_DATA = """
| Organization name | Repository name | Issue 'Number - Title' |Linked to project | Project status | Issue URL |
|-------------------|-----------------|------------------------|------------------|----------------|-----------|
"""
TABLE_HEADER_WITHOUT_PROJECT_DATA = """
| Organization name | Repository name | Issue 'Number - Title' | Issue state | Issue URL |
|-------------------|-----------------|------------------------|-------------|-----------|
"""

# Table header for Report page
REPORT_PAGE_HEADER = """
| Error Type | Source | Message |
| ---------- | ------ | ------- |
"""

# Constant to symbolize if issue is linked to a project
LINKED_TO_PROJECT_TRUE = "🟢"
LINKED_TO_PROJECT_FALSE = "🔴"
