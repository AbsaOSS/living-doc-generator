export GITHUB_TOKEN=$(printenv GITHUB_TOKEN)
export PROJECT_STATE_MINING="true"
export PROJECTS_TITLE_FILTER="[]"
export REPOSITORIES='[
            {
              "owner": "absa-group",
              "repo-name": "living-doc-example-project",
              "query-labels": ["feature", "bug"]
            }
          ]'

python3 main.py

