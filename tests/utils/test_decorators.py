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
from github import GithubException
from requests import RequestException

from living_documentation_generator.utils.decorators import debug_log_decorator, safe_call_decorator


# sample function to be decorated
def sample_function(x, y):
    return x + y


# debug_log_decorator


def test_debug_log_decorator(mocker):
    # Mock logging
    mock_log_debug = mocker.patch("living_documentation_generator.utils.decorators.logger.debug")

    decorated_function = debug_log_decorator(sample_function)
    expected_call = [
        mocker.call("Calling method %s with args: %s and kwargs: %s.", "sample_function", (3, 4), {}),
        mocker.call("Method %s returned %s.", "sample_function", 7),
    ]

    actual = decorated_function(3, 4)

    assert actual == 7
    assert mock_log_debug.call_args_list == expected_call


# safe_call_decorator


def test_safe_call_decorator_success(rate_limiter):
    @safe_call_decorator(rate_limiter)
    def sample_method(x, y):
        return x + y

    actual = sample_method(2, 3)

    assert actual == 5


def test_safe_call_decorator_network_error(rate_limiter, mocker):
    mock_log_error = mocker.patch("living_documentation_generator.utils.decorators.logger.error")

    @safe_call_decorator(rate_limiter)
    def sample_method():
        raise ConnectionError("Test connection error")

    actual = sample_method()

    assert actual is None
    assert mock_log_error.call_count == 1

    args, kwargs = mock_log_error.call_args
    assert args[0] == "Network error calling %s: %s."
    assert args[1] == "sample_method"
    assert isinstance(args[2], ConnectionError)
    assert str(args[2]) == "Test connection error"
    assert kwargs['exc_info']


def test_safe_call_decorator_github_api_error(rate_limiter, mocker):
    mock_log_error = mocker.patch("living_documentation_generator.utils.decorators.logger.error")

    @safe_call_decorator(rate_limiter)
    def sample_method():
        raise GithubException(status=404)

    actual = sample_method()

    assert actual is None
    assert mock_log_error.call_count == 1

    args, kwargs = mock_log_error.call_args
    assert args[0] == 'GitHub API error calling %s: %s.'
    assert args[1] == "sample_method"
    assert isinstance(args[2], GithubException)
    assert str(args[2]) == "404"
    assert kwargs['exc_info']


def test_safe_call_decorator_http_error(mocker, rate_limiter):
    mock_log_error = mocker.patch("living_documentation_generator.utils.decorators.logger.error")

    @safe_call_decorator(rate_limiter)
    def sample_method():
        raise RequestException("Test HTTP error")

    actual = sample_method()

    assert actual is None
    assert mock_log_error.call_count == 1

    args, kwargs = mock_log_error.call_args
    assert args[0] == "HTTP error calling %s: %s."
    assert args[1] == "sample_method"
    assert isinstance(args[2], RequestException)
    assert str(args[2]) == "Test HTTP error"
    assert kwargs['exc_info']


def test_safe_call_decorator_exception(rate_limiter, mocker):
    mock_log_error = mocker.patch("living_documentation_generator.utils.decorators.logger.error")

    @safe_call_decorator(rate_limiter)
    def sample_method(x, y):
        return x / y

    actual = sample_method(2, 0)

    assert actual is None
    mock_log_error.assert_called_once()
    exception_message = mock_log_error.call_args[0][0]
    assert "%s by calling %s: %s." in exception_message
    exception_type = mock_log_error.call_args[0][1]
    assert "ZeroDivisionError" in exception_type
    method_name = mock_log_error.call_args[0][2]
    assert "sample_method" in method_name



