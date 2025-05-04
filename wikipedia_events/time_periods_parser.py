import csv
import re
import os
from datetime import datetime, timedelta

def extract_time_periods(input_csv, output_csv):
    """
    Parse Wikipedia section titles from a CSV file and extract date/time periods.

    Args:
        input_csv (str): Path to the input CSV file with Wikipedia section titles
        output_csv (str): Path to save the output CSV with extracted time periods
    """
    # Patterns to match different date formats
    patterns = [
        # Pattern for dates with month and year: "October 2023"
        r'(?P<month>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<year>\d{4})',

        # Pattern for date ranges with months and years: "October–November 2023"
        r'(?P<month1>January|February|March|April|May|June|July|August|September|October|November|December)[-–](?P<month2>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<year>\d{4})',

        # Pattern for date ranges with month-year to month-year: "December 2023 – January 2024"
        r'(?P<month1>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<year1>\d{4})[-–]\s*(?P<month2>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<year2>\d{4})',

        # Pattern for full dates: "7 October" or "7 October 2023"
        r'(?P<day>\d{1,2})\s+(?P<month>January|February|March|April|May|June|July|August|September|October|November|December)(?:\s+(?P<year>\d{4}))?',
    ]

    # Read the input CSV
    titles_with_periods = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row['title']

            # Skip non-title rows or irrelevant sections
            if title in ['See also', 'Notes', 'References', 'External links']:
                continue

            # Check if the title contains a time period
            found_match = False
            for pattern in patterns:
                matches = re.search(pattern, title, re.IGNORECASE)
                if matches:
                    period_info = extract_period_info(matches)
                    titles_with_periods.append({
                        'title': title,
                        'period': period_info['formatted_period'],
                        'start_date': period_info['start_date'],
                        'end_date': period_info['end_date'],
                        'duration_days': period_info['duration_days'],
                        'level': row['level'],
                        'indented_title': row['indented_title']
                    })
                    found_match = True
                    break

    # Sort by chronological order if dates are available
    titles_with_periods.sort(key=lambda x: x['start_date'] if x['start_date'] else '9999-12-31')

    # Write the output CSV
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['title', 'period', 'start_date', 'end_date', 'duration_days', 'level', 'indented_title']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(titles_with_periods)

    return len(titles_with_periods)


def extract_period_info(matches):
    """
    Extract structured period information from regex matches.

    Args:
        matches: Regex match object containing date components

    Returns:
        dict: Structured period information
    """

    # Convert month name to number
    def month_to_num(month_name):
        if not month_name:
            return None
        try:
            return datetime.strptime(month_name, '%B').month
        except ValueError:
            return None

    # Initialize result dictionary
    result = {
        'formatted_period': '',
        'start_date': None,
        'end_date': None,
        'duration_days': None
    }

    # Get all matched groups
    match_dict = matches.groupdict()

    # Case 1: Full date (day + month + optional year)
    if 'day' in match_dict and match_dict['day']:
        day = int(match_dict['day'])
        month = month_to_num(match_dict['month'])
        year = int(match_dict['year']) if 'year' in match_dict and match_dict['year'] else datetime.now().year

        result[
            'formatted_period'] = f"{day} {match_dict['month']} {year if 'year' in match_dict and match_dict['year'] else ''}"
        result['start_date'] = f"{year}-{month:02d}-{day:02d}"
        result['end_date'] = result['start_date']
        result['duration_days'] = 1

    # Case 2: Month + Year
    elif 'month' in match_dict and match_dict['month'] and 'year' in match_dict and match_dict['year']:
        month = month_to_num(match_dict['month'])
        year = int(match_dict['year'])

        # Get the last day of the month
        if month == 12:
            next_month_year = year + 1
            next_month = 1
        else:
            next_month_year = year
            next_month = month + 1

        last_day = (datetime(next_month_year, next_month, 1) - timedelta(days=1)).day

        result['formatted_period'] = f"{match_dict['month']} {year}"
        result['start_date'] = f"{year}-{month:02d}-01"
        result['end_date'] = f"{year}-{month:02d}-{last_day}"

        # Calculate duration
        start_date = datetime.strptime(result['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(result['end_date'], '%Y-%m-%d')
        result['duration_days'] = (end_date - start_date).days + 1

    # Case 3: Month Range in same year
    elif 'month1' in match_dict and match_dict['month1'] and 'month2' in match_dict and match_dict[
        'month2'] and 'year' in match_dict and match_dict['year']:
        month1 = month_to_num(match_dict['month1'])
        month2 = month_to_num(match_dict['month2'])
        year = int(match_dict['year'])

        # Get the last day of the end month
        if month2 == 12:
            next_month_year = year + 1
            next_month = 1
        else:
            next_month_year = year
            next_month = month2 + 1

        last_day = (datetime(next_month_year, next_month, 1) - datetime.timedelta(days=1)).day

        result['formatted_period'] = f"{match_dict['month1']} - {match_dict['month2']} {year}"
        result['start_date'] = f"{year}-{month1:02d}-01"
        result['end_date'] = f"{year}-{month2:02d}-{last_day}"

        # Calculate duration
        start_date = datetime.strptime(result['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(result['end_date'], '%Y-%m-%d')
        result['duration_days'] = (end_date - start_date).days + 1

    # Case 4: Full date range (month-year to month-year)
    elif 'month1' in match_dict and match_dict['month1'] and 'year1' in match_dict and match_dict[
        'year1'] and 'month2' in match_dict and match_dict['month2'] and 'year2' in match_dict and match_dict['year2']:
        month1 = month_to_num(match_dict['month1'])
        year1 = int(match_dict['year1'])
        month2 = month_to_num(match_dict['month2'])
        year2 = int(match_dict['year2'])

        # Get the last day of the end month
        if month2 == 12:
            next_month_year = year2 + 1
            next_month = 1
        else:
            next_month_year = year2
            next_month = month2 + 1

        last_day = (datetime(next_month_year, next_month, 1) - datetime.timedelta(days=1)).day

        result['formatted_period'] = f"{match_dict['month1']} {year1} - {match_dict['month2']} {year2}"
        result['start_date'] = f"{year1}-{month1:02d}-01"
        result['end_date'] = f"{year2}-{month2:02d}-{last_day}"

        # Calculate duration
        start_date = datetime.strptime(result['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(result['end_date'], '%Y-%m-%d')
        result['duration_days'] = (end_date - start_date).days + 1

    return result



if __name__ == "__main__":
    # Define the input and output file paths
    input_csv = "../data/wikipedia/wiki_Gaza_war.csv"  # Update this path to match your file location
    output_csv = "../data/wikipedia/Gaza_war_time_periods.csv"  # Update this path for your output

    # Process the file
    count = extract_time_periods(input_csv, output_csv)
    print(f"Found {count} titles with time periods. Results saved to '{output_csv}'.")
