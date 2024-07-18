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

cd src || exit 1

python3 living_documentation_generator.py

cd .. || exit 1

