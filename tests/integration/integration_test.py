from exceptiongroup import catch

import main
import os

def test_output_folder_is_created(setup_for_integration_tests, clean_for_integration_tests):
    gh_token = os.getenv("GITHUB_TOKEN")
    if gh_token is not None:
        os.environ["INPUT_GITHUB_TOKEN"] = gh_token
    else:
        raise EnvironmentError("GITHUB_TOKEN environment variable is not set")

    # Environment variables for LivDoc regime functionality
    os.environ["INPUT_LIV_DOC_REPOSITORIES"] = ('[{"organization-name": "AbsaOSS",'
                                                '"repository-name": "living-doc-generator",'
                                                '"query-labels": ["under discussion"],'
                                                '"projects-title-filter": []}]')

    main.run()

    output_folder = "output"
    assert os.path.exists(output_folder)


def test_output_folder_is_not_created(setup_for_integration_tests, clean_for_integration_tests):
    os.environ["INPUT_GITHUB_TOKEN"] = ""
    # Environment variables for LivDoc regime functionality
    os.environ["INPUT_LIV_DOC_REPOSITORIES"] = ('[{"organization-name": "AbsaOSS",'
                                                '"repository-name": "living-doc-generator",'
                                                '"query-labels": ["under discussion"],'
                                                '"projects-title-filter": []}]')

    try:
        main.run()
    except:
        pass

    output_folder = "output"
    assert not os.path.exists(output_folder)
