class GithubProjectQueries:
    ISSUES_PER_PAGE_LIMIT = 100
    PROJECTS_FROM_REPO_QUERY = """
                query {{
                  repository(owner: "{organization_name}", name: "{repository_name}") {{
                    projectsV2(first: 100) {{
                      nodes {{
                        id
                        number
                        title
                      }}
                    }}
                  }}
                }}
                """
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
              repository(owner: "{organization_name}", name: "{repository_name}") {{
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

    @staticmethod
    def get_projects_from_repo_query(organization_name: str, repository_name: str) -> str:
        return GithubProjectQueries.PROJECTS_FROM_REPO_QUERY.format(organization_name=organization_name,
                                                                    repository_name=repository_name)

    @staticmethod
    def get_issues_from_project_query(project_id: str, after_argument: str) -> str:
        return GithubProjectQueries.ISSUES_FROM_PROJECT_QUERY.format(project_id=project_id,
                                                                     issues_per_page=GithubProjectQueries.ISSUES_PER_PAGE_LIMIT,
                                                                     after_argument=after_argument)

    @staticmethod
    def get_project_field_options_query(organization_name: str, repository_name: str, project_number: int) -> str:
        return GithubProjectQueries.PROJECT_FIELD_OPTIONS_QUERY.format(organization_name=organization_name,
                                                                       repository_name=repository_name,
                                                                       project_number=project_number)
