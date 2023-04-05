"""
Connects to an SMTP server and sends an email

Usage:
    Set the SERVER and PORT variables as necessary

Authentication:
    No SMTP level authentication supported here
    The mail server will need to allow the IP of the client to relay

Restrictions:
    None

To Do:
    None

Author:
    Luke Robertson - November 2022
"""


import smtplib
from email.mime.text import MIMEText
from config import SMTP


SERVER = SMTP['server']
PORT = SMTP['port']


def send_mail(message):
    '''
    Takes a message as a string
    Sends the message to the smtp server, as defined in config.yaml
    '''

    to = ''
    sender = SMTP['sender']
    receivers = SMTP['receivers']
    for receiver in receivers:
        if to != '':
            to += ", "
        to += receiver

    # Convert the given message to MIME format
    msg = MIMEText(message)

    # Add email details
    msg['Subject'] = 'Test mail - Network Assistant'
    msg['From'] = SMTP['sender']
    msg['To'] = to

    # Send the email
    with smtplib.SMTP(SERVER, PORT) as server:
        server.sendmail(sender, receivers, msg.as_string())
        print("Successfully sent email")
