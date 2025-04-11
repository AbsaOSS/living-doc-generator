import os

from datetime import date

output_folder = "output"
directory_path = f"{output_folder}/liv-doc-regime"
issue88_path = f"{directory_path}/features/TEST: Documented feature /_index.md"
issue89_path = f"{directory_path}/user_stories/89_test_user_story_in_project.md"
issue90_path = f"{directory_path}/features/TEST: Documented feature  in project/_index.md"
issue91_path = f"{directory_path}/user_stories/91_test_user_story.md"

issue88_header = f'''---
title: "TEST: Documented feature "
date: {date.today().strftime("%Y-%m-%d")}
weight: 1
---
'''
issue88_content_header_wopm = '''
![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue88_content_header_wpm = '''
![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue88_content_header_wpmep = '''
![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue88_content = '''
# Feature

This is a documented feature created for integration testing 
Please **don't remove** this 
Please **don't add this task to the project** 

## Description

Feature description

- [ ] subtask 1
- [ ] subtask 2
'''
issue89_header = f'''---
title: "TEST: User story in project"
date: {date.today().strftime("%Y-%m-%d")}
weight: 1
---
'''
issue89_content_header_wopm = '''
![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue89_content_header_wpm = '''
![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue89_content_header_wpmep = '''
![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue89_content ='''
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
issue90_header = f'''---
title: "TEST: Documented feature  in project"
date: {date.today().strftime("%Y-%m-%d")}
weight: 1
---
'''
issue90_content_header_wopm = '''
![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue90_content_header_wpm = '''
![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue90_content_header_wpmep = '''
![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue90_content ='''
# Feature

This is a documented feature created for integration testing 
Please **don't remove** this 
Please **don't remove this task from the project** 

## Description

Feature description

- [ ] subtask 1
- [ ] subtask 2
'''
issue91_header = f'''---
title: "TEST: User story"
date: {date.today().strftime("%Y-%m-%d")}
weight: 1
---'''
issue91_content_header_wopm = '''

![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue91_content_header_wpm = '''

![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue91_content_header_wpmep = '''

![GitHub State:Open](https://img.shields.io/badge/GitHub_State-Open-brightgreen)
![Project State:Open](https://img.shields.io/badge/Project_State-Open-brightgreen)
![Priority:Low](https://img.shields.io/badge/Priority-Low-blue)
<a href='https://github.com/absa-group/aqueduct-living-documentation/issues/5' target='_blank'>GitHub icon</a>
'''
issue91_content = '''
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

def count_files_in_directory(directory):
    return sum(len(files) for _, _, files in os.walk(directory))

def validate_issue(path, issue):
    with open(path, 'r') as f:
        markdown_string = f.read()


        if issue not in markdown_string:
            print(f"Expected:\n'{issue}'")
            print("\n=====================-\n")
            print(f"Actual:\n'{markdown_string}'")
            return False
        return True


def test_validate_for_test_without_project_mining():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 6
    assert validate_issue(issue88_path, issue88_header + issue88_content_header_wopm + issue88_content)
    assert validate_issue(issue89_path, issue89_header + issue89_content_header_wopm + issue89_content)
    assert validate_issue(issue90_path, issue90_header + issue90_content_header_wopm + issue90_content)
    assert validate_issue(issue91_path, issue91_header + issue91_content_header_wopm + issue91_content)

def test_validate_for_test_with_project_mining():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 6
    assert validate_issue(issue88_path, issue88_header + issue88_content_header_wpm + issue88_content)
    assert validate_issue(issue89_path, issue89_header + issue89_content_header_wpm + issue89_content)
    assert validate_issue(issue90_path, issue90_header + issue90_content_header_wpm + issue90_content)
    assert validate_issue(issue91_path, issue91_header + issue91_content_header_wpm + issue91_content)

def test_validate_for_test_with_project_mining_and_excluded_project():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 6
    assert validate_issue(issue88_path, issue88_header + issue88_content_header_wpmep + issue88_content)
    assert validate_issue(issue89_path, issue89_header + issue89_content_header_wpmep + issue89_content)
    assert validate_issue(issue90_path, issue90_header + issue90_content_header_wpmep + issue90_content)
    assert validate_issue(issue91_path, issue91_header + issue91_content_header_wpmep + issue91_content)
