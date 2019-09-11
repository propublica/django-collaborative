# Technical Users: Letting Users Log in With Their Google Account

In order to allow users to sign in with their Google account, you need to request access from Google to do this. Specifically, you need something called OAuth2 keys from Google. To get these keys, follow these steps:

1. Go to the Google Developer's Console.
2. Create a new project \(or select an existing one\).
3. On the left, select "Credentials."
4. Select the "OAuth consent screen."
5. Give your application a name and support email. Click "Save" at the bottom.
6. Go back to the "Credentials" tab. Click "Create credentials" &gt; "OAuth client ID"
7. Select "Web application." This will expose more options.
8. Under "Authorized JavaScript origins" enter: http://\[HOSTNAME\]

   Under "Authorized redirect URIs" enter: http://\[HOSTNAME\]/complete/google-oauth2 

   Important: Replace \[HOSTNAME\] with the URL of your Collaborate system.

9. Click "Save."

This will bring up a prompt containing the Google OAuth2 Key and Secret. Copy each to the input boxes.

Optionally, you can select one or more domains to whitelist. This will let users whose email addresses are within the whitelisted domain sign in, without needing to first create their user account.

If you didn't whitelist any domains, you'll need to pre-create each user that you want to be able sign in via Google Sign-In. This can be done from the users section of the admin dashboard.

