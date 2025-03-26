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

import pytest

from utils.exceptions import LivDocInvalidQueryFormatError
from utils.utils import (
    make_issue_key,
    sanitize_filename,
    validate_query_format,
    get_action_input,
    set_action_output,
    load_template, generate_root_level_index_page,
)


# make_issue_key


def test_make_issue_key():
    organization_name = "org"
    repository_name = "repo"
    issue_number = 123

    expected_key = "org/repo/123"
    actual_key = make_issue_key(organization_name, repository_name, issue_number)

    assert expected_key == actual_key


# sanitize_filename


@pytest.mark.parametrize(
    "filename_example, expected_filename",
    [
        ("in<>va::l#(){}id//.fi|le?*.txt", "invalid.file.txt"),  # Remove invalid characters for Windows filenames
        ("another..invalid...filename.txt", "another.invalid.filename.txt"),  # Reduce consecutive periods
        (
            "filename   with   spaces.txt",
            "filename_with_spaces.txt",
        ),  # Reduce consecutive spaces to a single space and replace spaces with '_'
    ],
)
def test_sanitize_filename(filename_example, expected_filename):
    actual_filename = sanitize_filename(filename_example)
    assert expected_filename == actual_filename


# GitHub action utils
# get_action_input


def test_get_input_with_hyphen(mocker):
    mock_getenv = mocker.patch("os.getenv", return_value="test_value")

    actual = get_action_input("test-input", default=None)

    mock_getenv.assert_called_with("INPUT_TEST_INPUT", default=None)
    assert "test_value" == actual


def test_get_input_without_hyphen(mocker):
    mock_getenv = mocker.patch("os.getenv", return_value="another_test_value")

    actual = get_action_input("anotherinput", default=None)

    mock_getenv.assert_called_with("INPUT_ANOTHERINPUT", default=None)
    assert "another_test_value" == actual


# validate_query_format


def test_validate_query_format_right_behaviour(mocker):
    mock_log_error = mocker.patch("utils.utils.logger.error")

    # Test case where there are no missing or extra placeholders
    query_string = "This is a query with placeholders {placeholder1} and {placeholder2}"
    expected_placeholders = {"placeholder1", "placeholder2"}
    validate_query_format(query_string, expected_placeholders)
    mock_log_error.assert_not_called()


def test_validate_query_format_missing_placeholder(mocker):
    mock_log_error = mocker.patch("utils.utils.logger.error")

    # Test case where there are missing placeholders
    query_string = "This is a query with placeholders {placeholder1} and {placeholder2}"
    expected_placeholders = {"placeholder1", "placeholder2", "placeholder3"}
    with pytest.raises(LivDocInvalidQueryFormatError):
        validate_query_format(query_string, expected_placeholders)
        mock_log_error.assert_called_with(
            "%s%s\nFor the query: %s",
            "Missing placeholders: {'placeholder3'}. ",
            "",
            "This is a query with placeholders {placeholder1} and {placeholder2}",
        )


def test_validate_query_format_extra_placeholder(mocker):
    mock_log_error = mocker.patch("utils.utils.logger.error")

    # Test case where there are extra placeholders
    query_string = "This is a query with placeholders {placeholder1} and {placeholder2}"
    expected_placeholders = {"placeholder1"}
    with pytest.raises(LivDocInvalidQueryFormatError):
        validate_query_format(query_string, expected_placeholders)
        mock_log_error.assert_called_with(
            "%s%s\nFor the query: %s",
            "",
            "Extra placeholders: {'placeholder2'}.",
            "This is a query with placeholders {placeholder1} and {placeholder2}",
        )


# set_action_output


def test_set_output_default(mocker):
    mocker.patch("os.getenv", return_value="default_output.txt")
    mock_open = mocker.patch("builtins.open", new_callable=mocker.mock_open)

    set_action_output("test-output", "test_value")

    mock_open.assert_called_with("default_output.txt", "a", encoding="utf-8")
    handle = mock_open()
    handle.write.assert_any_call("test-output=test_value\n")


def test_set_output_custom_path(mocker):
    mocker.patch("os.getenv", return_value="custom_output.txt")
    mock_open = mocker.patch("builtins.open", new_callable=mocker.mock_open)

    set_action_output("custom-output", "custom_value", "default_output.txt")

    mock_open.assert_called_with("custom_output.txt", "a", encoding="utf-8")
    handle = mock_open()
    handle.write.assert_any_call("custom-output=custom_value\n")




# generate_root_level_index_page


def test_generate_root_level_index_page(mocker):
    # Arrange
    index_root_level_page = "Root Level Template Content"
    output_path = "/base/output"
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    # Act
    generate_root_level_index_page(index_root_level_page, output_path)

    # Assert
    mock_open.assert_called_with("/base/output/_index.md", "w", encoding="utf-8")
    handle = mock_open()
    handle.write.assert_called_with(index_root_level_page)


# load_template


def test_load_template(mocker):
    # Arrange
    file_path = "templates/test_template.html"
    error_message = "Template file was not successfully loaded."
    expected_content = "Template Content"
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data=expected_content))

    # Act
    actual_content = load_template(file_path, error_message)

    # Assert
    mock_open.assert_called_with(file_path, "r", encoding="utf-8")
    assert actual_content == expected_content


def test_load_template_error(mocker):
    # Arrange
    file_path = "templates/non_existent_template.html"
    error_message = "Template file was not successfully loaded."
    mock_open = mocker.patch("builtins.open", side_effect=FileNotFoundError)
    mock_logger = mocker.patch("utils.utils.logger")

    # Act
    result = load_template(file_path, error_message)

    # Assert
    assert result is None
    mock_open.assert_called_with(file_path, "r", encoding="utf-8")
    mock_logger.error.assert_called_with(error_message, exc_info=True)
