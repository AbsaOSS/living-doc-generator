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
from github.Issue import Issue

from living_documentation_generator.model.consolidated_issue import ConsolidatedIssue
from living_documentation_generator.model.project_status import ProjectStatus


# update_with_project_data


# THIS MIGHT NOT BE NEEDED, SINCE WE TEST ASSIGN AND APPEND
def test_update_with_project_data_correct_behaviour():
    actual_consolidated_issue = ConsolidatedIssue("organization/repo")
    project_status = ProjectStatus()

    actual_consolidated_issue.update_with_project_data(project_status)

    assert actual_consolidated_issue.linked_to_project
    assert actual_consolidated_issue.project_issue_statuses == [project_status]


# generate_page_filename


def test_generate_page_filename_correct_behaviour():
    mock_issue = Issue(None, None, {"number": 1, "title": None}, completed=True)
    consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    actual = consolidated_issue.generate_page_filename()

    assert actual == "1.md"


def test_generate_page_filename_with_none_title(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.model.consolidated_issue.logger.error")
    mock_issue = Issue(None, None, {"number": 1, "title": None}, completed=True)
    consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    actual = consolidated_issue.generate_page_filename()

    assert actual == "1.md"
    mock_log_error.assert_called_once_with(
        "Issue page filename generation failed for Issue %s/%s (%s). Issue does not have a title.",
        "organization",
        "repository",
        1,
        exc_info=True,
    )
