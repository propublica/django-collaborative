import json
import logging
import re

import requests
from tablib import Dataset

from apiclient import discovery
from google.oauth2 import service_account

from django_models_from_csv.utils.csv import extract_key_from_csv_url


logger = logging.getLogger(__name__)


class PrivateSheetImporter:
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    def __init__(self, credentials):
        """
        Initialize a Google Private sheets reader service, given a
        service account credentials JSON. The credentials can either
        be a dict, JSON string or file (bytes). This routine will do
        all the proper conversions for internal use.
        """
        # file upload
        if type(credentials) == bytes:
            credentials = json.loads(credentials.decode("utf-8"))
        # JSON string, as stored in the DB
        elif type(credentials) == str:
            credentials = json.loads(credentials)
        # we need to have a decoded credentials dict by here
        creds = service_account.Credentials.from_service_account_info(
            credentials, scopes=scopes
        )
        # TODO: catch authentication error, return friendly msg. (we
        #       might we need to do this above as well)
        self.service = discovery.build("sheets", "v4", credentials=creds)

    def get_sheet_information(self, sheet_id):
        """
        Get information about a Google Sheet via the API. This will return
        edit links, information about the time zone, number of sub-sheets
        (a.k.a. worksheets in Excel) and the number of rows/cols for each.

        Google Sheet information API response:
            {
                'spreadsheetId': 'SHEET ID',
                'properties': {
                    'title': 'SHEET TITLE',
                    'locale': 'en_US',
                    'autoRecalc': 'ON_CHANGE',
                    'timeZone': 'America/Los_Angeles',
                    'defaultFormat': {
                        'backgroundColor': {
                            'red': 1,
                            'green': 1,
                            'blue': 1}
                        ,
                        'padding': {
                            'top': 2,
                            'right': 3,
                            'bottom': 2,
                            'left': 3}
                        ,
                        'verticalAlignment': 'BOTTOM',
                        'wrapStrategy': 'OVERFLOW_CELL',
                        'textFormat': {
                            'foregroundColor': {}
                            ,
                            'fontFamily': 'arial,sans,sans-serif',
                            'fontSize': 10,
                            'bold': False,
                            'italic': False,
                            'strikethrough': False,
                            'underline': False}
                    }
                },
                'sheets': [{
                    'properties': {
                        'sheetId': 00000000,
                        'title': 'Worksheet Title',
                        'index': 0,
                        'sheetType': 'GRID',
                        'gridProperties': {
                            'rowCount': 102,
                            'columnCount': 19,
                            'frozenRowCount': 1}
                    }
                }],
                'spreadsheetUrl': 'SHEET BROWSER URL HERE'
            }
        """
        # TODO: catch 403 here. if raised, this most likely means the
        #       user didn't set up the service account properly or didn't
        #       share the sheet with the service account
        return self.service.spreadsheets().get(
            spreadsheetId=sheet_id
        ).execute()

    def get_sheet_values(self, sheet_id, worksheet_index=0):
        """
        Get the rows of a Sheet, as an array of arrays where the first is
        the header row. Optionally, you can specify a worksheet index number,
        the default being the first (0 index).

        Google Sheet values API response:
            {
                'range': "'Form Responses 1'!A1:S102",
                'majorDimension': 'ROWS',
                'values': [[
                    'Timestamp',
                    'Question?',
                    'What date?',
                    'What time?'
                ],[
                    '4/8/2019 20:43:03',
                    'First response',
                    '4/9/2019',
                    '10:01:00 PM']]
            }
        """
        data = self.get_sheet_information(sheet_id)
        sheet = data["sheets"][worksheet_index]

        # name of the worksheet, if we pass this as the range
        # to the sheets API, it will give us all values on this
        # spreadsheet
        title = sheet["properties"]["title"]

        # TODO: catch error. see note in self.get_sheet_information (above)
        return self.service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=title
        ).execute()["values"]

    def get_csv_from_url(self, sheet_url):
        """
        Return a CSV (text data) from a protected Google sheet URL.
        """
        sheet_id = extract_key_from_csv_url(sheet_url)
        values = self.get_sheet_values(sheet_id)
        headers = [re.sub("[:,\"'\n]", "", h) for h in values.pop(0)]
        logger.error("Sheet Headers: %s" % headers)
        # TODO: this should be shared across screendoor importer
        data = Dataset(headers=headers)
        n_headers = len(headers)
        for row in values:
            n_cols = len(row)
            if n_cols < n_headers:
                row += [""] * (n_headers - n_cols)
            data.append(row)
        csv_data = data.export("csv")
        return csv_data
