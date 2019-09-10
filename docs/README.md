# Collaborate User Manual

Collaborate is an open-source tool that newsrooms can use to enable multiple reporters to share a dataset. It's modeled after the tools ProPublica built for its Electionland and Documenting Hate projects, in which hundreds of reporters shared the same sets of data.

It's designed to help multiple people sift through a large dataset and to add information to each data point. It is not meant to be used for statistical data analysis.

Although it can work with most datasets, Collaborate is built especially well for crowdsourced projects in which the data is pulled from a forms tool like Google Forms or Screendoor. 

It will allow you to assign tips to reporters (or claim them for yourself), add a contact log for getting in touch with tipsters, save information learned about each tip and update each one’s status. It will also allow you to add tags to make it easier to sort through the data.

To learn more about how to carry out collaborative data projects, read our guide.

Collaborate is still in beta, which means we're still fixing bugs. It also means you should be careful to back up your data. If you encounter problems or errors, you can report them here.

The code for Collaborate is available on Github and can be forked and altered to suit your organization’s needs.

Collaborate is being provided as a hopefully useful tool, but it is being provided as is and all users should take necessary precautions, including backing up their data, before using it. ProPublica disclaims any responsibility for its use, makes no warranties about it, and makes no promises to keep it updated in any way.

## How to Launch Collaborate (using Heroku)

1. Click this link to create a new instance of Collaborate in a service called Heroku. 
2. You'll need a Heroku account. Create a new account, or log into an existing one. Make sure you confirm your new account by email. Note that Heroku has free and paid tiers.
3. Under app name, choose a name. If it’s already in use, you'll get a message in red and have to choose another.
4. Scroll down — don't worry about pipeline or add-ons. Enter your email address under COLLAB_ADMIN_EMAIL. Create a password under COLLAB_ADMIN_PASSWORD, which you will use to log into Collaborate. Pick a secure one! Finally, enter a username under COLLAB_ADMIN_USERNAME. You’ll use this later to log into Collaborate. There's a final box labeled DISABLE_COLLECTSTATIC; leave it as is.
5. Click “Deploy app.” The Heroku service will start running a script; wait for it to load. 
6. When the script finishes loading, at the bottom of the page, a message will appear: “Your app was successfully deployed.” Click on “View.”
7. You'll arrive on the app screen. Enter the username and password you just entered on the previous screen in Heroku.

That’s it! You’re now ready to create your first collaborative project. 

Some important things to keep in mind.

1. You’ve created a copy of the Collaborate service that is for your exclusive use. Nobody has access to it but you. Later, we’ll show you how to add other users to your system.
2. You’ve created a website on the live internet. Although it will only accept secure connections from web browsers, it’s up to you to control access and to pick a good password to keep it secure.


## How to Upload Your Data

Collaborate allows you to work with spreadsheets in CSV format and in Google Sheets, and with forms created through Google Forms and Screendoor. 

### To Use a CSV File

Only use this option if your dataset is complete; this is a static file and won't auto-update. Just choose the file and upload it from your computer. It will use the filename that's saved on your computer.

In the “Add a Data Source” section, click on the plus sign to the left of “File Upload (CSV).”

### To Use Google Sheets

Google Sheets should be used if you want to continually add data or you're using Google Forms. Google Sheets can be set to public or private. A public spreadsheet can only be seen by those who have the link. You can use a private sheet if you're working with sensitive data.

### Using a Public Google Spreadsheet

If your spreadsheet doesn’t contain private or sensitive information, you can set it to be publicly viewable. Make sure the link is set to "Anyone with the link can view," which is found in the “Share” menu in Google Sheets. Important: Be sure that your data is in the first tab of the workbook.

Next, you'll need to copy the spreadsheet's URL from the address bar in your browser. Give your project a name in the Data Source Label field, and paste in the URL you copied from your spreadsheet.

### Using Google Forms

If you're using Google Forms, you'll need to go to your Google Form and click the “Responses” tab. Then click on “Create Spreadsheet.” (Read instructions here from Google.)

### Using a Private Google Spreadsheet

Important: Be sure that your data is in the first tab of the workbook.

You'll need to go through a short setup process the first time you add a private sheet. There’s a wizard with these instructions within Collaborate.

If your data contains sensitive information or information you’re not ready to be public, Collaborate does support using private Google Sheets. The process is a little involved but actually very easy.

Importing private Google Sheets for the first time consists of several steps: creating a Google service account that can access Google Sheets, uploading an account credentials file to your version of Collaborate and sharing the sheet with the account email.

#### Creating a Service Account and Credentials File

A service account is a special kind of account you create with which you can later share your spreadsheet in a secure way. It may look like an email address, but it won’t work as one. You only need to create a service account once. Subsequent imports will reuse that account’s credentials, as long as you keep sharing the private spreadsheet with the account.

1. Go to the Google Developer Console and create a new project.
2. From the “Enable APIs and Services” screen, search for "Google Sheets" and click on the "Google Sheets API" box.
3. In the left panel, click the "Credentials" button.
4. On the next page, click "Create Credentials" menu toward the top of the page and select "Service account."
5. In the wizard that loads, give your service account a name. It doesn’t matter what it is. Then click "Create."
6. On the next page, you should see the service account you added. Click the dropdown menu and select the "Viewer" role. Then click "Continue."
7. Toward the bottom of the next page, click "Create Key." A window on the right side of your screen will appear.
8. Select the "JSON" option (should be default) and click "Done." The system will download the file to your computer. Remember where you saved it.
9. On the left-hand tab, click on “Service Accounts.” Copy the email address listed in the "Service Accounts" list.

#### Giving Collaborate the Permission to View Your Sheet
1. Go back to your private Google Sheet and share it with the service account's email address, just as you normally would. 
2. Now go back to Collaborate. Upload the credentials file you saved a few steps ago. Done! All future private sheets can be imported by simply sharing them with the service account email using Google Sheets and checking the "private sheet" checkbox during the Collaborate import.

### Using Screendoor

First, you'll need to find the project ID for your form. You'll find that in Screendoor in your project under Settings > General Settings > Advanced Settings.

Next, you'll need to produce an API key. Ask your Screendoor administrator; it should be a string of letters and numbers.

Input the project ID and give your project a name and paste in the two fields.

## Organizing Your Data
Once you upload the data, you'll see the import screen.

Here, you can refine the columns by the type of data they contain, such as numbers or dates.

You can also choose the order in which the columns appear in the user interface. The first five columns will appear on your main screen, so you can drag and drop the most important columns in the top five slots.

Finally, you can choose which columns are searchable and filterable. You'll most likely want to make everything searchable. Filters let you show only the entries that have one of a limited set of multiple-choice answers. Important: Don’t make a field that allows free-form text or more than 20 possible answers filterable. 

Note: Your choices here are important but not unalterable. If you want to change the column order or these preferences later, you can refresh the data by hitting the “Re-Import” button on the top right of Collaborate’s main screen.

You can also choose to redact personal information from specific columns. You'll have to go through a separate process for that. (See the section below titled “Redacting Data With Cloud Data Loss Prevention.”)

## Adding Other Google Services

After you upload data for the first time, you'll get the option to set up additional Google services, including the setup processes for private sheets, for Google Sign-In and for using Google’s cloud service to redact names and other personal information. 

You can also opt to set these up later by clicking “Continue.”

## Completing the Setup Process

Once your data has been successfully uploaded, you'll be taken to your main screen, and you can access your project under “Data Sources.”

## Using Collaborate

### Adding Metadata

Collaborate is meant to make it easier to coordinate on large datasets. The metadata fields added by Collaborate allow you to leave notes on each entry, keep track of which journalist is working on which data point, set the status of each data point and create a log of contacts on each data point. 

Important: Any time you update the metadata, don't forget to scroll down to the bottom of the page and hit “Save.”

### Status

Status is a field that helps you keep track of what's going on with each tip or data point. You can update this in the list view by selecting the dropdown, or in an individual data point by using the dropdown, scrolling to the bottom of the page and hitting “Save.”

You can filter by the status of all the tips in the list view in the right-hand column.

### Assigned-to 
This helps you track which reporter is working on each data point. You can add these in the list view or while you're in an individual data point.

If you're in an individual data point, be sure to hit “Save” after you make updates.

Each assignee name added will appear in the “Filters” column in the list view so that you can track who is working on which data points.

### Notes
This field exists within individual data points. This allows you to add any information you'd like in a text format. Make sure to hit “Save” when you add to the field.

### Contact Log

For crowdsourced projects, you can keep track of each time a reporter reaches out to the source. Enter the reporter name and select a contact method. Click “Today” for today's date, or select a date by clicking on the calendar icon. Click “Now” for time, or select a time by clicking the clock. Then scroll down and hit “Save.” Each contact will now be saved in a log on that individual entry.

### Creating Tags

In order to organize your data into groups, you can create tags. There are two ways to do this.

On your list view page, you can type in a new or existing tag in the “Tags” box. Select the data points you want to add the tag to using the check boxes and click “Add.” You can do the same to remove them — that is, clicking the “Remove” button. You can also remove tags in list view by clicking the small “X” next to the tag name in the “Tags” column.

You can also add tags in the individual data point. Open an individual data point, and you can type in a tag in the “Tags” field to create a new one or to bring up an existing tag. Tags will also appear as filters on your main screen.

If you need to update or delete a tag, go to the main screen and click on “Tags” under the “Tagging” line. Click on an individual tag to edit it.

You can also filter by tags on the main screen.

### Updating Your Data

If you receive new responses to your crowdsourcing form in Google Forms or Screendoor, or if you enter new records into your Google Sheet, that information will automatically update in Collaborate. The system is set to refresh every 15 minutes. If you'd like to force a refresh, just click the “Re-import” button.

### Exporting Your Data

You can export your data as a spreadsheet. On the top right corner of the page, click the “Export” button. Choose the file format you'd like from the dropdown. Then click “Submit.”

### Redacting Data With Cloud Data Loss Prevention

To have the app automatically redact personally identifiable information (names, phone numbers, email addresses, etc.) upon import from a spreadsheet, you can use the Google Data Loss Prevention, or DLP, service. In order to use this service, you need to create a DLP credentials file and set up a billing account with Google by following the instructions below. Please keep in mind that Google has a free tier and that you can use your free credits toward the service.

Note: This will not remove the information from the source data (e.g., your original Google Sheet). This will only prevent it from being saved to Collaborate's database and shown to your users.

#### Credentials Instructions

1. Go to the Google Developer's Console.
2. Create a new project or select an existing one (if you've already set up Google private sheets, for example).
3. From the dropdown menu on the top left, select "IAM & admin" > "Service accounts."
4. Click "Create Service Account" at the top of the service accounts page.
5. Name your new Google Redactor service account.
6. Open the "Select a role" menu, search for "DLP User" and select that role to grant your account access to the redactor service.
7. Select "Create Key" and, in the right tab that opens, select a JSON key and click "Create." Save the credentials file it gives you. Finally, click the "Done" button below the newly created keys list.
8. Go to the Google Cloud API screen for Google DLP. Click "Enable.” Cloud DLP requires you to set up a billing account with Google. If you haven't done this, you will be asked to go through the account wizard. At the end, you will be directed back to this screen, where you can click "Enable" again. 
9. Once you have those credentials, upload them to Collaborate by clicking on "Configure Google Services" on the main screen. Click on "Google Redaction (Data Loss Prevention)." Scroll down to "Credentials file," upload the file, and click "Continue." You are now ready to select fields for redaction by clicking the “Redact” checkbox on the Import and Refine screen.

You can see Google’s documentation for getting credentials for more technical details.

### Creating Users

You can add multiple users to a dataset. On your main screen, go to Users > Add User under “Authentication and Authorization.” Create a username and enter the user's email address. Enter a temporary password; the person will be asked to change the password when they log in. 

Important: Remember to make the password secure even though it’s temporary, and transmit the password to the user securely. 

Once you have created the new user, you'll be asked to provide more information about them and to give them access permission.

### Adding Users to Projects

You can restrict users' access to specific projects. If you want to give the person access to a specific project, click on “Users” under “Authentication and Authorization.” Select the user you want to edit. Scroll down to “Groups.” Click on the project you want to add, and click the right-hand arrow button. Repeat this for each project. When you're done, scroll to the bottom and click “Save.”

If you have other administrators, you can give them access to everything. You can give them superuser status by checking the superuser status box. Scroll to the bottom and click “Save.”

### Technical Users: Letting Users Log in With Their Google Account 

In order to allow users to sign in with their Google account, you need to request access from Google to do this. Specifically, you need something called OAuth2 keys from Google. To get these keys, follow these steps:

1. Go to the Google Developer's Console.
2. Create a new project (or select an existing one).
3. On the left, select "Credentials."
4. Select the "OAuth consent screen."
5. Give your application a name and support email. Click "Save" at the bottom.
6. Go back to the "Credentials" tab. Click "Create credentials" > "OAuth client ID"
7. Select "Web application." This will expose more options.
8. Under "Authorized JavaScript origins" enter: http://[HOSTNAME]
Under "Authorized redirect URIs" enter: http://[HOSTNAME]/complete/google-oauth2 
Important: Replace [HOSTNAME] with the URL of your Collaborate system.
9. Click "Save."

This will bring up a prompt containing the Google OAuth2 Key and Secret. Copy each to the input boxes.

Optionally, you can select one or more domains to whitelist. This will let users whose email addresses are within the whitelisted domain sign in, without needing to first create their user account.

If you didn't whitelist any domains, you'll need to pre-create each user that you want to be able sign in via Google Sign-In. This can be done from the users section of the admin dashboard.

### Deleting a Project or Entry

To delete a project from Collaborate, navigate to your main screen. In the Data Sources section, click “Delete an Import.” Select the project or projects by clicking the checkboxes. Then click the “Action” box, select “Delete Selected Successful Imports” and click “Go.” A new screen that will appear that says “Are you sure?” Click “Yes, I'm sure.”

To delete a single record, open up the entry. Scroll to the bottom, and click “Delete.” You'll arrive at a screen that says “Are you sure?” Click “Yes, I'm sure.”

### Changing Your Password

To change your password, navigate to the main screen. At the top of the page, you'll see "Change Your Password" next to “View Site.” Make sure to hit “Save” after you change your password.

### Language support

You can upload data in any language. Currently, Collaborate will translate part of the user interface of the tool into Spanish. (Full translation is still in development.) You can toggle the language in the top right of your screen.
