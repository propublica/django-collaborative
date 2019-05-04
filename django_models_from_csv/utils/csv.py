import re

import requests


SHEETS_BASE = "https://docs.google.com/spreadsheet"


def extract_key_from_csv_url(url):
    """
    Extract the Google spreadsheet key from a Google Sheets share URL so
    we can convert it into a CSV export URL.
    """
    matches = re.findall(
        "https://docs.google.com/spreadsheets/d/([^/]+)/edit",
        url
    )
    if not matches:
        raise ValueError(_("Invalid Google Sheets share URL"))
    return matches[0]


def fetch_csv(csv_url):
    """
    Take a wither a Google Sheet share link like this ...
        https://docs.google.com/spreadsheets/d/KEY_HERE/edit#gid=09232

    ... or a normal CSV url ...
        https://some.site/my.csv

    ... and return the corresponding CSV.
    """
    url = csv_url
    if csv_url.startswith(SHEETS_BASE):
        key = extract_key_from_csv_url(csv_url)
        url = '{0}/ccc?key={1}&output=csv'.format(
            SHEETS_BASE, key
        )
    r = requests.get(url)
    data = r.text
    return data



