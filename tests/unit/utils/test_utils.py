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
import os

import pytest

from utils.utils import make_issue_key, sanitize_filename, generate_root_level_index_page, load_template, \
    make_absolute_path


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


# make_absolute_path


def test_make_absolute_path_with_relative_path():
    relative_path = "some/relative/path"
    expected = os.path.abspath(relative_path)
    assert make_absolute_path(relative_path) == expected

def test_make_absolute_path_with_absolute_path():
    absolute_path = os.path.abspath("already/absolute/path")
    assert make_absolute_path(absolute_path) == absolute_path


# generate_root_level_index_page


def test_generate_root_level_index_page(mocker):
    # Arrange
    index_root_level_page = "Root Level Template Content"
    output_path = "/base/output"

    mocker.patch("os.path.exists", return_value=False)  # Pretend the directory doesn't exist
    mocker.patch("os.makedirs")  # Prevent actual directory creation
    mock_open = mocker.patch("builtins.open", mocker.mock_open())   # Mock file open/write

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
