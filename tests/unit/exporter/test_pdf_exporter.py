import unittest

from github.Issue import Issue

from living_documentation_regime.exporter.pdf_exporter import PDFExporter
from living_documentation_regime.model.consolidated_issue import ConsolidatedIssue
from unittest.mock import Mock

class MyTestCase(unittest.TestCase):
    def test_something(self):
        repository_issue=Mock(spec=Issue)
        issues: dict[str, ConsolidatedIssue] = {
            "issue1": ConsolidatedIssue(
                repository_id="A",
                repository_issue=repository_issue
            ),
            "issue2": ConsolidatedIssue(
                repository_id="B",
                repository_issue=repository_issue
            ),
        }
        exporter = PDFExporter("pdftest.pdf")
        exporter.export(issues=issues)


if __name__ == '__main__':
    unittest.main()
