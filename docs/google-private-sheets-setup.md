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

    ![Create new project](01-create-project.png "Create a new project")

2. From the 'Enable APIs and Services' screen, search for "Google Sheets" and
   click on the "Google Sheets API" box.

    ![Click 'Enable APIs and Services'](02-goto-enable-apis-and-services.png "Click 'Enable APIs and Services'")

    ![Enable Sheets API](03-enable-sheets-apis.png "Enable Sheets API")

3. In the left panel, click the "Credentials" button.

    ![Click 'Credentials'](04-click-credentials.png "Click 'Credentials'")

4. Then click "Create Credentials" menu towards the top of the page that loads
and select "Service account".

    ![Create Service Account](05-create-service-account.png "Create Service Account credentials")

5. In the wizard that loads, name your service account. I chose
   "private sheet reader". Then click "Create".

    ![Name Service Account](06-name-service-account.png "Name your service account")

6. In the next page, add the "Viewer" role to your service account and
   then click "Continue"

    ![Add 'Viewer' role](07-add-viewer-role.png "Add the 'Viewer' role")

7. Towards the bottom of the next page, click "Create Key". A right tab will
   appear.

    ![Click 'Create Key'](08-create-key.png "Click 'Create Key'")

8. Select the "JSON" option (should be default) and click "Done". Save the file
   that it gives you.

    ![Create a JSON key](09-create-json-key.png "Create a JSON key")

9. Copy the service account email address in the "Service Accounts" list.

    ![Copy account email](10-copy-service-account-email.png "Copy the service account email")

### Giving collaborative the permission to view your sheet

1. Go back to your private google sheet and share it with the service account's email address. Click "Send".

    ![Share your sheets with this account](11-share-with-service-account-email.png "Share your private sheets with this account")

2. Finally, upload the credentials JSON file below. Done! All future private
   sheets can be imported by simply sharing it with the service account email
   and checking the "private sheet" checkbox during the import.

    ![Uploading credentials](12-uploading-credentials.png "Uploading credentials")

## Subsequent imports of private sheets

Once the above instructions have been successfully followed, and your private
sheet has been imported successfully, you can import new private sheets in two
steps:

1. Share your private spreadsheet with the service account.

    ![Share your sheets with this account](11-share-with-service-account-email.png "Share your private sheets with this account")

2. Select the "This is a private Google spreadsheet" option in the
   import screen.

    ![Click the private sheet checkbox](13-check-private-sheet.png "Click the private sheet checkbox")

