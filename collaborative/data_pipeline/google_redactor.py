import logging
import json
import sys
import tempfile

from django.conf import settings
import google.cloud.dlp

from django_models_from_csv.models import CredentialStore


logger = logging.getLogger(__name__)


COLLAB_PIPE_GOOGLE_DLP_PII_FILTERS = getattr(
    settings, "COLLAB_PIPE_GOOGLE_DLP_PII_FILTERS",
    ["EMAIL_ADDRESS", "FIRST_NAME", "LAST_NAME", "PHONE_NUMBER"]
)


def deidentify_with_mask(project, string, info_types, masking_character=None,
                         number_to_mask=0, dlp=None):
    """Uses the Data Loss Prevention API to deidentify sensitive data in a
    string by masking it with a character.
    Args:
        project: The Google Cloud project id to use as a parent resource.
        item: The string to deidentify (will be treated as text).
        masking_character: The character to mask matching sensitive data with.
        number_to_mask: The maximum number of sensitive characters to mask in
            a match. If omitted or set to zero, the API will default to no
            maximum.
    Returns:
        None; the response from the API is printed to the terminal.
    """


    # Convert the project id into a full resource id.
    parent = dlp.project_path(project)

    # Construct inspect configuration dictionary
    inspect_config = {
        'info_types': [{'name': info_type} for info_type in info_types]
    }

    # Construct deidentify configuration dictionary
    deidentify_config = {
        'info_type_transformations': {
            'transformations': [
                {
                    'primitive_transformation': {
                        'character_mask_config': {
                            'masking_character': masking_character,
                            'number_to_mask': number_to_mask
                        }
                    }
                }
            ]
        }
    }

    # Construct item
    item = {'value': string}

    # Call the API
    response = dlp.deidentify_content(
        parent, inspect_config=inspect_config,
        deidentify_config=deidentify_config, item=item)

    return response.item.value


def run(row, columns=None):
    try:
        dlp_cred = CredentialStore.objects.get(
            name="google_dlp_credentials"
        )
    except CredentialStore.DoesNotExist:
        return

    account_json = json.loads(dlp_cred.credentials)

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f_in:
        f_in.write(dlp_cred.credentials)
        f_in.flush()
        try:
            # We have to close this in Windows
            f_in.close()
        except Exception as e:
            pass # this means we're on a unix env

        dlp = google.cloud.dlp.DlpServiceClient.from_service_account_json(
            f_in.name
        )
        project = account_json.get("project_id")

        redact_column_names = []
        for column in columns:
            if not column.get("redact"):
                continue
            redact_column_names.append(column.get("name"))
        for header in row:
            if header not in redact_column_names:
                continue
            try:
                row[header] = deidentify_with_mask(
                    project,
                    row[header],
                    COLLAB_PIPE_GOOGLE_DLP_PII_FILTERS,
                    dlp=dlp,
                )
            except Exception as e:
                logger.warning("Google DLP error: %s" % (e))
