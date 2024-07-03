import os
import subprocess
import sys


def extend_args():
    env_vars = {
        'FETCH_DIRECTORY': "src/data/fetched_data",
        'CONSOLIDATION_DIRECTORY': "src/data/consolidation_data",
        'MARKDOWN_PAGE_DIRECTORY': "src/output/markdown_pages"
    }

    return env_vars


def run_script(script_name, env):
    """ Helper function to run a Python script with environment variables using subprocess """
    try:
        # Running the python script with given environment variables
        result = subprocess.run(['python3', script_name], env=env, text=True, capture_output=True, check=True)
        print(f"Output from {script_name}: {result.stdout}")

    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: \n{e.stdout}\n{e.stderr}")
        sys.exit(1)


def main():
    print("Extracting arguments from command line.")
    env_vars = extend_args()

    # Create a local copy of the current environment variables
    local_env = os.environ.copy()

    # Add the script-specific environment variables to the local copy
    local_env.update(env_vars)

    print("Starting the Living Documentation Generator - mining phase")

    # Clean the environment before mining
    run_script('clean_env_before_mining.py', local_env)

    # Data mine GitHub features from repository
    run_script('github_query_issues.py', local_env)

    # Data mine GitHub project's state
    run_script('github_query_project_state.py', local_env)

    # Consolidate all feature data together
    run_script('consolidate_feature_data.py', local_env)

    # Generate markdown pages
    run_script('convert_features_to_pages.py', local_env)

    # TODO ideas to consider during OOP refactoring
    #
    #   1. make clean script as method in this script
    #   2. can be run_script replaced by method calls? ==> reduction standalone script files to methods using OOP
    #       - we have ActionInputs class, we will have shared logic in library
    #   3. we can introduce a classes
    #       - LivingDocumentationDataMiner - mines issues from N repositories, projects
    #           - will define method for issues mining
    #           - will define method for project state mining
    #       - LivingDocumentationConsolidator - consolidates mined data
    #       - LivingDocumentationBuilder - builds markdown pages from consolidated data


if __name__ == '__main__':
    print("Starting Living Documentation generation.")
    main()
    print("Living Documentation generation completed.")
