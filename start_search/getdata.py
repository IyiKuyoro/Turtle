"""
This module contains all the required functions to get data from
the google sheet for this project

Returns:
    Module: The get data module containing a list of relevant functions
"""
import os

from googleapiclient import discovery
from google.oauth2 import service_account

def _get_service():
    """Create a google sheets version 4 service

    Returns:
        Discovery: The created google sheet service
    """
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        secrete_file = os.path.join(os.getcwd(), 'secret.json')

        credentials = service_account.Credentials.from_service_account_file(secrete_file,
                                                                            scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        return service
    except Exception:
        # ToDo Raise a server error here
        raise


def _get_data_from_google_sheet(sheet_id, fields, doc_range):
    """Retrieve data from a google sheet

    Args:
        sheet_id (string): The google sheet id
        fields (string): The fields to be included in the http response
        doc_range (string): The range of cells to be retrived from the sheet

    Returns:
        Dic: The response data gotten from the request
    """
    sheet_service = _get_service()
    request = sheet_service.spreadsheets().values().get(spreadsheetId=sheet_id,
                                                        range=doc_range,
                                                        fields=fields)
    return request.execute()


def update_data_in_google_sheet(sheet_id, doc_range, values):
    """Update the app meta

    Args:
        sheet_id (string): The google sheet id
        doc_range (string): The range to be updated
        values (list): A list of data to be entered into the cells

    Returns:
        Dic: The response data gotten from the request
    """
    sheet_service = _get_service()
    value = {
        "range": doc_range,
        "majorDimension": "ROWS",
        "values": values
    }
    value_input_option = 'USER_ENTERED'
    request = sheet_service.spreadsheets().values().update(spreadsheetId=sheet_id,
                                                           valueInputOption=value_input_option,
                                                           range=doc_range,
                                                           body=value)
    return request.execute()


def parse_data(data, meta):
    """Parese the google sheet data into readable data

    Args:
        data ([type]): [description]

    Returns:
        [type]: [description]
    """
    result = data['values']

    if meta:
        return {
            result[0][0]: [value[0]
                           for index, value in enumerate(result)
                           if index != 0 and value[0] != ''],
            result[0][1]: [value[1]
                           for index, value in enumerate(result)
                           if index != 0 and value[1] != ''],
            result[0][2]: [value[2]
                           for index, value in enumerate(result)
                           if index != 0 and value[2] != '']
        }
    else:
        return {
            result[0][0]: [value[0]
                           for index, value in enumerate(result)
                           if index != 0 and value[0] != ''],
            result[0][1]: [value[1]
                           for index, value in enumerate(result)
                           if index != 0 and value[1] != '']
        }


def get_sheet_contents(sheet_id, fields, doc_range, meta):
    """Get the content of a google sheet

    Args:
        sheet_id (string): The google sheet id
        fields (string): The fields that should be returned in the response of the request
        doc_range (string): The range of cells to be returned
        meta (boolean): Are you trying ro pull meta data

    Returns:
        dic: A dictionary of values containing the sheet data
    """
    contents = _get_data_from_google_sheet(sheet_id, fields, doc_range)
    return parse_data(contents, meta)
