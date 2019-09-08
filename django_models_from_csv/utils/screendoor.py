import logging
import re

import requests
from tablib import Dataset


logger = logging.getLogger(__name__)


class ScreendoorImporter:
    def __init__(self, api_key=None, base_url="https://screendoor.dobt.co",
                 per_page=100):
        self.api_key = api_key
        self.base_url = base_url
        self.per_page = per_page

    def get_form(self, project_id, form_id=None):
        if not form_id:
            url = "%s/api/projects/%s/forms?v=1&api_key=%s" % (
                self.base_url, project_id, self.api_key
            )
            response = requests.get(url)
            data = response.json()
            return data[0]
        else:
            url = "%s/api/projects/%s/forms/%s?v=1&api_key=%s" % (
                self.base_url, project_id, form_id, self.api_key
            )
            response = requests.get(url)
            return response.json()

    def get_responses(self, project_id, form_id):
        url = "%s/api/projects/%s/responses?v=1&api_key=%s&per_page=%s" % (
            self.base_url, project_id, self.api_key, self.per_page
        )

        # get all pages. first page response has a Link header with
        # a list of next, pref, first, last URLs. Keep getting these
        # until no more pages exist. (stolen from Ken's electionland code)
        all_data = []
        while url:
            response = requests.get(url)
            all_data += response.json()
            url = response.links.get('next', {}).get('url', None)

        # filter down responses to correct form
        return [d for d in all_data if d.get("form_id") == form_id]

    def get_header_maps(self, form_data):
        header_map = {}
        for field in form_data.get("field_data", []):
            label = field.get("label")
            id = field.get("id")
            header_map[id] = "%s (ID: %s)" % (label, id)
        return header_map

    def attachment_link(self, data):
        return "%s/attachments/%s/download" % (
            self.base_url,
            data.get("id")
        )

    def build_csv_from_data(self, form_data, response_data):
        id_to_label = self.get_header_maps(form_data)
        headers = ["id"]
        for c in id_to_label.values():
            headers.append(re.sub(r"[\,\n\r]+", "", c))

        data = Dataset(headers=headers)
        for response_info in response_data:
            response = response_info.get("responses", {})
            row_id = response_info["id"]
            row = [row_id]
            for pk in response.keys():
                value = response.get(pk)
                if isinstance(value, str) or not value:
                    row.append(value)
                # attachment
                elif isinstance(value, list) and value[0].get("filename"):
                    links = " ".join([self.attachment_link(rec) for rec in value])
                    row.append(links)
                elif value.get("checked"):
                    row.append(", ".join(value.get("checked")))
                elif value.get("other_text"):
                    row.append(value.get("other_text"))
                # Screendoor dates come across like this:
                # {'day': '01', 'year': '2019', 'month': '01'}
                elif value.get("day") and value.get("year") \
                        and value.get("month"):
                    row.append("{year}-{month}-{day}".format(
                        **value
                    ))
                else:
                    logger.error("Unhandled value type: %s (%s)." % (
                        value, type(value)
                    ))
                    # logger.error("Response data structure: %s" % (
                    #     response
                    # ))
                    row.append(None)
            data.append(row)
        return data.export("csv")

    def build_csv(self, project_id, form_id=None):
        """
        Take our screendoor project ID and (optionally) form ID and
        build a CSV, using the labels from the form. This can then be
        fed into the normal CSV->model system for table building.

        If you don't supply a form_id, the first form in the
        project will be pulled.
        """
        form_data = self.get_form(project_id, form_id=form_id)
        if not form_id:
            form_id = form_data["id"]
        response_data = self.get_responses(project_id, form_id)
        return self.build_csv_from_data(form_data, response_data)
