import wikipediaapi
import json
import csv
import os


def parse_wikipedia_titles_api(page_title):
    """
    Extract section titles from a Wikipedia page using the Wikipedia API.

    Args:
        page_title (str): The title of the Wikipedia page

    Returns:
        dict: A dictionary with section information
    """
    # Initialize the Wikipedia API with a user agent
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        user_agent='MyProject/1.0'
    )

    # Get the page
    page = wiki_wiki.page(page_title)

    # Check if the page exists
    if not page.exists():
        return {"error": "Page does not exist"}

    # Get the main title
    main_title = page.title

    # Dictionary to store all sections
    result = {
        "main_title": main_title,
        "sections": []
    }

    # Recursive function to extract section titles with their levels
    def process_sections(sections, level=2):
        section_list = []
        for section in sections:
            # Skip empty sections
            if section.title:
                section_info = {
                    "title": section.title,
                    "level": level
                }
                result["sections"].append(section_info)

            # Process subsections (recursively)
            if section.sections:
                process_sections(section.sections, level + 1)

    # Start processing from top-level sections
    process_sections(page.sections)

    return result


def save_to_json(data, filename):
    """
    Save the extracted Wikipedia section data to a JSON file.

    Args:
        data (dict): The dictionary containing Wikipedia section data
        filename (str): The name of the output file (without extension)

    Returns:
        str: Path to the saved file
    """
    # Add .json extension if not present
    if not filename.lower().endswith('.json'):
        filename += '.json'

    # Write the data to the JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return os.path.abspath(filename)


def save_to_csv(data, filename):
    """
    Save the extracted Wikipedia section data to a CSV file.

    Args:
        data (dict): The dictionary containing Wikipedia section data
        filename (str): The name of the output file (without extension)

    Returns:
        str: Path to the saved file
    """
    # Add .csv extension if not present
    if not filename.lower().endswith('.csv'):
        filename += '.csv'

    # Prepare the data for CSV format (flattening the hierarchy)
    csv_data = []

    # Add the main title as the first row
    csv_data.append({
        'level': 1,
        'title': data['main_title'],
        'indented_title': data['main_title']
    })

    # Add all sections
    for section in data['sections']:
        # Create indented title for better readability in CSV
        indent = "  " * (section['level'] - 2)
        indented_title = f"{indent}{section['title']}"

        csv_data.append({
            'level': section['level'],
            'title': section['title'],
            'indented_title': indented_title
        })

    # Write to CSV file
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['level', 'title', 'indented_title']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)

    return os.path.abspath(filename)


if __name__ == "__main__":
    page_title = "Gaza_war"
    result = parse_wikipedia_titles_api(page_title)

    # Print the results
    print(f"Main title: {result['main_title']}\n")
    print("Sections:")

    for section in result["sections"]:
        # Indent based on heading level
        indent = "  " * (section["level"] - 2)
        print(f"{indent}{'#' * section['level']} {section['title']}")

    # Save to JSON and CSV files
    # Use sanitized filename based on the page title
    sanitized_filename = page_title.replace(" ", "_").replace("(", "").replace(")", "")

    # json_path = save_to_json(result, f"wiki_{sanitized_filename}")
    # print(f"\nJSON file saved to: {json_path}")

    csv_path = save_to_csv(result, f"wiki_{sanitized_filename}")
    print(f"CSV file saved to: {csv_path}")