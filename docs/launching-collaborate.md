# Launching Collaborate

### **Using Heroku and Google Cloud**

Important: Using a service like Google Cloud and Heroku requires some technical knowledge, and while the service has a free tier, you may incur charges when using it. You’ll be responsible for paying for, maintaining and backing up your own Collaborate instance. ProPublica will not have access to it \(or even know that it exists\). Shutting your instance down may cause you to lose data. You should make sure you understand how to use this or any cloud service before relying on it.

### **Using Your Own Server**

If you set up Collaborate on your own server, you'll need your developer to make a small addition in order for data to update dynamically from Google Sheets and Screendoor.

[Here is an example cron line that developers can use](https://github.com/propublica/django-collaborative/blob/master/deploy/cron/refresh_data_sources). It assumes Collaborate is installed at `/opt/collaborative/app` and python virtual env at `/opt/collaborative/venv`. Developers should add the file to `/etc/crontab`.  


