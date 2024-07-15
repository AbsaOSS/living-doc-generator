NOT_SET_FOR_NOW = "NOT_SET_IN_THIS_VERSION"
NO_PROJECT_ATTACHED = "---"
NO_PROJECT_MINING = "-?-"


class ConsolidatedIssue:
    def __init__(self, issue_json):
        # TODO: finish all the fields with other version
        # Main issue structure
        self.number: int = issue_json["number"]
        self.organization_name: str = issue_json["organization_name"]
        self.repository_name: str = issue_json["repository_name"]
        self.title: str = issue_json["title"]
        self.state: str = issue_json["state"]
        # self.url: str = NOT_SET_FOR_NOW
        self.body: str = issue_json["body"]
        # self.created_at: str = NOT_SET_FOR_NOW
        # self.updated_at: str = NOT_SET_FOR_NOW
        # self.closed_at: str = NOT_SET_FOR_NOW
        # self.milestone: str = NOT_SET_FOR_NOW
        self.labels: list[str] = issue_json["labels"]

        # Extra project data
        self.linked_to_project: bool = False
        self.project_name: str = NO_PROJECT_ATTACHED
        self.status: str = NO_PROJECT_ATTACHED
        self.priority: str = NO_PROJECT_ATTACHED
        self.size: str = NO_PROJECT_ATTACHED
        self.moscow: str = NO_PROJECT_ATTACHED

        self.error: str | None = None

    def update_with_project_data(self, project_issue):
        self.linked_to_project = True
        self.project_name = project_issue["project_name"]
        self.status = project_issue["status"]
        self.priority = project_issue["priority"]
        self.size = project_issue["size"]
        self.moscow = project_issue["moscow"]

    def no_project_mining(self):
        self.linked_to_project = NO_PROJECT_MINING
        self.project_name = NO_PROJECT_MINING
        self.status = NO_PROJECT_MINING
        self.priority = NO_PROJECT_MINING
        self.size = NO_PROJECT_MINING
        self.moscow = NO_PROJECT_MINING

        return self

    def to_dict(self):
        return {
            "number": self.number,
            "organization_name": self.organization_name,
            "repository_name": self.repository_name,
            "title": self.title,
            "state": self.state,
            # "url": self.url,
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
