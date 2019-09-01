# Google Private Sheets Instructions

## Initial Setup

Importing private Google Sheets consists of several steps, when importing
one for the first time. The basic steps consist of creating a Google
[service account](https://cloud.google.com/iam/docs/understanding-service-accounts)
that can access Google Sheets, uploading the account credentials file to the
collaborative web app, and sharing the sheet with the account email.

You only need to create a service account once. Subsequent imports will re-use
the service account credentials, granted you share the private spreadsheet
with account.

Step-by-step instructions are broken up into two steps: creating the account
and granting access to the sheet.

### Creating a service account and credentials file

1. Go to the [Google Console](https://console.developers.google.com/projectselector/apis/library?pli=1&supportedpurview=project) and create a new project.

    ![Create new project](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/01-create-project.png)

2. From the 'Enable APIs and Services' screen, search for "Google Sheets" and
   click on the "Google Sheets API" box.

    ![Click 'Enable APIs and Services'](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/02-goto-enable-apis-and-services.png)

    ![Enable Sheets API](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/03-enable-sheets-apis.png)

3. In the left panel, click the "Credentials" button.

    ![Click 'Credentials'](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/04-click-credentials.png)

4. Then click "Create Credentials" menu towards the top of the page that loads
and select "Service account".

    ![Create Service Account](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/05-create-service-account.png)

5. In the wizard that loads, name your service account. I chose
   "private sheet reader". Then click "Create".

    ![Name Service Account](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/06-name-service-account.png)

6. In the next page, add the "Viewer" role to your service account and
   then click "Continue"

    ![Add 'Viewer' role](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/07-add-viewer-role.png)

7. Towards the bottom of the next page, click "Create Key". A right tab will
   appear.

    ![Click 'Create Key'](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/08-create-key.png)

8. Select the "JSON" option (should be default) and click "Done". Save the file
   that it gives you.

    ![Create a JSON key](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/09-create-json-key.png)

9. Copy the service account email address in the "Service Accounts" list.

    ![Copy account email](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/10-copy-service-account-email.png)

### Giving collaborative the permission to view your sheet

1. Go back to your private google sheet and share it with the service account's email address. Click "Send".

    ![Share your sheets with this account](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/11-share-with-service-account-email.png)

2. Finally, upload the credentials JSON file below. Done! All future private
   sheets can be imported by simply sharing it with the service account email
   and checking the "private sheet" checkbox during the import.

    ![Uploading credentials](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/12-uploading-credentials.png)

## Subsequent imports of private sheets

Once the above instructions have been successfully followed, and your private
sheet has been imported successfully, you can import new private sheets in two
steps:

1. Share your private spreadsheet with the service account.

    ![Share your sheets with this account](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/11-share-with-service-account-email.png)

2. Select the "This is a private Google spreadsheet" option in the
   import screen.

    ![Click the private sheet checkbox](https://raw.githubusercontent.com/propublica/django-collaborative/master/django_models_from_csv/static/django_models_from_csv/instructions/13-check-private-sheet.png)

