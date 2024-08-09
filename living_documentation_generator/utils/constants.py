class Constants:
    # Action inputs environment variables
    GITHUB_TOKEN = 'GITHUB_TOKEN'
    PROJECT_STATE_MINING = 'PROJECT_STATE_MINING'
    REPOSITORIES = 'REPOSITORIES'
    OUTPUT_PATH = 'OUTPUT_PATH'

    # GitHub API constants
    ISSUES_PER_PAGE_LIMIT = 100
    ISSUE_STATE_ALL = 'all'
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

    # Symbol, when no project is attached to an issue
    NO_PROJECT_ATTACHED = '---'

    # Constant to symbolize if issue is linked to a project
    LINKED_TO_PROJECT_TRUE = '🟢'
    LINKED_TO_PROJECT_FALSE = '🔴'
