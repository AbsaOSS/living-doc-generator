import os

output_folder = "output"
directory_path = f"{output_folder}/liv-doc-regime"
issue88_path = f"{directory_path}/88_test_documented_feature_.md"
issue89_path = f"{directory_path}/89_test_user_story_in_project.md"
issue90_path = f"{directory_path}/90_test_documented_feature_in_project.md"
issue91_path = f"{directory_path}/91_test_user_story.md"

issue88_header = '''
| Attribute | Content |
|---|---|
| Organization name | AbsaOSS |
| Repository name | living-doc-generator |
| Issue number | 88 |
| Title | TEST: Documented feature  |
| State | open |
| Issue URL | <a href='https://github.com/AbsaOSS/living-doc-generator/issues/88' target='_blank'>GitHub link</a>  |
| Created at | 2025-02-19 08:45:06+00:00 |
| Updated at | 2025-02-25 13:54:16+00:00 |
| Closed at | None |
| Labels | int-tests, DocumentedFeature |'''
issue88_content ='''

 
<h3>Issue Content</h3>

# Feature

This is a documented feature created for integration testing 
Please **don't remove** this 
Please **don't add this task to the project** 

## Description

Feature description

- [ ] subtask 1
- [ ] subtask 2
'''
issue89_header = '''
| Attribute | Content |
|---|---|
| Organization name | AbsaOSS |
| Repository name | living-doc-generator |
| Issue number | 89 |
| Title | TEST: User story in project |
| State | open |
| Issue URL | <a href='https://github.com/AbsaOSS/living-doc-generator/issues/89' target='_blank'>GitHub link</a>  |
| Created at | 2025-02-19 08:48:59+00:00 |
| Updated at | 2025-02-25 13:47:55+00:00 |
| Closed at | None |
| Labels | int-tests, DocumentedUserStory |'''
issue89_content ='''

 
<h3>Issue Content</h3>

# User Story

> This is a user story created for integration testing
> Please **don't remove** this
> Please **don't remove this task from  the project** 

## Description

Some user story description

## Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## User Guide

### Description

[Provide a summary of the user story, describing how it supports usability and efficiency.]

### End-to-End Test to Guide Steps

- **Automated**: [True/False]
- **Prerequisite**:
    - [List any prerequisites, e.g., At least one searchable object in the database]

- **Steps**:
    - Step 1: [Instruction]
    - Step 2: [Instruction]
'''
issue90_header = '''
| Attribute | Content |
|---|---|
| Organization name | AbsaOSS |
| Repository name | living-doc-generator |
| Issue number | 90 |
| Title | TEST: Documented feature  in project |
| State | open |
| Issue URL | <a href='https://github.com/AbsaOSS/living-doc-generator/issues/90' target='_blank'>GitHub link</a>  |
| Created at | 2025-02-19 08:55:41+00:00 |
| Updated at | 2025-02-25 13:54:07+00:00 |
| Closed at | None |
| Labels | int-tests, DocumentedFeature |'''
issue90_content ='''

 
<h3>Issue Content</h3>

# Feature

This is a documented feature created for integration testing 
Please **don't remove** this 
Please **don't remove this task from the project** 

## Description

Feature description

- [ ] subtask 1
- [ ] subtask 2
'''
issue91_header = '''
| Attribute | Content |
|---|---|
| Organization name | AbsaOSS |
| Repository name | living-doc-generator |
| Issue number | 91 |
| Title | TEST: User story |
| State | open |
| Issue URL | <a href='https://github.com/AbsaOSS/living-doc-generator/issues/91' target='_blank'>GitHub link</a>  |
| Created at | 2025-02-19 08:58:08+00:00 |
| Updated at | 2025-02-25 13:45:46+00:00 |
| Closed at | None |
| Labels | int-tests, DocumentedUserStory |'''
issue91_content = '''

 
<h3>Issue Content</h3>

# User Story

> This is a user story created for integration testing
> Please **don't remove** this
> Please **don't add this to the project** 

## Description

Some user story description

## Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## User Guide

### Description

[Provide a summary of the user story, describing how it supports usability and efficiency.]

### End-to-End Test to Guide Steps

- **Automated**: [True/False]
- **Prerequisite**:
    - [List any prerequisites, e.g., At least one searchable object in the database]

- **Steps**:
    - Step 1: [Instruction]
    - Step 2: [Instruction]'''
link_to_project_false = '''
| Linked to project | 🔴 |'''
S_P1_TODO = '''
| Project title | integration-tests-for-living-doc-generator |
| Status | Todo |
| Priority | P1 |
| Size | S |
| MoSCoW | --- |'''

M_P0_IN_PROGRESS = '''
| Project title | integration-tests-for-living-doc-generator |
| Status | In Progress |
| Priority | P0 |
| Size | M |
| MoSCoW | --- |'''
def count_files_in_directory(directory):
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])

def validate_issue(path, issue):
    with open(path, 'r') as f:
        markdown_string = f.read()
        if issue not in markdown_string:
            print(issue)
            print("\n=====================-\n")
            print(markdown_string)
            return False
        return True


def test_validate_for_test_without_project_mining():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 4 + 1
    assert validate_issue(issue88_path, issue88_header + issue88_content)
    assert validate_issue(issue89_path, issue89_header + issue89_content)
    assert validate_issue(issue90_path, issue90_header + issue90_content)
    assert validate_issue(issue91_path, issue91_header + issue91_content)

def test_validate_for_test_whit_project_mining():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 4 + 1
    assert validate_issue(issue88_path, issue88_header + link_to_project_false + issue88_content)
    assert validate_issue(issue89_path, issue89_header)
    assert validate_issue(issue89_path, S_P1_TODO )
    assert validate_issue(issue89_path, issue89_content)
    assert validate_issue(issue90_path, issue90_header)
    assert validate_issue(issue90_path, M_P0_IN_PROGRESS)
    assert validate_issue(issue90_path, issue90_content)
    assert validate_issue(issue91_path, issue91_header + link_to_project_false + issue91_content)

def test_validate_for_test_whit_project_mining_and_excluded_project():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 4 + 1
    assert validate_issue(issue88_path, issue88_header + link_to_project_false + issue88_content)
    assert validate_issue(issue89_path, issue89_header + S_P1_TODO + issue89_content)
    assert validate_issue(issue90_path, issue90_header + M_P0_IN_PROGRESS + issue90_content)
    assert validate_issue(issue91_path, issue91_header + link_to_project_false + issue91_content)