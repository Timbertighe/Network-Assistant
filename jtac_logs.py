"""
Connects to a Junos device and generate support files
    RSI, log collation
Uploads the files to an FTP server

Usage:
    TBA

Authentication:
    Supports username and password for login to NETCONF over SSH
    Junos supports RSA keys, but this script currently does not

Restrictions:
    Requires JunosPyEZ to be installed
    Requres a username/password to connect
    Requires NetConf to be enabled on the target device

To Do:
    Move the FTP host to a config file

Author:
    Luke Robertson - March 2023
"""

import datetime
import termcolor
from plugins.junos import netconf
import jnpr.junos.exception
from core import teamschat
from core import crypto
from config import plugin_list
import threading


# Get logs from a junos device
def get_logs(chat_id, **kwargs):
    if 'device' in kwargs:
        teamschat.send_chat(
            f"I'll get the logs for {kwargs['device']}. Give me a few minutes",
            chat_id
        )
        thread = threading.Thread(
            target=get_rsi,
            args=(kwargs['device'], chat_id,)
        )
        thread.start()

    else:
        teamschat.send_chat(
            "Sorry. you'll need to give me a device name",
            chat_id
        )


# Collect the RSI, and logs, then upload to FTP
def get_rsi(host, chat_id):

    # Get FTP details
    ftp_server = ''
    ftp_dir = ''

    for plugin in plugin_list:
        if 'Junos' in plugin['name']:
            ftp_server = plugin['handler'].ftp_server
            ftp_dir = plugin['handler'].ftp_dir

    if ftp_server == '' or ftp_dir == '':
        print(termcolor.colored("Could not get FTP server details", "red"))
        teamschat.send_chat(
            "Sorry, I couldn't get the FTP server details from the plugin",
        )
        return

    # Get date for filenames
    date = str(datetime.date.today())

    # Get passwords required to connect to the FTP server
    ftp_secret = crypto.pw_decrypt(dev_type='server', device=ftp_server)
    if not ftp_secret:
        teamschat.send_chat(
            f"I couldn't get a password to connect to {ftp_server}",
            chat_id
        )
        return

    # Build the FTP URL
    ftp_user = ftp_secret['user']
    ftp_pass = ftp_secret['password']
    ftp_url = f'ftp://{ftp_user}:{ftp_pass}@{ftp_server}/{ftp_dir}/'

    # Get passwords required to connect to the device
    secret = crypto.pw_decrypt(dev_type='junos', device=host)
    if not secret:
        teamschat.send_chat(
            f"I couldn't get a password to connect to {host}",
            chat_id
        )
        return

    # Connect to the Junos device; Should return a connection object
    # If the returned object is not right, handle the error
    dev = netconf.junos_connect(host, secret['user'], secret['password'])
    if not isinstance(dev, jnpr.junos.device.Device):
        netconf.error_handler(err=dev, dev=dev, chat_id=chat_id)
        return False

    # Get the hostname, as it is configured on the device
    hostname = dev.facts['hostname']

    # Request the device to generate the support file
    rsi_filename = f'/var/log/RSI-Support-{hostname}-{date}.txt'
    print(termcolor.colored(f'RSI filename: {rsi_filename}', 'green'))
    result = netconf.send_shell(
        f'request support information | save {rsi_filename}',
        dev
    )
    if not isinstance(result, str):
        netconf.error_handler(err=result, dev=dev, chat_id=chat_id)
        return False
    teamschat.send_chat(
        f"I've created the RSI<br> \
            <span style=\"color:Yellow\">{rsi_filename}</span>",
        chat_id
    )

    # Request the device to create an archive of the logs
    log_filename = f'/var/tmp/Support-{hostname}-{date}.tgz'
    print(termcolor.colored(f'Archive filename: {log_filename}', 'green'))
    result = netconf.send_shell(
        f'file archive compress source /var/log/* destination {log_filename}',
        dev
    )
    if not isinstance(result, str):
        netconf.error_handler(err=result, dev=dev, chat_id=chat_id)
        return False
    print(termcolor.colored(f"Result is: {result}", "red"))
    teamschat.send_chat(
        f"I've created the log archive<br> \
            <span style=\"color:Yellow\">{log_filename}</span>",
        chat_id
    )

    # Upload the archive to an FTP server
    ftp_file = f'ftp://{ftp_server}/{ftp_dir}/Support-{hostname}-{date}.tgz'

    print(termcolor.colored(f'Uploading to {ftp_url}', 'green'))
    teamschat.send_chat(
        "I'm uploading the archive now...",
        chat_id
    )

    result = netconf.send_shell(
        f'file copy /var/tmp/Support-{hostname}-{date}.tgz {ftp_url}/',
        dev
    )
    if 'not' in result.lower():
        netconf.error_handler(err=result, dev=dev, chat_id=chat_id)
        return False

    # Gracefully close the device
    teamschat.send_chat(
        f"All done! The logs are here:<br> \
            <span style=\"color:Yellow\">{ftp_file}</span>",
        chat_id
    )
    dev.close()
