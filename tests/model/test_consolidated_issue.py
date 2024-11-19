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


# generate_page_filename


def test_generate_page_filename_correct_behaviour():
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    actual = consolidated_issue.generate_page_filename()

    assert "1_issue_title.md" == actual


def test_generate_page_filename_with_none_title(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.model.consolidated_issue.logger.error")
    mock_issue = Issue(None, None, {"number": 1, "title": None}, completed=True)
    consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    actual = consolidated_issue.generate_page_filename()

    assert "1.md" == actual
    mock_log_error.assert_called_once_with(
        "Issue page filename generation failed for Issue %s/%s (%s). Issue does not have a title.",
        "organization",
        "repository",
        1,
        exc_info=True,
    )


# generate_directory_path


def test_generate_directory_path_structured_output_disabled_grouping_by_topics_disabled(mocker):
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_output_directory",
        return_value="/base/output/path",
    )
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_is_structured_output_enabled", return_value=False
    )
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    actual = consolidated_issue.generate_directory_path("issue table")

    assert ["/base/output/path"] == actual


def test_generate_directory_path_structured_output_enabled_grouping_by_topics_disabled(mocker):
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_output_directory",
        return_value="/base/output/path",
    )
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_is_structured_output_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_is_grouping_by_topics_enabled",
        return_value=False,
    )
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    actual = consolidated_issue.generate_directory_path("issue table")

    assert ["/base/output/path/organization/repository"] == actual


def test_generate_directory_path_structured_output_disabled_grouping_by_topics_enabled_two_issue_topics(mocker):
    mock_log_debug = mocker.patch("living_documentation_generator.model.consolidated_issue.logger.debug")
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_output_directory",
        return_value="/base/output/path",
    )
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_is_structured_output_enabled", return_value=False
    )
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True
    )
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    actual = consolidated_issue.generate_directory_path("| Labels | feature, BETopic, FETopic |")

    assert ["/base/output/path/BETopic", "/base/output/path/FETopic"] == actual
    mock_log_debug.assert_called_once_with(
        "Multiple Topic labels found for Issue #%s: %s (%s): %s",
        1,
        "Issue Title",
        "organization/repository",
        "BETopic, FETopic",
    )


def test_generate_directory_path_structured_output_disabled_grouping_by_topics_enabled_no_issue_topics(mocker):
    mock_log_error = mocker.patch("living_documentation_generator.model.consolidated_issue.logger.error")
    mock_log_debug = mocker.patch("living_documentation_generator.model.consolidated_issue.logger.debug")
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_output_directory",
        return_value="/base/output/path",
    )
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_is_structured_output_enabled", return_value=False
    )
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True
    )
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    actual = consolidated_issue.generate_directory_path("| Labels | feature, bug |")

    assert ["/base/output/path/NoTopic"] == actual
    mock_log_error.assert_called_once_with(
        "No Topic label found for Issue #%i: %s (%s)", 1, "Issue Title", "organization/repository"
    )
    mock_log_debug.assert_not_called()


def test_generate_directory_path_structured_output_enabled_grouping_by_topics_enabled_one_issue_topic(mocker):
    mock_log_debug = mocker.patch("living_documentation_generator.model.consolidated_issue.logger.debug")
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_output_directory",
        return_value="/base/output/path",
    )
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_is_structured_output_enabled", return_value=True
    )
    mocker.patch(
        "living_documentation_generator.action_inputs.ActionInputs.get_is_grouping_by_topics_enabled", return_value=True
    )
    mock_issue = Issue(None, None, {"number": 1, "title": "Issue Title"}, completed=True)
    consolidated_issue = ConsolidatedIssue("organization/repository", mock_issue)

    actual = consolidated_issue.generate_directory_path("| Labels | feature, BETopic, FETopic |")

    assert [
        "/base/output/path/organization/repository/BETopic",
        "/base/output/path/organization/repository/FETopic",
    ] == actual
    mock_log_debug.assert_called_once_with(
        "Multiple Topic labels found for Issue #%s: %s (%s): %s",
        1,
        "Issue Title",
        "organization/repository",
        "BETopic, FETopic",
    )
