"""
Plugin template class

Modules:
    3rd Party: yaml, socket, struct, termcolor
    Custom: core/sql, core/hash

Classes:

    PluginTemplate
        Template class for plugins

Functions

    None

Exceptions:

    None

Misc Variables:

    None

Limitations/Requirements:
    None

Author:
    Luke Robertson - April 2023
"""


import yaml
import socket
import struct
import termcolor

from core import sql, hash


class PluginTemplate():
    """A tmeplate class for plugins

    Plugins inherit this class to use its functions
    Any methods here can be superseeded by the plugin class

    Attributes
    ----------
    None

    Methods
    -------
    ip2integer()
        Convert an IP address to an integer
        This is so it can be written to SQL

    refresh()
        Refresh the plugins config file

    sql_write()
        Write entries to an SQL table

    authenticate()
        Authenticate a webhook
    """

    # Initialise the class and read the YAML file
    def __init__(self, location):
        """Constructs the class

        Setup default variables and load the config file
        Setup webhook authentication

        Parameters
        ----------
        location : str
            Location of the plugin's config file

        Raises
        ------
        Exception
            If there were problems loading the config file

        Exception
            If an auth header is not used by this plugin

        Returns
        -------
        None
        """

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
        """Converts an IP address to a long integer

        Parameters
        ----------
        ip : str
            The IP address to convert

        Raises
        ------
        None

        Returns
        -------
         : str
            The string in a long integer format
        """

        ip = ip.split(",")[0]
        packedIP = socket.inet_aton(ip)
        return struct.unpack("!L", packedIP)[0]

    # Refresh the plugin's config file
    def refresh(self):
        """Reread the config file for changes

        Parameters
        ----------
        none

        Raises
        ------
        Exception
            If the config file could not be opened

        Returns
        -------
         : bool
            True if there was no error
            False if there was an error
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

        return True

    # Write to an SQL database
    def sql_write(self, database, fields):
        """Write information to a database

        Parameters
        ----------
        database : str
            The database table to write to

        fields : dict
            Fields to write to the table

        Raises
        ------
        Exception
            If the SQL class couldn't be created

        Exception
            If the fields couldn't be written to SQL

        Returns
        -------
         : bool
            True if there was no error
            False if there was an error
        """

        # Create an SQL connection object
        try:
            sql_conn = sql.Sql()
        except Exception as err:
            print(termcolor.colored(
                f"An error occurred instantiating the SQL object: {err}",
                "red"
            ))
            return False

        try:
            sql_conn.add(database, fields)
        except Exception as err:
            print(termcolor.colored(
                f"An error occurred writing to SQL: {err}",
                "red"
            ))
            return False

        return True

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
