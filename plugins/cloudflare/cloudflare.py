"""
Receives webhooks from CloudFlare
Authenticated webhook authenticity
Sends alerts on Teams when required

Usage:
    TBA

Restrictions:
    TBA

To Do:
    TBA

Author:
    Luke Robertson - March 2023
"""

from core import teamschat
from core import plugin
import termcolor
from dateutil.parser import parse
from tzlocal import get_localzone
from pytz import timezone


# Location of the config file
LOCATION = 'plugins\\cloudflare\\config.yaml'


class CloudFlareHandler(plugin.PluginTemplate):
    def __init__(self):
        super().__init__(LOCATION)
        self.table = ""

    # Handle a webhook that has been sent to us
    def handle_event(self, raw_response, src):
        alert = raw_response['data']

        # Reformat the timestamp to make it nicer
        if 'timestamp' in alert:
            timestamp = parse(alert['timestamp'])
            timestamp = timestamp.astimezone(timezone(str(get_localzone())))
            timestamp = timestamp.strftime("%H:%M:%S")
        else:
            timestamp = 'no timestamp'

        # Put together a dictionary of useful information
        # This uses try/except, as some alerts uses different fields
        try:
            event = {
                'type': raw_response['alert_type'],
                'time': timestamp,
                'pool': alert['pool_name'],
                'name': alert['origin_name'],
                'health': alert['new_health'],
                'reason': alert['origin_failure_reason'],
                'service': alert['origin_name'],
                'src_ip': src,
            }

            # Create the main message, with colour highlighting
            message = f"<b><span style=\"color:Yellow\">{event['type']} \
                </span></b> on <b><span style=\"color:Orange\"> \
                {event['pool']} </span></b> at {event['time']}"

        # If the expected fields didn't exist, send the raw message
        except Exception as err:
            event = {
                'text': alert,
                'src_ip': src,
                'health': '',
                'service': '',
            }
            print(f"Cloudflare plugin error: {err}")
            message = f"Cloudflare event: {event['text']}"

        # Create the health message with colour highlighting
        print(event)
        if event['health'] == 'Healthy':
            health = f"Current status for <b><span style=\"color:Orange\"> \
                {event['service']}</span></b> is  \
                <b><span style=\"color:Lime\">{event['health']}</span></b>"

        else:
            health = f"Current status for <b><span style=\"color:Orange\"> \
                {event['service']}</span></b> is  \
                <b><span style=\"color:Red\">{event['health']}</span></b>"

        # Log to terminal
        print(termcolor.colored(f"raw message: {raw_response}", "yellow"))

        # Send the main message
        teamschat.send_chat(
            message,
            self.config['config']['chat_id']
        )

        # Send the health status
        if event['health'] != '':
            teamschat.send_chat(
                health,
                self.config['config']['chat_id']
            )

    # Authenticate the valididity of a webhook
    def authenticate(self, request, plugin):
        local_secret = plugin['handler'].webhook_secret
        sender_secret = request.headers[self.auth_header]

        if local_secret == sender_secret:
            return True
        else:
            return False
