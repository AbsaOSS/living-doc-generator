# Copyright 2025 ABSA Group Limited
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
This module contains the abstract Output Factory class which is
responsible for generating outputs in the correct format.
"""

import logging

from abc import ABC, abstractmethod
from living_documentation_regime.model.consolidated_issue import ConsolidatedIssue

logger = logging.getLogger(__name__)


class OutputFactory(ABC):
    """An abstract class representing the Output Factory."""

    @abstractmethod
    def generate_output(self, issues: dict[str, ConsolidatedIssue]) -> None:
        """
        An abstract method for generating the output in the correct format.

        @param issues: The data to be saved in the output.
        @return: None
        """
