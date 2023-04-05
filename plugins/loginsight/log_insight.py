"""
Provides supporting functions to the Log Insight webhooks
Parses incoming webhooks, filters, and sends to teams

Usage:
    import 'log_insight' into the application

Restrictions:
    Needs access to the 'teamschat' module

To Do:
    TBA

Author:
    Luke Robertson - November 2022
"""


# import yaml
from core import teamschat
from core import plugin
from datetime import datetime
import termcolor


# Location of the config file
LOCATION = 'plugins\\loginsight\\config.yaml'


class LogInsight(plugin.PluginTemplate):
    # Initialise the class from the inherited class
    def __init__(self):
        super().__init__(LOCATION)
        self.table = self.config['config']['sql_table']

    # Handle the webhook
    def handle_event(self, raw_response, src):
        '''Handle webhooks when the are sent'''
        # Add the sending IP to the event
        raw_response['source'] = src

        # Cleanup the message
        event = self.parse_message(raw_response)
        message = event
        message = f"<span style=\"color:yellow\"><b>{event['hostname']} \
            </span></b> had a <span style=\"color:orange\"><b> \
            {message['alert']} </span></b>event.<br> {event['description']} \
            <br><span style=\"color:lime\">{event['recommendation']}</span> \
            <br><a href={message['url']}>See more logs here</a>"

        # Log the message, and send to teams
        self.log(message, raw_response)

    # Parse the message
    def parse_message(self, event):
        message = {}
        message['source'] = event['source']
        message['alert'] = event['alert_name']
        message['time'] = event['timestamp']
        try:
            message['hostname'] = event['messages'][0]['fields'][0]['content']
        except IndexError:
            message['hostname'] = 'Log Insight'

        try:
            message['description'] = event['messages'][0]['text']
        except IndexError:
            message['description'] = ''
        except KeyError:
            message['description'] = ''

        if event['recommendation'] == 'null':
            message['recommendation'] = 'No recommended actions'
        else:
            message['recommendation'] = event['recommendation']

        message['url'] = event['url']
        return message

    # Log to Teams and SQL
    def log(self, message, event):
        date = datetime.now().date()
        time = datetime.now().time().strftime("%H:%M:%S")

        chat_id = teamschat.send_chat(
            message,
            self.config['config']['chat_id']
        )['id']
        print(termcolor.colored(f"Log Insight event: {event}", "yellow"))

        try:
            description = event['messages'][0]['text'].replace("'", "")
        except KeyError:
            description = ''
        except IndexError:
            description = ''

        try:
            hostname = event['messages'][0]['fields'][0]['content']
        except IndexError:
            hostname = 'No hostname'

        fields = {
            'device': f"'{hostname}'",
            'event': f"'{event['source']}'",
            'description': f"'{description}'",
            'logdate': f"'{date}'",
            'logtime': f"'{time}'",
            'source': f"{self.ip2integer(event['source'])}",
            'message': f"'{chat_id}'"
        }

        self.sql_write(
            database=self.config['config']['sql_table'],
            fields=fields
        )

    # Check webhook authentication
    # This overrides the default implementation from the template
    # WARNING: Log Insight sends the username and password in clear text
    def authenticate(self, request, plugin):
        # Check if there is an authentication header
        if request.headers[plugin['handler'].auth_header] != 'undefined':
            username = self.config['config']['webhook_user']
            password = self.config['config']['webhook_secret']
            sent_username = \
                request.headers[plugin['handler'].auth_header]
            sent_password = \
                request.headers[plugin['handler'].auth_header_secret]

            if (username == sent_username) and (password == sent_password):
                return True
            else:
                return False

        # If there is no authentication header
        else:
            print(termcolor.colored(
                'Log Insight: Unauthenticated webhook',
                "yellow"
            ))
            return True
