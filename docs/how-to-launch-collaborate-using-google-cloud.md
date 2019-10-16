# How to Launch Collaborate \(Using Google Cloud\)

The Google Cloud Run button launches your own instance of Collaborate using the Google Cloud environment. Using Google Cloud requires you to [setup a Google Project](https://console.cloud.google.com/projectselector2/home/dashboard), enable [Google Cloud billing](https://cloud.google.com/billing/docs/how-to/modify-project) and enable the [Cloud Run API](https://github.com/propublica/django-collaborative/blob/master/gc-run). [Full setup instructions on using Google Cloud are here](https://cloud.google.com/run/docs/quickstarts/build-and-deploy).

Once you've deployed your Cloud Run instance, you can manage your running instance from the [Google Developers Console](https://console.cloud.google.com/run).

### **Google Cloud Run Setup**

You'll have to go through three steps before you can begin the setup process for Collaborate. 

1. First, you'll need to set up a Google project. [Click here](https://console.cloud.google.com/projectselector2/home/dashboard?_ga=2.109895747.-794541741.1567796729&pli=1) and log into your Google account.

At the top of the page, click "Select a project."

![](https://lh3.googleusercontent.com/_HarOAsrMMSLedRdpA6iD3iixVCUu1n7Qcy8--JVgU0_tlxeh28X4_OU7u7dK7ZlT23JrUUd9kPjSLZzGy3SkBLOx2hT_-EvaNQ7uwK6SGXtO3to-FkdABBT9yEmjPkp6kxst2y6)

2. Then, click "New project."

![](https://lh6.googleusercontent.com/L-4Pc7q9KwJ-dcv-PEaVBRWj2Tpfnijh6MFgCqNyiBWxDaxy_at2CpF3jQq3lCiN7roTQr3hnC_h4tSpiNN-JmAWlXxlJlkqAf4ZgJ-Rph11kWE44bG3WGhTJZJ7LeKW5j6G5Mbl)

3. Enter a project name, and click "Create."

![](https://lh3.googleusercontent.com/WFsLYwhHnUTWJC4GMFSGxDZZVg65kMUVRvzADzwkEroXlGGEVohh-BxvqXZLTo_JhjFqDZ1bK0PmWbpn_hVZh0Y1v2kk__p7IaL6bQHlBCetDTGJ67d_MuRZwPNSqLReDt6PhwCy)

4. Next, you'll need to enable billing on your Google account. Click on "Billing" in the left-hand column.

If you don't have a billing account, you'll be directed to set one up. If you already have a billing account, [follow these directions.](https://cloud.google.com/billing/docs/how-to/modify-project)

5. Select "Link a billing account."

![](https://lh3.googleusercontent.com/7J17181d_SUQ2u4p03Bdw7gU3ITrrgQVQVbn576Xp4qMu6Yl7ln7zU_rH-GaQGNFgraQItLcd5BiZArPFSkQdcqQ81tz9VsE_HPP1_ugx893gUOr959mWP3DUts8AfrDpk8tidj4)

6. Then click "Create Billing Account."

![](https://lh5.googleusercontent.com/-SEe6urzIrFAQbiAm4sKQaEyXygcC4T5qpoeIi7WBAFWJpO_vezo89botD2Jph_omoiflE2HFQIJ8mZsz_at69LoCwe-lFLZx3MQ78_e-uSwytjPlQwD_MLcy2zxudF5OCXbzPwH)

7. Then follow the prompt and enter your information. Google will give you credit for a free trial.

![](https://lh5.googleusercontent.com/Ym0WcTXG8CAggk7BsfzX3SthLUGU0BPj398CYyH3aV6ydG_qcDBGOUsDeq0ZcRjbq-jH2VA7_ZWIBDkcqY2mq_T5konFYJmA33VZMMyK6xql7Q-HvUJAJze-0zouRMP9MB-w9fff)

Once you've entered your information, you'll get this confirmation.

![](https://lh3.googleusercontent.com/3GxgUOALAUQiCBMpOpIZeapPDhrlqUtbqYqiaMAIn1h9LQn-ABIeqhKfPwzgeZAC0RGWdq4QZfInbVs_XeIuvDGG5v3La1wCAGac6a2gLviGGbYJRI0DCtEAF-Fpe1nhlhs2oEK6)

8. Finally, you'll need to enable the Cloud Run API. [Click here](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com,run.googleapis.com&redirect=https://console.cloud.google.com&_ga=2.144368627.-794541741.1567796729) and choose your project from the dropdown menu. Click "Continue."

![](https://lh6.googleusercontent.com/JnlJRAkW1Eo_VW0JoH9RfFO-701n7jRzVdmuS2pqoFUrFS3cdFaEetjsqhA9LST5YA6YAglOr8nOP35twGKNgeys28G6hflhuk5QWUVXeZztMN1lbSGSMmMa_PPex4k1uZbSa8Hz)

You'll see this confirmation.  


![](https://lh4.googleusercontent.com/EzRz07qqS9384hPMS_q9eJtXdiUBJVk9qGHa1ttzO_dJsWW0T2esbb6xTzhdVHFQIOB2JNU4f53x_eU-bNazuS0A54l1X3AryEKmtfiCLw5uYKn-Iu1JIgDrkaIoWXe_IEDOa9Ak)

### **Deploy Collaborate**

After you've followed these three steps, you'll be ready to deploy your instance of Collaborate. 

1. [Click here](https://console.cloud.google.com/cloudshell/editor?shellonly=true&cloudshell_image=gcr.io/cloudrun/button&cloudshell_git_repo=https://github.com/propublica/django-collaborative.git&cloudshell_git_branch=cloud-run&cloudshell_working_dir=deploy/google-cloud) to start. Make sure you're logged into the Google account you used for the setup process.

2. Check the end-user agreement box \(making sure you understand what you’re committing to\) and click "Start Cloud Shell."

![](https://lh6.googleusercontent.com/ec3k0of-zrvCUifkj6TI_aHIeElRZ9dZu9spucAWC5YWmq9z8qCu81mtmhc6TdczSDY2_WoWhtFjuh7x9zUlCA6t6Gcnqo7YQ5tWTndR3NGq07PQeHD7R6zwLXVD7BEiNAz6Kkfj)

3. The following message will appear. Click "Proceed."

![](https://lh4.googleusercontent.com/rRY5qNH6DEBH8JtZPjhUynY6d4RKEwTMnNoNLeg1kLsTVVDdBup1Ee4ZoGL3EWFMQx6qgpQQm4WFx1-O8nim5jTPyitP_Ch-EnN0_sSypB5edBWA1m6SGfEKi1YCFxCwzv-6nMhh)

4. The page will start running a script.

![](https://lh4.googleusercontent.com/f9pavGplGfiT6svc5IH_FyYbEl0XVQO1mK86nKHaUxG9h0FehfnjsdcO9d7t7C1dgW-KzHV958sThh3QGXcKlDdeZl5sF-5aNC8atNaYWXTnFDHuKl2xbocqP2LxrggETlfb_LAd)

It will then display the following message:

Value of COLLAB\_ADMIN\_USERNAME environment variable \(Default admin account username.\)

Enter the admin username you'd like to use for Collaborate, and hit enter.

![](https://lh3.googleusercontent.com/TfwSyKVIB_6tTj2ALiPIoVJ_h0l856BbTmTRQKNoOCdBCL9psWjwG6gFzjLtXlb0wvYt59RMvuXD8EwftIki1HZxgfp0ZV635tUGj8ohRbvS0GdC9p4LCQZV3pTBN38w-1QfY_08)

5. Then enter your email address, and hit enter. Type in a temporary password, and hit enter.

![](https://lh5.googleusercontent.com/lA3i3LVKEW9_LeC5-RJfdFD7Qzl207DcZk-TPsdQLlTlYeRy8mskaTj0lBYlsGcnjSpNoLiFV-fPo9ux7qiXpBc6HhtGqbbZVcWoDoukitInNiky9_lFi5g37aVRkPr3PFynXTiB)

6. Next, it will ask ask you to select the Google Cloud project. Use the arrow keys to select the project you created during the setup process, and hit "Enter."

![](https://lh6.googleusercontent.com/ylzwV7E1GTpccGMRAmRzn34E0-FCstsIl-RrbMX7CvXuGH4SuuO8yE0dm7QBJWJn_NKhilFT8E9-ZF-MUUDYpBWwfin-as40d0HsJToDiw-W7Uh6Il6NgsQKHxIse9ZWObPM4kV3)

7. Then use the arrow keys to select your time zone, and hit "Enter."

![](https://lh4.googleusercontent.com/_zUs8jm79ovY8O2Fx6YYLJr_cPEiLyBWxkMq_z2QnVxRN2rVjc6Waa2-79WzjfcWBS4rvK-973igS7tDGWZVy4abHS0c_imzmsbCEEchzXfX38sArs7lRqroPPZ3yiIQ7aybWf55)

8. Then a script will begin to run. It make take a few minutes.

![](https://lh4.googleusercontent.com/J8kgtc8DJrRDXLR-PIczRWgela5Vp0BhFR2IcJdZMgM9x1iYxI-LC-MELYV5HvHMpqqly3yQIPeYtiD0qFyD24NKQ1wXpMusqLjmZ5elimiAvOHxe6hJlsZsVYfHsu1MC3_JKti8)

![](https://lh5.googleusercontent.com/iDoM1QUS513jbcdeTI7yesTz82NyESs0Vuxv7ULxIqntzWeke0yHJXn89b2DbJ6xI3RmjnH0ixkAnWg3S-U9yfK3HW9rh90lLCUfZz4FV-J9KfgUwL64kAQZA7OldKNY7DJYzEKc)

9. Once the process is completed, you'll get a link marked in green. Click the link.

![](https://lh6.googleusercontent.com/j02fymFeVvwz8ZKIyAxPqQmrLb-nWRudfg8TP5aQi-nkSnEIpu3IK5Iw5g0QCuK3i5ZkzGo7LuvY8TSga1scCBwiT9A7VgeOHnDbtKNVP77Wji7NtBqc0h2duLSCy9u3nLQ0vOYj)

Now you can use the login information you put in to get started!

![](https://lh4.googleusercontent.com/aoocTxu4L76L249frWulPewjI_KFrKJYL7Hx0tu7XLm4JeeNC2aCG5MDecPnBWVPhr-VgBnkhjHft1JvAqBF_0wnovsHsC31xlNy0_CUkFd4kYKNFVSw3PM37r7tUcjDrs5T-aib)

  


