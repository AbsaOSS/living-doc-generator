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
import time

import pytest
from github import Github
from github.Rate import Rate
from github.RateLimit import RateLimit

from living_documentation_generator.utils.github_rate_limiter import GithubRateLimiter


@pytest.fixture
def rate_limiter(mocker, request):
    mock_github_client = mocker.Mock(spec=Github)
    mock_github_client.get_rate_limit.return_value = request.getfixturevalue("mock_rate_limiter")
    return GithubRateLimiter(mock_github_client)


@pytest.fixture
def mock_rate_limiter(mocker):
    mock_rate = mocker.Mock(spec=Rate)
    mock_rate.timestamp = mocker.Mock(return_value=time.time() + 3600)

    mock_core = mocker.Mock(spec=RateLimit)
    mock_core.reset = mock_rate

    mock = mocker.Mock(spec=GithubRateLimiter)
    mock.core = mock_core
    mock.core.remaining = 10

    return mock


@pytest.fixture
def mock_logging_setup(mocker):
    mock_log_config = mocker.patch("logging.basicConfig")
    yield mock_log_config
