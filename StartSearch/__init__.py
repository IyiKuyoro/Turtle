import datetime
import logging
import math
import json
import os

import azure.functions as func
from dominate.tags import body, div, a, h1, p
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


def send_email(to, content, sendGridMessage):
    """Send an email

    Args:
        to (string): The email address of the recipient
        content (string): The content of the email
        sendGridMessage (object): The send grid messager
    """
    message = {
        "personalizations": [{
        "to": [{
            "email": to
            }]}],
        "subject": "Alert Me Report for {}".format(datetime.date.today()),
        "content": [{
            "type": "text/HTML",
            "value": content }]}

    sendGridMessage.set(json.dumps(message))


def main(mytimer: func.TimerRequest, sendGridMessage: func.Out[str]) -> None:
    try:
        GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
        GOOGLE_DATA_SHEET_RANGE = 'Sheet1!A1:B100'
        GOOGLE_META_SHEET_RANGE = 'turtle_meta!A1:C3'
        GOOGLE_SEARCH_API_KEY = os.environ["GOOGLE_SEARCH_API_KEY"]
        NUM_OF_RESULTS = 2

        report = {}

        contents = get_sheet_contents(
            GOOGLE_SHEET_ID,
            'values',
            GOOGLE_DATA_SHEET_RANGE,
            False
            )

        turtle_meta = get_sheet_contents(
            GOOGLE_SHEET_ID,
            'values',
            GOOGLE_META_SHEET_RANGE,
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
            results = get_search_result_by_term(GOOGLE_SEARCH_API_KEY, search_term, NUM_OF_RESULTS, last_result)

            if int(results['searchInformation']['totalResults']) > 0:
                def filter(item): 
                    return {
                        "title": item['title'],
                        "link": item['link'],
                        "snippet": item['snippet'],
                    }
                report[search_term] = map(filter, results['items'])

        # Update turtle meta
        update_data_in_google_sheet(
            GOOGLE_SHEET_ID,
            'turtle_meta!A2:C2',
            [[next_group + 1 if next_group < 3 else 0,
            num_of_groups,
            last_result + 2 if next_group == 3 else last_result]]
        )

        # Send the email
        email_content = generate_email(report)
        send_email(os.environ["USER_EMAIL"], str(email_content), sendGridMessage)

        logging.info('Report was generated at %s', datetime.date.today())
    except Exception: # Change to server error
        # Send main informing of server error to developer
        raise
