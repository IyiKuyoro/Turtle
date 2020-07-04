"""Contains the main function that is triggered when the timmer elapses

Returns:
    Module: The main module
"""
import datetime
import logging
import math
import json
import os

from dominate.tags import body, div, a, h1, p
import azure.functions as func
from .getdata import get_sheet_contents, update_data_in_google_sheet
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
    for _, results in report.items():
        for result in results:
            link = a(h1(result['title']))
            link['href'] = result['link']
            snippet = p(result['snippet'])
            item = div(link, snippet)
            email_body.add(item)

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


def main(_: func.TimerRequest, send_grid_message: func.Out[str]) -> None:
    """The main function that is triggered when the timmer elapses

    Args:
        _ (func.TimerRequest): The "my_timer" azure function argument
        send_grid_message (func.Out[str]): The SendGrid API object

    Returns:
        None: This function returns None
    """
    try:
        google_sheet_id = os.environ["GOOGLE_SHEET_ID"]
        google_data_sheet_range = 'Sheet1!A1:B100'
        google_meta_sheet_range = 'turtle_meta!A1:C3'
        google_search_api_key = os.environ["GOOGLE_SEARCH_API_KEY"]
        num_of_results = 2

        report = {}

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
        last_result = int(turtle_meta['last_result'][0])
        num_of_groups = int(turtle_meta['num_of_groups'][0])
        next_group = int(turtle_meta['next_group'][0])

        # Group countries
        countries_len = len(contents['Country'])
        country_div = math.floor(countries_len / num_of_groups)
        group_countries = []
        for i in range(num_of_groups):
            group_countries.append(' '.join(contents['Country'][i*country_div:country_div*(i + 1)]))

        # Run google search against each term
        for term in contents['Technical Term']:
            country = group_countries[next_group]
            search_term = '{} {}'.format(term, country)
            results = get_search_result_by_term(
                google_search_api_key, search_term,
                num_of_results, last_result
            )

            if int(results['searchInformation']['totalResults']) > 0:
                def rearange(item):
                    return {
                        "title": item['title'],
                        "link": item['link'],
                        "snippet": item['snippet'],
                    }
                report[search_term] = map(rearange, results['items'])

        # Update turtle meta
        update_data_in_google_sheet(
            google_sheet_id,
            'turtle_meta!A2:C2',
            [[next_group + 1 if next_group < 3 else 0,
              num_of_groups,
              last_result + 2 if next_group == 3 else last_result]]
        )

        # Send the email
        email_content = generate_email(report)
        send_email(os.environ["USER_EMAIL"], str(email_content), send_grid_message)

        logging.info('Report was generated at %s', datetime.date.today())
    except Exception: # Change to server error
        # Send main informing of server error to developer
        raise
