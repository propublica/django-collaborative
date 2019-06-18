import re

import requests
from tablib import Dataset

from django_models_from_csv.utils.csv import extract_key_from_csv_url


class GoogleOAuth:
    API_HOST = "https://www.googleapis.com{path}"
    GET_TOKEN_URL = "/oauth2/v4/token"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def check_for_failure(self, response):
        # TODO: handle failure response
        return response.json()

    def get_refreshed_token(self, refresh_token):
        """
        Refresh an expired access token. Returns the following
        data structure on success:
            {
              'access_token':'TOKEN HERE',
              'expires_in':3920,
              'token_type':'Bearer'
            }
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        url = self.API_HOST.format(path=self.GET_TOKEN_URL)
        r = requests.post(url, data=data)
        return self.check_for_failure(r)

    def get_initial_token(self, code):
        """
        Turn a user's copypasta access code into a usable API access
        token. These expire quickly, so we need to act fast (or refresh
        them).

        As a referense, a successful Google OAuth token request response will
        look like the following:
            {
              'access_token': 'ACCESS TOKEN HERRE',
              'expires_in': 3600,
              'refresh_token': 'REFRESH TOKEN HERE',
              'scope': 'https://www.googleapis.com/auth/spreadsheets.readonly',
              'token_type': 'Bearer'
            }

        Until we implement token refresh, users will be asked to re-auth
        every time they need to update a private Sheet.
        """
        data = {
            "code": code,
            "client_id": self.client_id,
            "grant_type": "authorization_code",
            "client_secret": self.client_secret,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
        }
        url = self.API_HOST.format(path=self.GET_TOKEN_URL)
        r = requests.post(url, data=data)
        return self.check_for_failure(r)

    def get_access_data(self, code=None, refresh_token=None):
        """
        Unified wrapper for getting auth data (access & refresh tokens)
        from a code or refresh token. Handles refresh OAuth-ness.
        """
        # TODO: handle code failure (401), fallback to refresh if available
        if code:
            return self.get_initial_token(code)
        elif refresh_token:
            return self.get_refreshed_token(refresh_token)
        else:
            raise ValueError("No auth code or refresh token supplied for auth")


class PrivateSheetImporter:
    SHEETS_HOST = "https://sheets.googleapis.com"
    GET_SHEET_URL = "/v4/spreadsheets/{sheet_id}"
    GET_SHEET_VALUES_URL = "/v4/spreadsheets/{sheet_id}/values/{start}:{end}"

    def __init__(self, access_token):
        self.access_token = access_token

    def authed_url(self, path):
        return self.SHEETS_HOST + path + "?access_token=%s" % self.access_token

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
        path = self.GET_SHEET_URL.format(sheet_id=sheet_id)
        url = self.authed_url(path)
        r = requests.get(url)
        data = r.json()
        return data

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
        end_row = sheet["properties"]["gridProperties"]["rowCount"]
        path = self.GET_SHEET_VALUES_URL.format(
            sheet_id=sheet_id, start=1, end=end_row
        )
        url = self.authed_url(path)
        r = requests.get(url)
        sheet_data = r.json()
        return sheet_data["values"]

    def get_csv_from_url(self, sheet_url):
        """
        Return a CSV (text data) from a protected Google sheet URL.
        """
        sheet_id = extract_key_from_csv_url(sheet_url)
        values = self.get_sheet_values(sheet_id)
        headers = values.pop(0)
        # TODO: this should be shared across screendoor importer
        data = Dataset(headers=[re.sub("[\,\n\r]+", "", h) for h in headers])
        for row in values:
            data.append(row)
        return data.export("csv")
