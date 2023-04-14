"""
Connects to a Junos device and generate support files
    RSI, log collation
Uploads the files to an FTP server
Supports username and password for login to NETCONF over SSH
Junos supports RSA keys, but this script currently does not

Modules:
    3rd Party: JunosPyEz (junos-eznc), datetime, termcolor, threading
    Internal: core/teamschat, core/crypto, config.plugin_list

Classes:

    None

Functions

    get_logs()
        Extract details from the users request
    get_rsi()
        Collect logs from the device, and upload to FTP

Exceptions:

    None

Misc Variables:

    None

Limitations:
    Requires NetConf to be enabled on the target device
    Uses username/password for authentication

Author:
    Luke Robertson - April 2023
"""


import datetime
import termcolor
import threading
from plugins.junos import netconf
import jnpr.junos.exception

from core import teamschat
from core import crypto
from config import plugin_list


def get_logs(chat_id, **kwargs):
    '''
    Extracts details from the users request, such as device name

        Parameters:
            chat_id : str
                The chat ID to report back to
            kwargs : list
                Additional details, such as device names

        Returns:
            None
    '''

    # Look through kwargs to find a device name
    #   This should have an NLP entity of 'DEVICE' assigned
    device = ''
    if 'ents' in kwargs:
        for ent in kwargs['ents']:
            if ent['label'] == "DEVICE":
                device = ent['ent']
                break

    # If we have a valid device name:
    if device != '':
        teamschat.send_chat(
            f"I'll get the logs for {device}. Give me a few minutes",
            chat_id
        )

        # Start a thread calling get_rsi()
        #   This is the part that does the work on the device
        thread = threading.Thread(
            target=get_rsi,
            args=(device, chat_id,)
        )
        thread.start()

    # If there's no valid device name, we can't proceed
    else:
        teamschat.send_chat(
            "Sorry. you'll need to give me a device name",
            chat_id
        )


def get_ftp(chat_id):
    '''
    Get FTP details to upload the logs

    (1) Get FTP server information
    (2) Get FTP username/password

    Parameters:
        chat_id : str
            The chat ID to report back to

    Returns:
        : dict
            The full FTP path (including username/password)
            A simplified path (no username/password)
        False : bool
            If there was a problem
    '''

    # Collect FTP server and directory information
    #   This comes from the config file
    ftp_server = ''
    ftp_dir = ''

    for plugin in plugin_list:
        if 'Junos' in plugin['name']:
            ftp_server = plugin['handler'].ftp_server
            ftp_dir = plugin['handler'].ftp_dir

    # Handle errors if this can't be found
    if ftp_server == '' or ftp_dir == '':
        print(termcolor.colored("Could not get FTP server details", "red"))
        teamschat.send_chat(
            "Sorry, I couldn't get the FTP server details from the plugin",
        )
        return False

    # Get passwords required to connect to the FTP server
    ftp_secret = crypto.pw_decrypt(dev_type='server', device=ftp_server)

    # If that didn't work, print an error and return
    if not ftp_secret:
        teamschat.send_chat(
            f"I couldn't get a password to connect to {ftp_server}",
            chat_id
        )
        return False

    # Build the FTP URL
    ftp_user = ftp_secret['user']
    ftp_pass = ftp_secret['password']
    ftp_url = f'ftp://{ftp_user}:{ftp_pass}@{ftp_server}/{ftp_dir}/'
    redacted = f'ftp://{ftp_server}/{ftp_dir}/'

    return {'full_path': ftp_url, 'redacted_path': redacted}


def get_rsi(host, chat_id):
    '''
    Connect to a junos device and get the logs

    (1) Generate the RSI
    (2) Compress logs to an archive
    (3) Upload to an FTP server

        Parameters:
            host : str
                The hostname to connect to
            chat_id : str
                The chat ID to report back to

        Returns:
            True : bool
                If successful
            False : bool
                If there was a problem
    '''

    # Get passwords required to connect to the device
    secret = crypto.pw_decrypt(dev_type='junos', device=host)
    if not secret:
        teamschat.send_chat(
            f"I couldn't get a password to connect to {host}",
            chat_id
        )
        return False

    # Connect to the Junos device; Should return a connection object
    # If the returned object is not right, handle the error
    dev = netconf.junos_connect(host, secret['user'], secret['password'])
    if not isinstance(dev, jnpr.junos.device.Device):
        netconf.error_handler(err=dev, dev=dev, chat_id=chat_id)
        return False

    # Get extra details for filenames
    hostname = dev.facts['hostname']
    date = str(datetime.date.today())
    rsi_filename = f'/var/log/RSI-Support-{hostname}-{date}.txt'
    print(termcolor.colored(f'RSI filename: {rsi_filename}', 'green'))

    # Generate the RSI
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

    # Create an archive of logs
    log_filename = f'/var/tmp/Support-{hostname}-{date}.tgz'
    print(termcolor.colored(f'Archive filename: {log_filename}', 'green'))

    result = netconf.send_shell(
        f'file archive compress source /var/log/* destination {log_filename}',
        dev
    )

    if not isinstance(result, str):
        netconf.error_handler(err=result, dev=dev, chat_id=chat_id)
        return False

    print(termcolor.colored(f"Device responded: {result}", "green"))

    teamschat.send_chat(
        f"I've created the log archive<br> \
            <span style=\"color:Yellow\">{log_filename}</span>",
        chat_id
    )

    # Upload the archive to an FTP server
    ftp = get_ftp(chat_id)

    # Check for a valid result, and build filenames
    if ftp:
        ftp_url = ftp['full_path']
        ftp_server = ftp['redacted_path']
        ftp_file = f'{ftp_server}Support-{hostname}-{date}.tgz'

    else:
        return False

    # Inform the user
    print(termcolor.colored(f'Uploading to {ftp_url}', 'green'))
    teamschat.send_chat(
        "I'm uploading the archive now...",
        chat_id
    )

    # Copy the archive to FTP
    #   Sometimes the junos device mangles this string,
    #   so it should be manually encoded as ASCII
    result = netconf.send_shell(
        (
            f'file copy /var/tmp/Support-{hostname}-{date}.tgz {ftp_url}'
        ).encode('ascii'),
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

    return True
