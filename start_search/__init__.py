"""Contains the main function that is triggered when the timmer elapses

Returns:
    Module: The main module
"""
import os
import random
import logging
import datetime
import azure.functions as func

from .helper import generate_email, send_email, \
                    remove_duplicates, get_country_code, \
                    get_all_required_data, run_all_google_searches
from .getdata import update_data_in_google_sheet

def main(mytimer: func.TimerRequest, sendGridMessage: func.Out[str]) -> None:
    """The main function that is triggered when the timmer elapses

    Args:
        _ (func.TimerRequest): The "my_timer" azure function argument
        send_grid_message (func.Out[str]): The SendGrid API object

    Returns:
        None: This function returns None
    """
    try:
        google_sheet_id = os.environ["GOOGLE_SHEET_ID"]
        num_of_results = 2
        report = []

        contents, turtle_meta, blacklisted_sites = get_all_required_data(google_sheet_id)

        last_result = int(turtle_meta['last_result'][0])
        num_of_groups = int(turtle_meta['num_of_groups'][0])
        next_group = int(turtle_meta['next_group'][0])

        report = run_all_google_searches(
            contents=contents,
            blacklisted_sites=blacklisted_sites,
            num_of_groups=num_of_groups,
            next_group=next_group,
            last_result=last_result
        )
        report = remove_duplicates(report)

        # Update turtle meta
        update_data_in_google_sheet(
            google_sheet_id,
            'turtle_meta!A2:C2',
            [[next_group + 1 if next_group < num_of_groups - 1 else 0,
              num_of_groups,
              last_result + num_of_results if next_group == num_of_groups - 1 else last_result]]
        )

        # Send the email
        email_content = generate_email(report)
        send_email(os.environ["USER_EMAIL"], str(email_content), sendGridMessage)

        logging.info('Report was generated at %s', datetime.date.today())
    except Exception as err:
        send_email(os.environ["DEVELOPER_EMAIL"], str(err), sendGridMessage)
