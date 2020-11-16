"""
This module contains helper methods for the main function
"""
import os
import math
import json
import datetime

from dominate.tags import body, div, a, h1, h2, h3, h4, p
from .getdata import get_sheet_contents, get_excluded_site_list
from .searchdata import get_search_result_by_term


def generate_email(report):
    """Generate the email content

    Args:
        report (dic): A dictionary containing the report

    Returns:
        string: The HTML text of the email body
    """
    email_body = body()
    header = h1("This weeks search results")
    email_body.add(header)
    for (term, country_dic) in report.items():
        term_header = h2(term)
        term_div = div(term_header)
        email_body.add(term_div)
        for (country, results) in country_dic.items():
            country_header = h3(country)
            country_div = div(country_header)
            email_body.add(country_div)
            for result in results:
                link = a(h4(result['title']))
                link['href'] = result['link']
                snippet = p(result['snippet'])
                item = div(link, snippet)
                country_div.add(item)

    return email_body


def send_email(receiver, content, send_grid_message):
    """Send an email

    Args:
        receiver (string): The email address of the recipient
        content (string): The content of the email
        send_grid_message (object): The send grid messager
    """
    message = {
        "personalizations": [{
            "to": [{
                "email": receiver
            }]}],
        "subject": "Alert Me Report for {}".format(datetime.date.today()),
        "content": [{
            "type": "text/HTML",
            "value": content
            }]}

    send_grid_message.set(json.dumps(message))


def remove_duplicates(report):
    """
    Remove all duplicate results from report

    Args:
        report (dic): The report to be sent

    Returns:
        dic: The filtered report
    """
    dic = {}

    for (_, country_dic) in report.items():
        for (country, results) in country_dic.items():
            new_results = []
            for result in results:
                title = result['title']
                link = result['link']

                if title not in dic and link not in dic:
                    new_results.append(result)

                dic[title] = True
                dic[link] = True

            country_dic[country] = new_results

    return report


def get_country_code(country):
    """
    Get the google country code for a country

    Args:
        country (string): The country to be searched against

    Returns:
        string: The country code
    """
    file_path = os.path.join(os.getcwd(), 'start_search/country_code.json')
    with open(file_path,'r') as content:
        my_dict=json.load(content)

    if country in my_dict:
        return my_dict[country]

    return ''


def get_all_required_data(google_sheet_id):
    """
    Get all the required data to effectively run the search

    Args:
        google_sheet_id (string): The sheet id where data is held

    Returns:
        tuple: (contents, turtle_meta, blacklisted_sites)
    """
    google_data_sheet_range = 'Sheet1!A1:B100'
    google_meta_sheet_range = 'turtle_meta!A1:C3'

    contents = get_sheet_contents(
        google_sheet_id,
        'values',
        google_data_sheet_range,
        False
    )

    turtle_meta = get_sheet_contents(
        google_sheet_id,
        'values',
        google_meta_sheet_range,
        True
    )

    blacklisted_sites = get_excluded_site_list(
        sheet_id=google_sheet_id,
        fields='values',
        doc_range='exclude_site!A1:A100'
    )

    return (contents, turtle_meta, blacklisted_sites)


def run_all_google_searches(contents, blacklisted_sites, num_of_groups, next_group, last_result):
    """
    Run the search for each pair of terms

    Args:
        contents (dict): A dictionary containing the Technical Terms and Countries to be searched
        blacklisted_sites (list): A list of sites that have been blacklisted
        num_of_groups (int): The number of places to group the countries into
        next_group (int): The next group of countries to be searched
        last_result (int): The last set of results returned

    Returns:
        list: A list of results gotten from all the search
    """
    report = []
    dic_report = dict()
    google_search_api_key = os.environ["GOOGLE_SEARCH_API_KEY"]

    # Group countries
    countries_len = len(contents['Country'])
    country_div = math.floor(countries_len / num_of_groups)

    start_country_group = next_group * country_div
    end_country_group = country_div*(next_group + 1)
    # Run google search against each term
    for term in contents['Technical Term']:
        dic_report[term] = dict()
        for country in contents['Country'][start_country_group:end_country_group]:
            dic_report[term][country] = []
            country_code = get_country_code(country.lower())

            joined_search_term = '{} {}'.format(term, country)

            results = get_search_result_by_term(
                key=google_search_api_key,
                term=joined_search_term,
                num_of_results=2,
                start_at=last_result,
                excluded_sites=blacklisted_sites,
                country=country_code
            )

            # Sort out the data to be displayed
            if int(results['searchInformation']['totalResults']) > 0:
                def rearange(item):
                    return {
                        "title": item['title'],
                        "link": item['link'],
                        "snippet": item['snippet'],
                    }
                for item in results['items']:
                    report.append(rearange(item))
                    dic_report[term][country].append(rearange(item))

    return dic_report
