#!/usr/bin/env python3

import logging
import requests
from bs4 import BeautifulSoup
import re
import glob
from datetime import datetime
import configparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the logger level to the lowest level
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Configure the console handler for INFO level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Configure the file handler for DEBUG level (with file appending)
file_handler = logging.FileHandler(
    'check_perm_processing_times.log', mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def send_email(new_date, priority_date):

    try:
        # Read email configuration
        config = configparser.ConfigParser()
        config.read('config.ini')

        sender_email = config.get('EmailCredentials', 'sender_email')
        sender_password = config.get('EmailCredentials', 'sender_password')
        receiver_emails = config.get(
            'EmailCredentials', 'receiver_emails').split(', ')

        logger.debug(
            f'sender_email: {sender_email}, sender_password: {"*"*len(sender_password)}, receiver_emails: {receiver_emails}')

    except Exception as e:
        logger.error(f"Failed to load email configurations: {e}")

    try:
        subject = 'PERM Processing Times Update'
        body = f'PERM Processing Times have been updated.\n\nLast Update: {new_date}\nPriority Date for Analyst Review: {priority_date}'

        for receiver_email in receiver_emails:
            logger.debug(f'Sending email to "{receiver_email}"...')

            msg = MIMEMultipart()
            msg.attach(MIMEText(body, 'plain'))
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = receiver_email

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())

            logger.info(f'Email sent successfully to "{receiver_email}".')
            return 0

    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return 1


def dump_content_to_file(content):

    # Create a filename with a timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    new_filename = f'webpage_content_{timestamp}.txt'

    # Write content to the new file
    with open(new_filename, 'w', encoding='utf-8') as file:
        file.write(content)

    logger.debug(f"Content has been dumped to {new_filename}")


def read_last_file_content():

    # Find the latest file in the series
    files = glob.glob('webpage_content_*.txt')
    if not files:
        logger.info("No webpage_content_*.txt files found.")
        return None

    # Sort files by filename (timestamp)
    files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]), reverse=True)

    # Choose the latest file
    chosen_file = files[0]

    # Read content from the chosen file
    with open(chosen_file, 'r', encoding='utf-8') as file:
        content = file.read()

    logger.debug(f"Content read from {chosen_file}")
    return content


def fetch_webpage_content():

    url = 'https://flag.dol.gov/processingtimes'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Fetch webpage content and save to file
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        logger.error(
            f'Failed to fetch webpage content, Return Code {response.status_code}')
        return None


def get_processing_dates(content):

    if content is None:
        return None

    try:
        # Get the relevant information
        soup = BeautifulSoup(content, 'html.parser')

        # Get the update data
        caption_tag = soup.find('caption').find(
            'strong', string='PERM Processing Times')
        update_date = re.search(
            r'\d{1,2}/\d{1,2}/\d{4}', caption_tag.find_next('em').get_text()).group(0)
        logger.debug(f'Got update_date as "{update_date}".')

        # Get the priority date
        priority_date_tag = soup.find(
            'td', string='Analyst Review').find_next('td')
        priority_date = priority_date_tag.get_text()
        logger.debug(f'Got priority_date as "{priority_date}".')

        return {'update_date': update_date, 'priority_date': priority_date}

    except Exception as e:
        logger.error(
            f'An unexpected error occurred while getting processing dates: {e}')
        return None


def check_perm_processing_times():

    # Fetch the webpage content
    webpage_content = fetch_webpage_content()

    # Get the processing dates from the webpage content
    webpage_dates = get_processing_dates(webpage_content)
    if webpage_dates is None:
        logger.error('Failed to get processing dates from the webpage.')
        exit(1)
    else:
        logger.debug(f'Obtained webpage_dates as {webpage_dates}')

    # Read the latest local file
    local_content = read_last_file_content()

    # Get the processing dates from the local file
    local_dates = get_processing_dates(local_content)
    if local_dates is None:
        logger.info('Processing dates not obtained from local file.')
    else:
        logger.debug(f'Obtained local_dates as {local_dates}')

    # Check if the processing dates have been updated
    webpage_update_date = webpage_dates.get('update_date')
    webpage_priority_date = webpage_dates.get('priority_date')
    local_update_date = local_dates.get(
        'update_date') if local_dates is not None else 'n/a'
    local_priority_date = local_dates.get(
        'priority_date') if local_dates is not None else 'n/a'

    if webpage_update_date != local_update_date:
        logger.info(
            f'Processing dates have been updated as of "{webpage_update_date}".')
        logger.info(
            f'The latest Priority Date for the Analyst Review process is "{webpage_priority_date}" as of "{webpage_update_date}" (was "{local_priority_date}" as of "{local_update_date}").')

        # Send email to receivers
        rcode = send_email(webpage_update_date, webpage_priority_date)
        if rcode:
            exit(0)
    else:
        logger.info(
            f'Processing dates haven\'t been updated since "{webpage_update_date}".')
        logger.info(
            f'The latest Priority Date for the Analyst Review process is "{webpage_priority_date}" as of "{webpage_update_date}".')

    # Dump the webpage content to local storage
    dump_content_to_file(webpage_content)

    exit(0)


if __name__ == "__main__":
    check_perm_processing_times()
