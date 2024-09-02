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
This module contains a GitHub Rate Limiter class methods,
which acts as a rate limiter for GitHub API calls.
"""

import logging
import time
from datetime import datetime
from typing import Callable, Optional, Any
from github import Github

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
# It is fine to have a single method in this class, since we use it as a callable class
class GithubRateLimiter:
    """
    A class that acts as a rate limiter for GitHub API calls.

    Note:
        This class is used as a callable class, hence the `__call__` method.
    """

    def __init__(self, github_client: Github):
        self.__github_client: Github = github_client

    @property
    def github_client(self) -> Github:
        """Getter of the GitHub client."""
        return self.__github_client

    def __call__(self, method: Callable) -> Callable:
        """
        Wraps the provided method to ensure it respects the GitHub API rate limit.

        @param method: The method to wrap.
        @return: The wrapped method.
        """

        def wrapped_method(*args, **kwargs) -> Optional[Any]:
            rate_limit = self.github_client.get_rate_limit().core
            remaining_calls = rate_limit.remaining
            reset_time = rate_limit.reset.timestamp()

            if remaining_calls < 5:
                logger.info("Rate limit almost reached. Sleeping until reset time.")
                sleep_time = reset_time - (now := time.time())
                while sleep_time <= 0:
                    # Note: received values can be in the past, so the time shift to 1st positive value is needed
                    reset_time += 3600  # Add 1 hour in seconds
                    sleep_time = reset_time - now

                total_sleep_time = sleep_time + 5  # Total sleep time including the additional 5 seconds
                hours, remainder = divmod(total_sleep_time, 3600)
                minutes, seconds = divmod(remainder, 60)

                logger.info(
                    "Sleeping for %s hours, %s minutes, and %s seconds until %s.",
                    int(hours),
                    int(minutes),
                    int(seconds),
                    datetime.fromtimestamp(reset_time).strftime("%Y-%m-%d %H:%M:%S"),
                )
                time.sleep(sleep_time + 5)  # Sleep for the calculated time plus 5 seconds

            return method(*args, **kwargs)

        return wrapped_method
