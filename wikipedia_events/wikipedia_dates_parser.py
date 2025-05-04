import requests
from bs4 import BeautifulSoup
import re
import csv
import nltk
from nltk.tokenize import sent_tokenize

# Download the necessary NLTK data for sentence tokenization
nltk.download('punkt', quiet=True)


def extract_wikipedia_dates(url):
    """
    Extract dates and their contexts from a Wikipedia page.

    Args:
        url (str): URL of the Wikipedia page

    Returns:
        list: A list of tuples (date, context)
    """
    # Fetch the Wikipedia page content
    print(f"Fetching content from {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the Wikipedia page. Status code: {response.status_code}")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the main content of the page
    content = soup.find(id="mw-content-text")
    if not content:
        print("Failed to locate the main content of the page.")
        return []

    # Extract the main article div
    main_content = content.find("div", {"class": "mw-parser-output"})
    if not main_content:
        main_content = content  # Fallback

    # Remove non-relevant sections
    for elem in main_content.find_all(['div', 'table'],
                                      {'class': ['navbox', 'vertical-navbox', 'reference', 'reflist', 'infobox']}):
        elem.decompose()

    # Extract all text from paragraphs, list items, and headings
    text_elements = main_content.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    # Define date patterns to search for
    date_patterns = [
        # Format: Month Day, Year (e.g., "October 7, 2023")
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b',

        # Format: Day Month Year (e.g., "7 October 2023")
        r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',

        # Format: DD.MM.YYYY or DD-MM-YYYY or DD/MM/YYYY
        r'\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b',

        # Format: Month Year (e.g., "October 2023")
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
    ]

    # Store date contexts
    date_contexts = {}

    # Process each text element
    print("Analyzing text and extracting dates...")
    for element in text_elements:
        text = element.get_text().strip()
        if not text:
            continue

        # Tokenize text into sentences
        sentences = sent_tokenize(text)

        for sentence in sentences:
            # Check each date pattern
            for pattern in date_patterns:
                matches = re.finditer(pattern, sentence)
                for match in matches:
                    date_str = match.group(0)

                    # Store the date and context
                    if date_str not in date_contexts:
                        date_contexts[date_str] = []

                    if sentence not in date_contexts[date_str]:
                        date_contexts[date_str].append(sentence)

    # Convert dictionary to list of tuples
    date_sentences = []
    for date, contexts in date_contexts.items():
        for context in contexts:
            date_sentences.append((date, context))

    # Sort by date string (alphabetical sort)
    date_sentences.sort(key=lambda x: x[0])

    return date_sentences


def write_to_csv(data, filename):
    """
    Write the extracted date data to a CSV file.

    Args:
        data (list): List of tuples (date, context)
        filename (str): Name of the output CSV file

    Returns:
        str: Status message
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Date', 'Context'])
            for date, sentence in data:
                csv_writer.writerow([date, sentence])

        return f"Data has been written to {filename}"
    except Exception as e:
        return f"Error writing to CSV: {str(e)}"



if __name__ == "__main__":
    url = 'https://en.wikipedia.org/wiki/Gaza_war'
    print(f"Starting extraction process...")

    date_data = extract_wikipedia_dates(url)
    print(f"Found {len(date_data)} date references.")

    output_filename = '../data/wikipedia/gaza_war_dates.csv'
    result = write_to_csv(date_data, output_filename)
    print(result)
    print("Process completed successfully.")
