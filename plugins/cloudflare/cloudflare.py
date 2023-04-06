"""
CloudFlare plugin

Receives webhooks from CloudFlare
Confirms webhook authenticity
Sends alerts on Teams when required

Modules:
    3rd Party: termcolor, dateutil, tzlocal, pytz
    Custom: teamschat, plugin

Classes:

    CloudFlareHandler
        Handle webhooks from Cloudflare
        Generate messages for Teams

Functions

    None

Exceptions:

    None

Misc Variables:

    LOCATION : str
        The location of the config file

Limitations/Requirements:
    No SQL logging at this time

Author:
    Luke Robertson - April 2023
"""


import termcolor
from dateutil.parser import parse
from tzlocal import get_localzone
from pytz import timezone

from core import teamschat
from core import plugin


# Location of the config file
LOCATION = 'plugins\\cloudflare\\config.yaml'


class CloudFlareHandler(plugin.PluginTemplate):
    """The main class of the CloudFlare plugin

    Handles webhooks as they arrive

    Attributes
    ----------
    None

    Methods
    -------
    timestamp()
        Extract the timestamp from the webhook
        Return it in a simpler format

    handle_event()
        The main plugin handler
        This processes an incoming webhook, and sends messages to users

    fields()
        Extract useful fields from the webhook

    authenticate()
        Authenticate the webhook
    """

    def __init__(self):
        """Constructs the class

        Loads the configuration file
        Sets the table to '', as there is no SQL yet

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        """

        super().__init__(LOCATION)
        self.table = ""

    def timestamp(self, json):
        """Reformat the timestamp to make it nicer

        The timestamp field in the webhook can vary, depending on the alert
        Extracts the timestamp from the webhook
        Converts to a datetime object
        Converts to the local timezone (original is in UTC)
        Simplifies the time format

        Parameters
        ----------
        json : json data
            The webhook (or part of it) that contains the timestamp

        Raises
        ------
        None

        Returns
        -------
        timestamp : str
            The simplified timestamp
        """

        # Reformat the timestamp to make it nicer
        # This field varies depending on the webhook
        if 'timestamp' in json:
            timestamp = parse(json['timestamp'])
            timestamp = timestamp.astimezone(timezone(str(get_localzone())))
            timestamp = timestamp.strftime("%H:%M:%S")

        if 'time' in json:
            timestamp = parse(json['timestamp'])
            timestamp = timestamp.astimezone(timezone(str(get_localzone())))
            timestamp = timestamp.strftime("%H:%M:%S")

        else:
            timestamp = 'no timestamp'

        return timestamp

    def fields(self, json):
        """Extract fields from the webhook

                Parameters
        ----------
        json : json data
            The webhook (or part of it) that contains the fields we need

        Raises
        ------
        None

        Returns
        -------
        fields : dict
            A dictionary of fields we can use
        """

        # Build a simple dictionary of fields
        #   Contains empty values by default to avoid KeyErrors
        fields = {
            'type': '',
            'time': '',
            'src_ip': '',
            'pool': '',
            'service': '',
            'health': '',
            'reason': ''
        }

        # Add more fields if they are available
        #   Not all webhooks have all fields
        #   Some webhooks use different field names
        if 'pool' in json:
            fields['pool'] = json['pool_name']

        if 'origin_name' in json:
            fields['service'] = json['origin_name']
        elif 'name' in json:
            fields['service'] = json['name']

        if 'new_health' in json:
            fields['health'] = json['new_health']
        elif 'status' in json:
            fields['health'] = json['status']

        if 'origin_failure_reason' in json:
            fields['reason'] = json['origin_failure_reason']
        elif 'status' in json:
            fields['reason'] = json['reason']

        return fields

    def handle_event(self, raw_response, src):
        """Handle a webhook that has been sent to us

        Takes a webhook, and extracts useful fields
        If some expected fields aren't there, send a default message
        Build messages to send to Teams

        Parameters
        ----------
        raw_response : requests object
            The raw webhook
        src : str
            The IP address that sent the webhook

        Raises
        ------
        Exception
            If there were problems adding fields to the dict

        Returns
        -------
        None
        """

        # Log to terminal
        print(termcolor.colored(f"raw message: {raw_response}", "yellow"))

        # Focus on the important part of the webhook
        alert = raw_response['data']

        # Reformat the timestamp to make it nicer
        timestamp = self.timestamp(alert)

        # Extract fields from the webhook
        fields = self.fields(alert)

        try:
            # Add a few fields of our own
            fields['type'] = raw_response['alert_type'],
            fields['time'] = timestamp,
            fields['src_ip'] = src

        # If there's a problem extracting fields
        except Exception:
            fields['text'] = alert
            message = f"Cloudflare event: {fields['text']}"

        # Build a message for Teams
        else:
            message = f"<b><span style=\"color:Yellow\">{fields['type']} \
                </span></b> on <b><span style=\"color:Orange\"> \
                {fields['pool']} </span></b> at {fields['time']}"

        # Send the main message
        teamschat.send_chat(
            message,
            self.config['config']['chat_id']
        )

        # Create the health message, if there is anything to share
        if fields['health'] != '':
            if fields['health'] == 'Healthy':
                health = \
                    f"Current status for \
                    <b><span style=\"color:Orange\"> \
                    {fields['service']}</span></b> is  \
                    <b><span style=\"color:Lime\"> \
                    {fields['health']}</span></b>"

            else:
                health = \
                    f"Current status for \
                    <b><span style=\"color:Orange\"> \
                    {fields['service']}</span></b> is  \
                    <b><span style=\"color:Red\"> \
                    {fields['health']}</span></b>"

            # Send the health status
            teamschat.send_chat(
                health,
                self.config['config']['chat_id']
            )

    def authenticate(self, request, plugin):
        """Authenticate a webhook

        Checks that the webhook has been sent from a reliable source
        Checks that the correct header exists in the webhook
        Compares the password to the one we have in our config
        CloudFlare sends the passwords in plain text

        Parameters
        ----------
        request : requests object
            The raw webhook, including headers
        plugin : list
            The list of plugin configuration

        Raises
        ------
        None

        Returns
        -------
        True : Boolean
            If the webhook is authenticated
        False : Boolean
            If authentication failed
        """

        # Get the secret we know
        local_secret = plugin['handler'].webhook_secret

        # Get the secret sent in the webhook
        sender_secret = request.headers[self.auth_header]

        # Compare them
        if local_secret == sender_secret:
            return True
        else:
            return False
