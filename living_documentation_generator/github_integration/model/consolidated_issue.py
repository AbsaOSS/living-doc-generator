from living_documentation_generator.github_integration.model.issue import Issue
from living_documentation_generator.github_integration.model.project_issue import ProjectIssue
from living_documentation_generator.utils import sanitize_filename

NOT_SET_FOR_NOW = "NOT_SET_IN_THIS_VERSION"
NO_PROJECT_ATTACHED = "---"
NO_PROJECT_MINING = "-?-"


class ConsolidatedIssue:
    def __init__(self, repository_id: str, repo_issue: Issue = None):
        # TODO: finish all the fields with newer version
        # Main issue structure
        self.__number: int = repo_issue.number if repo_issue else 0

        parts = repository_id.split("/")
        self.__organization_name: str = parts[0] if len(parts) == 2 else ""
        self.__repository_name: str = parts[1] if len(parts) == 2 else ""
        self.__title: str = repo_issue.title if repo_issue else ""
        self.__state: str = repo_issue.state if repo_issue else ""
        self.__url: str = repo_issue.url if repo_issue else ""
        self.__body: str = repo_issue.body if repo_issue else ""
        # self.created_at: str = NOT_SET_FOR_NOW
        # self.updated_at: str = NOT_SET_FOR_NOW
        # self.closed_at: str = NOT_SET_FOR_NOW
        # self.milestone: str = NOT_SET_FOR_NOW
        self.__labels: list[str] = repo_issue.labels if repo_issue else []

        # Extra project data
        self.__linked_to_project: bool = False
        self.__project_name: str = NO_PROJECT_ATTACHED
        self.__status: str = NO_PROJECT_ATTACHED
        self.__priority: str = NO_PROJECT_ATTACHED
        self.__size: str = NO_PROJECT_ATTACHED
        self.__moscow: str = NO_PROJECT_ATTACHED

        self.__error: str | None = None

    @property
    def number(self) -> int:
        return self.__number

    @property
    def organization_name(self) -> str:
        return self.__organization_name

    @property
    def repository_name(self) -> str:
        return self.__repository_name

    @property
    def title(self) -> str:
        return self.__title

    @property
    def state(self) -> str:
        return self.__state

    @property
    def url(self) -> str:
        return self.__url

    @property
    def body(self) -> str:
        return self.__body

    @property
    def labels(self) -> list[str]:
        return self.__labels

    @property
    def linked_to_project(self) -> bool:
        return self.__linked_to_project

    @property
    def project_name(self) -> str:
        return self.__project_name

    @property
    def status(self) -> str:
        return self.__status

    @property
    def priority(self) -> str:
        return self.__priority

    @property
    def size(self) -> str:
        return self.__size

    @property
    def moscow(self) -> str:
        return self.__moscow

    @property
    def error(self) -> str | None:
        return self.__error

    def load_issue(self, issue_json):
        self.__number = issue_json["number"]
        self.__organization_name = issue_json["organization_name"]
        self.__repository_name = issue_json["repository_name"]
        self.__title = issue_json["title"]
        self.__state = issue_json["state"]
        self.__url = issue_json["url"]
        self.__body = issue_json["body"]
        # self.__created_at = issue_json["created_at"]
        # self.__updated_at = issue_json["updated_at"]
        # self.__closed_at = issue_json["closed_at"]
        # self.__milestone = issue_json["milestone"]
        self.__labels = issue_json["labels"]

        return self

    def update_with_project_data(self, issue: ProjectIssue):
        self.__linked_to_project = True
        self.__project_name = issue.project_name
        self.__status = issue.status
        self.__priority = issue.priority
        self.__size = issue.size
        self.__moscow = issue.moscow

    def no_project_mining(self):
        self.__linked_to_project = NO_PROJECT_MINING
        self.__project_name = NO_PROJECT_MINING
        self.__status = NO_PROJECT_MINING
        self.__priority = NO_PROJECT_MINING
        self.__size = NO_PROJECT_MINING
        self.__moscow = NO_PROJECT_MINING

        return self

    def load_consolidated_issue(self, consolidated_issue_json):
        self.__number = consolidated_issue_json["number"]
        self.__organization_name = consolidated_issue_json["organization_name"]
        self.__repository_name = consolidated_issue_json["repository_name"]
        self.__title = consolidated_issue_json["title"]
        self.__state = consolidated_issue_json["state"]
        self.__url = consolidated_issue_json["url"]
        self.__body = consolidated_issue_json["body"]
        # self.__created_at = consolidated_issue_json["created_at"]
        # self.__updated_at = consolidated_issue_json["updated_at"]
        # self.__closed_at = consolidated_issue_json["closed_at"]
        # self.__milestone = consolidated_issue_json["milestone"]
        self.__labels = consolidated_issue_json["labels"]
        self.__linked_to_project = consolidated_issue_json["linked_to_project"]
        self.__project_name = consolidated_issue_json["project_name"]
        self.__status = consolidated_issue_json["status"]
        self.__priority = consolidated_issue_json["priority"]
        self.__size = consolidated_issue_json["size"]
        self.__moscow = consolidated_issue_json["moscow"]
        self.__error = consolidated_issue_json["error"]

        return self

    def generate_page_filename(self):
        md_filename_base = f"{self.number}_{self.title.lower()}.md"
        page_filename = sanitize_filename(md_filename_base)

        return page_filename

    def to_dict(self):
        return {
            "number": self.number,
            "organization_name": self.organization_name,
            "repository_name": self.repository_name,
            "title": self.title,
            "state": self.state,
            "url": self.url,
            "body": self.body,
            # "created_at": self.created_at,
            # "updated_at": self.updated_at,
            # "closed_at": self.closed_at,
            # "milestone": self.milestone,
            "labels": self.labels,
            "linked_to_project": self.linked_to_project,
            "project_name": self.project_name,
            "status": self.status,
            "priority": self.priority,
            "size": self.size,
            "moscow": self.moscow,
            "error": self.error
        }
