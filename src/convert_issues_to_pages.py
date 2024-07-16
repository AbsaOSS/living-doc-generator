"""Convert Features to Pages

This script is used to convert consolidated feature data into individual markdown files.
It reads a JSON file containing consolidated feature data, processes this data, and generates
 a markdown file for each feature.

 The script can be run from the command line with optional arguments:
    * python3 convert_issues_to_pages.py
 """

import json
import logging
import os
from datetime import datetime

from action.action_inputs import ActionInputs
from github_integration.model.consolidated_issue import ConsolidatedIssue
from utils import ensure_folder_exists

CONSOLIDATION_FILE = "../data/issue_consolidation/issue.consolidation.json"
ISSUE_PAGE_TEMPLATE_FILE = "../templates/issue_page_template.md"
INDEX_PAGE_TEMPLATE_FILE = "../templates/_index_page_template.md"
OUTPUT_DIRECTORY_ISSUE = "issues"


def replace_template_placeholders(template: str, replacement: dict[str, str]) -> str:
    """
        Replaces placeholders in a template ({replacement}) with corresponding values from a dictionary.

        @param template: The string template containing placeholders.
        @param replacement: The dictionary containing keys and values for replacing placeholders.

        @return: The updated template string with replaced placeholders.
    """

    # Update template with values from replacement dictionary
    for key, value in replacement.items():
        if value is not None:
            template = template.replace(f"{{{key}}}", value)
        else:
            template = template.replace(f"{{{key}}}", "")

    return template


def generate_issue_summary_table(consolidated_issue: ConsolidatedIssue) -> str:
    """
        Generates a string representation of feature info in a table format.

        @param consolidated_issue: The dictionary containing feature data.

        @return: A string representing the feature information in a table format.
    """
    # Get the issue labels and join them into one string
    labels = consolidated_issue.labels
    labels = ', '.join(labels) if labels else None

    # Get the issue URL and format it as a Markdown link
    issue_url = consolidated_issue.url
    issue_url = f"[GitHub link]({issue_url})" if issue_url else None

    # Define the header for the issue summary table
    # TODO: Does not support all the fields for now, have to update later
    headers = [
        "Organization name",
        "Repository name",
        "Issue number",
        "State",
        "Issue URL",
        # "Created at",
        # "Updated at",
        # "Closed at",
        "Labels"
        ]

    # Define the values for the issue summary table
    values = [
        consolidated_issue.organization_name,
        consolidated_issue.repository_name,
        consolidated_issue.number,
        consolidated_issue.state.lower(),
        issue_url,
        # consolidated_issue.created_at,
        # consolidated_issue.updated_at,
        # consolidated_issue.closed_at,
        labels
    ]

    # # Update the summary table, if issue has a milestone object
    # if consolidated_issue.milestone is not None:
    #     milestone_url = consolidated_issue.milestone.html_url
    #     milestone_url = f"[GitHub link]({milestone_url})"
    #
    #     headers.extend([
    #         "Milestone number",
    #         "Milestone title",
    #         "Milestone URL"
    #     ])
    #
    #     values.extend([
    #         consolidated_issue.milestone.number,
    #         consolidated_issue.milestone.title,
    #         milestone_url
    #     ])
    # else:
    #     headers.append("Milestone")
    #     values.append(None)

    # Update the summary table, if issue is linked to the project
    if consolidated_issue.linked_to_project:
        headers.extend([
            "Project title",
            "Status",
            "Priority",
            "Size",
            "MoSCoW"
        ])

        values.extend([
            consolidated_issue.project_name,
            consolidated_issue.status,
            consolidated_issue.priority,
            consolidated_issue.size,
            consolidated_issue.moscow
        ])
    else:
        headers.append("Linked to project")
        values.append(consolidated_issue.linked_to_project)

    # Initialize the Markdown table
    issue_info = f"| Attribute | Content |\n|---|---|\n"

    # Add together all the attributes from the summary table in Markdown format
    for attribute, content in zip(headers, values):
        issue_info += f"| {attribute} | {content} |\n"

    return issue_info


def generate_md_issue_page(issue_page_template: str, consolidated_issue: ConsolidatedIssue, output_directory: str) -> None:
    """
        Generates a markdown file for a given feature using a specified template.

        @param issue_page_template: The string template for the single page markdown file.
        @param consolidated_issue: The dictionary containing feature data.
        @param output_directory: The directory where the markdown file will be saved.

        @return: None
    """

    # Get all replacements for generating single issue page from a template
    title = consolidated_issue.title
    date = datetime.now().strftime("%Y-%m-%d")
    issue_content = consolidated_issue.body

    # Generate a summary table for the issue
    issue_table = generate_issue_summary_table(consolidated_issue)

    # Initialize dictionary with replacements
    replacements = {
        "title": title,
        "date": date,
        "page_issue_title": title,
        "issue_summary_table": issue_table,
        "issue_content": issue_content
    }

    # Run through all replacements and update template keys with adequate content
    issue_md_page = replace_template_placeholders(issue_page_template, replacements)

    # Get the page filename for naming single issue output correctly
    page_filename = consolidated_issue.generate_page_filename()

    # Save the single issue Markdown page
    with open(os.path.join(output_directory, page_filename), 'w', encoding='utf-8') as issue_file:
        issue_file.write(issue_md_page)

    print(f"Generated {page_filename}.")


def generate_markdown_line(consolidated_issue) -> str:
    """
        Generates a markdown summary line for a given feature.

        @param consolidated_issue: The dictionary containing feature data.

        @return: A string representing the markdown line for the feature.
    """

    # Extract issue details from the consolidated issue object
    organization_name = consolidated_issue.organization_name
    repository_name = consolidated_issue.repository_name
    number = consolidated_issue.number
    title = consolidated_issue.title
    title = title.replace("|", " _ ")
    page_filename = consolidated_issue.generate_page_filename()
    status = consolidated_issue.status
    url = consolidated_issue.url

    # Change the bool values to more user-friendly characters
    if consolidated_issue.linked_to_project:
        linked_to_project = "🟢"
    else:
        linked_to_project = "🔴"

    # Generate the markdown line for the issue
    md_issue_line = (f"|{organization_name} | {repository_name} | [#{number} - {title}]({page_filename}) |"
                     f" {linked_to_project} | {status} |[GitHub link]({url}) |\n")

    return md_issue_line


# def group_issues_by_milestone(consolidated_issues_data: list) -> Dict[str, List[ConsolidatedIssue]]:
#     """
#         Groups issues by their milestone.
#
#         @param consolidated_issues_data: A list of all consolidated issues.
#
#         @return: A dictionary where each key is a milestone title and the value is a list of issues
#          under that milestone.
#     """
#
#     # Initialize a dictionary to store all milestones
#     milestones = {}
#
#     # Create a consolidated issue objects from the data
#     for consolidated_issue_data in consolidated_issues_data:
#         consolidated_issue = ConsolidatedIssue()
#         consolidated_issue.load_from_data(consolidated_issue_data)
#
#         # Prepare the structure for correct grouping the issues with same milestone
#         if consolidated_issue.milestone is not None:
#             milestone_title = f"{consolidated_issue.milestone.title}"
#         else:
#             milestone_title = "No milestone"
#
#         # Create a new milestone structure, if it does not exist
#         if milestone_title not in milestones:
#             milestones[milestone_title] = []
#
#         # Add the issue to the correct milestone
#         milestones[milestone_title].append(consolidated_issue)
#
#     return milestones


# def generate_milestone_block(milestone_table_header: str, milestone_title: str, issue_lines: List[str]) -> str:
#     """
#         Generates a markdown block for a given milestone and its features.
#
#         @param milestone_table_header: The table header for the milestone block.
#         @param milestone_title: The title of the milestone.
#         @param issue_lines: A list of markdown lines, each representing a feature.
#
#         @return: A string representing the markdown block for the milestone.
#     """
#
#     milestone_block = f"\n### {milestone_title}\n" + milestone_table_header + "".join(issue_lines)
#
#     return milestone_block


def process_consolidated_issues(consolidated_issues_data,
                                issue_page_template: str,
                                output_directory: str) -> str:

    issue_markdown_content = ""
    table_header = """| Organization name     | Repository name | Issue 'Number - Title'  | Linked to project | Project status  |Issue URL   |
           |-----------------------|-----------------|---------------------------|---------|------|-----|
           """

    issue_markdown_content += "\n" + table_header

    for consolidated_issue_data in consolidated_issues_data:
        consolidated_issue = ConsolidatedIssue().load_consolidated_issue(consolidated_issue_data)
        issue_markdown_content += generate_markdown_line(consolidated_issue)

        generate_md_issue_page(issue_page_template, consolidated_issue, output_directory)

    return issue_markdown_content


# def generate_table_of_contents(content: str) -> str:
#     """
#     Generates a table of contents for a given markdown content.
#
#     @param content: The string containing the markdown content.
#
#     @return: A string representing the table of contents in a md format.
#     """
#
#     # Find all headings in the content
#     headings = re.findall(r"(#+) (.+)", content)
#
#     # Set the table of contents
#     toc = []
#
#     # Add the table of contents header
#     toc.append("## Table of Contents")
#
#     for level, title in headings:
#         # Ignore Heading 1
#         if len(level) == 1:
#             continue
#
#         # Normalize the title to create anchor links
#         normalized_title = re.sub(r"[^\w\s-]", '', title.lower())
#         anchor_link = normalized_title.replace(' ', '-')
#
#         # Calculate the indentation based on number of hash marks
#         indentation = ' ' * 4 * (len(level) - 2)
#
#         # Create Markdown string for the table of contents
#         toc_link = f"{indentation}- [{title}](#{anchor_link})"
#
#         toc.append(toc_link)
#
#     # ToC into single string separated
#     toc_string = "\n".join(toc)
#
#     return toc_string


def generate_index_page(issue_markdown_content: str, template_index_page: str, output_directory: str) -> None:
    """
        Generates an index summary markdown page for all features.

        @param issue_markdown_content: A string containing all the generated markdown blocks for the features.
        @param template_index_page: The string template for the index markdown page.
        @param output_directory: The directory where the index page will be saved.

        @return: None
    """

    # Prepare issues replacement for the index page
    replacement = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "issues": issue_markdown_content
    }

    # Replace the issue placeholders in the index template
    index_page = replace_template_placeholders(template_index_page, replacement)

    # Generate table of contents, if config value of `milestones_as_chapters` is True
    # table_of_contents = generate_table_of_contents(index_page_content) if milestones_as_chapters else ""

    # # Prepare additional replacements for the index page
    # replacements = {
    #     "table-of-contents": table_of_contents
    # }

    # Second wave of replacing placeholders in the index template
    # index_page = replace_template_placeholders(index_page_content, replacements)

    # Create an index page file
    with open(os.path.join(output_directory, "_index.md"), 'w', encoding='utf-8') as index_file:
        index_file.write(index_page)

    logging.info("Generated _index.md.")


def main() -> None:
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Script for converting consolidated issues into markdown pages started.")

    # Load action inputs from the environment
    action_inputs = ActionInputs().load_from_environment()
    output_directory_root = f"{action_inputs.output_directory}/liv-doc"
    output_directory = os.path.join(output_directory_root, OUTPUT_DIRECTORY_ISSUE)

    # Check if the output directory exists and create it if not
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(os.path.join(current_dir, output_directory), current_dir)

    logging.info("Starting the markdown page generation process.")

    # Load consolidated issue data and page templates
    with open(CONSOLIDATION_FILE, 'r', encoding='utf-8') as consolidation_json_file:
        consolidated_issues_data = json.load(consolidation_json_file)

    with open(ISSUE_PAGE_TEMPLATE_FILE, 'r', encoding='utf-8') as issue_page_template_file:
        issue_page_template = issue_page_template_file.read()

    with open(INDEX_PAGE_TEMPLATE_FILE, 'r', encoding='utf-8') as idx_page_template_file:
        index_page_template = idx_page_template_file.read()

    # Organize consolidated issues data by milestones
    # milestones = group_issues_by_milestone(consolidated_issues_data)

    # Generate single markdown pages
    issue_markdown_content = process_consolidated_issues(consolidated_issues_data,
                                                         issue_page_template,
                                                         output_directory)

    # Generate index page
    generate_index_page(issue_markdown_content, index_page_template, output_directory)

    logging.info(f"Living documentation generated at: {os.path.join(current_dir, output_directory_root)}")

    logging.info("Script for converting consolidated issues into markdown pages ended.")


if __name__ == "__main__":
    main()
