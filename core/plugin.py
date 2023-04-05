"""
Provides class templates for plugins

Usage:
    import this module into a plugins file
    When creating a class for the plugin,
        inherit the class here to get some predefined functionality
        eg:
            class MyPlugin(plugin.PluginTemplate):
                def __init__(self):
                    super().__init__(LOCATION)

Authentication:
    N/A

Restrictions:
    TBA

To Do:
    None

Author:
    Luke Robertson - March 2023
"""

import yaml
import socket
import struct
import termcolor
from core import sql, hash


class PluginTemplate():
    # Initialise the class and read the YAML file
    def __init__(self, location):
        # Default variables
        self.config = {}
        self.alert_levels = {}
        self.location = location
        self.phrase_list = False
        self.entities = False

        # Read the YAML file
        with open(location) as config:
            try:
                self.config = yaml.load(config, Loader=yaml.FullLoader)

            # Handle problems with YAML syntax
            except yaml.YAMLError as err:
                print('Error parsing config file, exiting')
                print('Check the YAML formatting at \
                    https://yaml-online-parser.appspot.com/')
                print(err)
                return False

        # Setup webhook authentication
        self.auth_header = self.config['config']['auth_header']
        self.webhook_secret = self.config['config']['webhook_secret']
        try:
            self.auth_header_secret = \
                self.config['config']['auth_header_secret']
        except Exception as e:
            print(f"{e} not used in this plugin")

    # Convert an IPv4 address to an integer
    def ip2integer(self, ip):
        """
        Convert an IP string to long integer
        """
        ip = ip.split(",")[0]
        # print(termcolor.colored(f"DEBUG: IP Address: {ip}", "red"))
        packedIP = socket.inet_aton(ip)
        return struct.unpack("!L", packedIP)[0]

    # Refresh the plugin's config file
    def refresh(self):
        """
        Re-read the config file as needed
        """
        with open(self.location) as config:
            try:
                self.config = yaml.load(config, Loader=yaml.FullLoader)

            # Handle problems with YAML syntax
            except yaml.YAMLError as err:
                print(termcolor.colored(
                    'Error parsing config file, exiting',
                    "red"))
                print('Check the YAML formatting at \
                    https://yaml-online-parser.appspot.com/')
                print(err)
                return False

    # Write to an SQL database
    def sql_write(self, database, fields):
        """
        Write fields to the SQL server
        """
        sql_conn = sql.Sql()
        sql_conn.add(database, fields)

    # Check webhook authentication
    def authenticate(self, request, plugin):
        # Check if there is an authentication header
        if plugin['handler'].auth_header != '':
            # Check that this webhook has come from a legitimate resource
            auth_result = hash.auth_message(
                header=plugin['handler'].auth_header,
                secret=plugin['handler'].webhook_secret,
                webhook=request
            )

            if auth_result == 'fail':
                print(termcolor.colored(
                    "Received a webhook with a bad secret",
                    "red"))
                return False

            elif auth_result == 'unauthenticated':
                print(termcolor.colored(
                    "Unauthenticated webhook received",
                    "yellow"))
                return False

        # If there is no authentication header
        else:
            print(termcolor.colored('Unauthenticated webhook', "yellow"))

        return True
