import httplib2
import os

from googleapiclient import discovery
from google.oauth2 import service_account

def _get_service():
    """Create a google sheets version 4 service

    Returns:
        Discovery: The created google sheet service
    """
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        secrete_file = os.path.join(os.getcwd(), 'secret.json')

        credentials = service_account.Credentials.from_service_account_file(secrete_file, scopes=scopes)
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
    r = sheet_service.spreadsheets().values().get(spreadsheetId=sheet_id, range=doc_range, fields=fields)
    return r.execute()


def parse_data(data):
    """Parese the google sheet data into readable data

    Args:
        data ([type]): [description]

    Returns:
        [type]: [description]
    """
    result = data['values']

    return {
        'term': [value[0] for index, value in enumerate(result) if index != 0 and value[0] != ''],
        'country': [value[1] for index, value in enumerate(result) if index != 0 and value[1] != '']
    }


def get_sheet_contents(sheet_id, fields, doc_range):
    contents = _get_data_from_google_sheet(sheet_id, fields, doc_range)
    return parse_data(contents)
