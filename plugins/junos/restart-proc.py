"""
Restart a junos process
This can be done gracefully (SIGTERM) or immediately (SIGKILL)

Usage:
    TBA

Authentication:
    Supports username and password for login to NETCONF over SSH
    Junos supports RSA keys, but this script currently does not

Restrictions:
    Requires JunosPyEZ to be installed
    Requres a username/password to connect
    Requires NETCONF to be enabled on the target device

To Do:
    TBA

Author:
    Luke Robertson - March 2023
"""

from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import RpcError
from lxml import etree

from core import crypto
from core import teamschat
import threading


# Get passwords required to connect to the device
def get_creds(chat_id, device):
    secret = crypto.pw_decrypt(dev_type='junos', device=device)
    if not secret:
        teamschat.send_chat(
            f"I couldn't get a password to connect to {device}",
            chat_id
        )
        return
    return secret


# Restart a process on a device
def restart(device, user, password, process, **kwargs):
    '''
    Restart a process on a device
    Requires device name, username and password, and a process to restart
    Optionally can pass 'immediately=True' to use SIGKILL
    '''
    print(f"Connecting to {device}...")
    if process == 'forwarding':
        print("This will restart the forwarding process")
        print("You will lose access to the device temporarily")
        print("(5+ minutes for small devices)")

    # Connect to the device
    try:
        with Device(host=device, user=user, passwd=password) as dev:
            # Restart the process immediately (SIGKILL)
            if 'immediately' in kwargs and kwargs['immediately'] is True:
                result = dev.rpc.restart_daemon(
                    immediately=True,
                    daemon_name=process,
                )
                print("Restart Initiated (SIGKILL)")

                # When using 'immediately', only a True or False is returned
                if result:
                    print("Restart Complete")
                else:
                    print("There were problems restarting this service")
                    print("Maybe check the system logs")

            # No args means restart gracefully (SIGTERM)
            # If args are invalid, just a regular restart will do
            else:
                result = dev.rpc.restart_daemon(
                    daemon_name=process
                )
                print("Restart Initiated (SIGTERM)")
                print(etree.tostring(result, encoding='unicode'))

    # Handle Connection error
    except ConnectError as err:
        print(f"There has been a connection error: {err}")

    # Handle an RPC error
    except RpcError as err:
        # Special handling for the forwarding process, as it will disconnect us
        if process == 'forwarding':
            print(f"I have been disconnected from {device}")
            print("This is normal when restarting the forwarding process")

        # Handle errors where a process is not running
        elif 'subsystem not running' in str(err):
            print(f"The {process} process cannot be started")
            print("It is not in use on this system")

        # Handle a bad process name
        elif 'invalid daemon' in str(err):
            print(f"The {process} does not exist on this system")
            print("Maybe it's typed incorrectly?")

        # Handle other RPC errors
        else:
            print(f"RPC Error has occurred: {err}")

    # Handle a generic error
    except Exception as err:
        print(f"Error was: {err}")


# Process the users phrase in order to restart a process
def nlp_restart(chat_id, **kwargs):
    # Find one or more device names in the entities
    device_list = []
    if 'ents' in kwargs:
        for ent in kwargs['ents']:
            if ent['label'] == "DEVICE":
                device_list.append(ent['ent'])

    # At the very least, we need one device to reboot
    if len(device_list) == 0:
        print("You need to give me a device name")
        return

    # Get the process to restart
    process = ""
    for ent in kwargs['ents']:
        if ent['label'] == "PROCESS":
            process = ent['ent']
            break

    if len(process) == 0:
        print("I need at least one process to restart")

    # Restart the processes
    for device in device_list:
        secret = get_creds(chat_id=chat_id, device=device)
        if not secret:
            return

        args = {
            'device': device,
            'user': secret['user'],
            'password': secret['password'],
            'process': process,
        }

        # Force restart
        if 'immediate' in kwargs['message']:
            print(f"restarting the {process} process on {device} immediately")

            teamschat.send_chat(
                f"restarting the {process} process on {device} immediately",
                chat_id
            )
            args['immediately'] = True

        # Graceful restart
        else:
            print(f"restarting the {process} process on {device}")

            teamschat.send_chat(
                f"restarting the {process} process on {device}",
                chat_id
            )

        # Run the thread
        thread = threading.Thread(
            target=restart,
            kwargs=args
        )
        thread.start()
