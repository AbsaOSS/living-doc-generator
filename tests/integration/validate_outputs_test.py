import os

output_folder = "output"
directory_path = f"{output_folder}/liv-doc-regime"
issue88_path = f"{directory_path}/88_test_task_issue.md"
issue89_path = f"{directory_path}/89_test_bug_issue_in_project.md"
issue90_path = f"{directory_path}/90_test_task_issue_in_project.md"
issue91_path = f"{directory_path}/91_test_bug_issue.md"

issue88 = '''
| Attribute | Content |
|---|---|
| Organization name | AbsaOSS |
| Repository name | living-doc-generator |
| Issue number | 88 |
| Title | TEST: task issue |
| State | open |
| Issue URL | <a href='https://github.com/AbsaOSS/living-doc-generator/issues/88' target='_blank'>GitHub link</a>  |
| Created at | 2025-02-19 08:45:06+00:00 |
| Updated at | 2025-02-19 08:48:22+00:00 |
| Closed at | None |
| Labels | enhancement, int-tests |

 
<h3>Issue Content</h3>

This is a task issue created for integration testing 
Please **don't remove** this 
Please **don't add this task to the project** this 
'''
issue89 = '''
| Attribute | Content |
|---|---|
| Organization name | AbsaOSS |
| Repository name | living-doc-generator |
| Issue number | 89 |
| Title | TEST: bug issue in project |
| State | open |
| Issue URL | <a href='https://github.com/AbsaOSS/living-doc-generator/issues/89' target='_blank'>GitHub link</a>  |
| Created at | 2025-02-19 08:48:59+00:00 |
| Updated at | 2025-02-19 08:58:56+00:00 |
| Closed at | None |
| Labels | bug, int-tests |

 
<h3>Issue Content</h3>

This is a bug issue created for integration testing
Please **don't remove** this
Please **don't remove this task from  the project** this
'''
issue90 = '''| Attribute | Content |
|---|---|
| Organization name | AbsaOSS |
| Repository name | living-doc-generator |
| Issue number | 90 |
| Title | TEST: task issue in project |
| State | open |
| Issue URL | <a href='https://github.com/AbsaOSS/living-doc-generator/issues/90' target='_blank'>GitHub link</a>  |
| Created at | 2025-02-19 08:55:41+00:00 |
| Updated at | 2025-02-19 08:55:41+00:00 |
| Closed at | None |
| Labels | enhancement, int-tests |

 
<h3>Issue Content</h3>

This is a task issue created for integration testing 
Please **don't remove** this 
Please **don't remove this task from the project** this '''
issue91 = '''| Attribute | Content |
|---|---|
| Organization name | AbsaOSS |
| Repository name | living-doc-generator |
| Issue number | 91 |
| Title | TEST: bug issue |
| State | open |
| Issue URL | <a href='https://github.com/AbsaOSS/living-doc-generator/issues/91' target='_blank'>GitHub link</a>  |
| Created at | 2025-02-19 08:58:08+00:00 |
| Updated at | 2025-02-19 08:58:08+00:00 |
| Closed at | None |
| Labels | bug, int-tests |

 
<h3>Issue Content</h3>

This is a bug issue created for integration testing
Please **don't remove** this
Please **don't add this to the project** this'''

def count_files_in_directory(directory):
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])

def validate_issue(path, issue):
    with open(path, 'r') as f:
        markdown_string = f.read()
        return issue in markdown_string


def test_validate_for_test1():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 4 + 1
    assert validate_issue(issue88_path, issue88)
    assert validate_issue(issue89_path, issue89)
    assert validate_issue(issue90_path, issue90)
    assert validate_issue(issue91_path, issue91)

def test_validate_for_test2():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 2 + 1

def test_validate_for_test3():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 2 + 1