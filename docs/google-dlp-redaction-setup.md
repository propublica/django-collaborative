1. Go to the [Google Developer's Console](https://console.developers.google.com)
2. Create a new project, or select an existing one (if you've already set up Google private sheets, for example).
2. From the drop down navigation menu on the top left, select "IAM &
   admin" &rarr; "Service accounts".

    ![Select service accounts](/static/collaborative/dlp/01-navigate-to-service-accounts.png)

3. Click "Create Service Account" at the top of the service accounts page.

    ![Select create new service account](/static/collaborative/dlp/02-create-new-service-account.png)

4. Name your new Google Redactor service account.

    ![Name your service account](/static/collaborative/dlp/03-create-service-account.png)

5. Open the "Select a role" menu, search for "DLP User" and select that role to
   grant your account access to the redactor service.

    ![Open select a role menu](/static/collaborative/dlp/04a-open-select-a-role-menu.png)

    ![Grant DLP User role](/static/collaborative/dlp/04b-grant-dlp-user-role.png)

6. Select "Create Key" and, in the right tab that opens, select a JSON key and
   click "Create". Save the credentials file it gives you. Finally, click the
   "Done" button below the newly created keys list.

    ![Click create key](/static/collaborative/dlp/05a-click-create-key.png)

    ![Save JSON credentials](/static/collaborative/dlp/05b-save-json-credentials.png)

    ![Click done](/static/collaborative/dlp/06-select-done.png)

7. Go to the [Google Cloud API screen for Google DLP](https://console.cloud.google.com/apis/library/dlp.googleapis.com).
   Click "Enable". Cloud DLP requires you set up a billing account with Google.
   If you haven't done this, you will be asked to go through the account
   wizard. At the end, you will be directed back to this screen, where you
   can click "Enable" again. Note that Google has a
   [free tier](https://cloud.google.com/dlp/pricing) and that you
   can use your free credits towards the service.

    ![Enable cloud DLP](/static/collaborative/dlp/07-enable-cloud-dlp.png)

    ![Enable billing, if you haven't](/static/collaborative/dlp/08-enable-billing.png)

8. Upload the credentials file to the collaborative system. You are now
   ready to select fields for redaction, by clicking the checkbox on the import
   and refine screen.

    ![Upload credentials file](/static/collaborative/dlp/09-upload-credentials.png)
