# Check PERM Processing Times

## Description

check_perm_processing_times.py

This script monitors the PERM processing times on the U.S. Department of Labor website. It compares the latest
update date with the information stored locally. If there is an update, it sends an email notification to specified
recipients. Finally it updates the local storage with the new webpage content for the future reference.

## Basic Usage

```basj
# Install Python Modules
pip3 install bs4 --user

# Go into the script folder
cd /path/to/check_perm_processing_times

# Configure email credentials
vi config.ini

# Run the script
./check_perm_processing_times.py

# Check the debug log
less check_perm_processing_times.log
```

Note: See "Configuring Email Credentials" below for more information.

## Run with Scheduler

In Linux, you can use the cron service to schedule tasks to run at specified intervals. Here's how you can set up a cron job to run a script every day at 8:00 am using the command line:

1. Open your crontab file for editing:

```bash
crontab -e
```

If this is the first time you're editing the crontab, you may be prompted to choose an editor.

2. Add the following line to run your script every day at 8:00 am:
```bash
0 8 * * * cd /path/to/check_perm_processing_times/ && ./check_perm_processing_times.py
```

Replace `/path/to/check_perm_processing_times/` with the actual path to your script.

Here's the breakdown of the time specification:

`0 8 * * *`: This represents the cron schedule in the format *minute hour day month day_of_week*. In this case, meaning minute 0 of hour 8, every day, every month, every day of the week.

## Configuring Email Credentials

Here's an example of the `config.ini` file:

```ini
[EmailCredentials]
sender_email = your_email@gmail.com
sender_password = your_email_password
receiver_emails = receiver_email1@gmail.com, receiver_email2@gmail.com
```

For enhanced flexibility and security, it's recommended to use a Google APP Password. Follow the steps outlined in this Google Support article to enable it for your account: https://support.google.com/accounts/answer/185833

When dealing with multiple email receivers, it's important to note the following:
- Email addresses separated by `, ` (comma followed by a space) will receive individual notifications, with each recipient being unaware of others.
- Email addresses separated by `,` (comma without a space) will be notified in the same email, allowing recipients to see each other's email addresses.

Example:

```ini
receiver_emails = user1@gmail.com,user2@gmail.com, user3@gmail.com
```

In this case, user1 and user2 will receive an email sent to both of them, and they can see each other's email addresses. User3 will receive an email sent only to themselves.
