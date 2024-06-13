from typing import List, Dict
import requests

from .project_issue import ProjectIssue
from .base_container import BaseContainer

CONSTANT = "N/A"
ISSUE_PER_PAGE = 100
ISSUES_FROM_PROJECT_QUERY = """
    query {{
      node(id: "{project_id}") {{
        ... on ProjectV2 {{
          items(first: {issues_per_page}, {after_argument}) {{
            pageInfo {{
              endCursor
              hasNextPage
            }}
            nodes {{
              content {{
                  ... on Issue {{
                    title
                    state
                    number
                    repository {{
                      name
                      owner {{
                        login
                      }}
                    }}
                  }}
                }}
              fieldValues(first: 100) {{
                nodes {{
                  __typename
                  ... on ProjectV2ItemFieldSingleSelectValue {{
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """
PROJECT_FIELD_OPTIONS_QUERY = """
        query {{
          repository(owner: "{org_name}", name: "{repo_name}") {{
            projectV2(number: {project_number}) {{
              title
              fields(first: 100) {{
                nodes {{
                  ... on ProjectV2SingleSelectField {{
                    name
                    options {{
                      name
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """


class Project(BaseContainer):
    def __init__(self):
        self.id: str = ""
        self.number: int = 0
        self.title: str = ""
        self.organization_name: str = ""
        # TODO: I will have object Project and its repositories. Delete this field
        self.project_repositories: List[str] = []
        self.issues: List[ProjectIssue] = []
        self.field_options: Dict[str, List[str]] = {}

    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'title': self.title,
            'organization_name': self.organization_name,
            'project_repositories': self.project_repositories,
            'issues': self.issues,
            'field_options': self.field_options
        }

    def load_from_json(self, gh_project, organization_name):
        self.id = gh_project.get("id", CONSTANT)
        self.title = gh_project.get("title", CONSTANT)
        self.number = gh_project.get("number", CONSTANT)
        self.organization_name = organization_name

    def update_field_options(self, session: requests.sessions.Session, repository):
        project_field_options_query = PROJECT_FIELD_OPTIONS_QUERY.format(org_name=repository.organization_name,
                                                                         repo_name=repository.repository_name,
                                                                         project_number=self.number)
        field_option_response = self.send_graphql_query(project_field_options_query, session)

        # Return empty list, if project has no issues attached
        if len(field_option_response) == 0:
            exit()

        field_options_nodes = field_option_response['repository']['projectV2']['fields']['nodes']
        for field_option in field_options_nodes:
            if "name" in field_option and "options" in field_option:
                field_name = field_option["name"]
                options = [option["name"] for option in field_option["options"]]

                # Update the dict with every unique field
                self.field_options.update({field_name: options})

    def get_gh_issues(self, session: requests.sessions.Session) -> List[dict]:
        """
        Fetches all issues from a given project using a GraphQL query.
        The issues are fetched supported by pagination.

        @param session: A configured request session.

        @return: The list of all issues in the project.
        """
        gh_project_issues = []
        cursor = None

        while True:
            # Add the after argument to the query if a cursor is provided
            after_argument = f'after: "{cursor}"' if cursor else ''

            # Fetch the GraphQL response with all issues attached to specific project
            issues_from_project_query = ISSUES_FROM_PROJECT_QUERY.format(project_id=self.id,
                                                                         issues_per_page=ISSUE_PER_PAGE,
                                                                         after_argument=after_argument)
            project_issues_response = self.send_graphql_query(issues_from_project_query, session)

            # Return empty list, if project has no issues attached
            if len(project_issues_response) == 0:
                return []

            general_response_structure = project_issues_response['node']['items']
            issue_data = general_response_structure['nodes']
            page_info = general_response_structure['pageInfo']

            # Extend project issues list per every page during pagination
            gh_project_issues.extend(issue_data)
            print(f"Loaded `{len(issue_data)}` issues.")

            # Check for closing the pagination process
            if not page_info['hasNextPage']:
                break
            cursor = page_info['endCursor']

        return gh_project_issues

    def update_attached_repositories(self, repository_name, attached_repositories):
        if repository_name != "N/A":
            if repository_name not in attached_repositories:
                self.project_repositories.append(repository_name)
                attached_repositories.append(repository_name)
