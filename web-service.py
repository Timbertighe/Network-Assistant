"""
Runs a small web server, using Flask
Listen for announcements from Mist (webhooks)

Usage:
    Add config to the 'config.yaml' file
    Base URL is something like http://localhost:{PORT}
    Test the web server - Browse to /test
    Test the mist webhook - GET /mist
    Send a Mist webhook - POST /mist

Authentication:
    Mist - Not required, as this service passively receives webhooks

Restrictions:
    Requires Flask module to be installed (pip install flask)
    Requires pyyaml module to be installed (pip install pyyaml)
    Requires termcolor to be installed (pip install termcolor)
    Requires a public IP and FW rules (for webhooks to send to)
        TCP port is set in the WEB_PORT variable
    No support for HTTPS; Use SSL offloading (eg, nginx, F5, NetScaler)
    A config file, config.yaml, must exist in the same directory as this script
    NOTE: When using Flask debug mode, the authentication window opens twice;
        Apparently a known Flask issue

To Do:
    Find an alternative to saving the token to a file
        Can't get variables to work between Flask routes
        My current solution is to save to disk, and read later

Author:
    Luke Robertson - March 2023
"""


from core import azureauth
from core import crypto
from core import teamschat
from core import schedule_tasks
from nlp import nlp

from config import GLOBAL, GRAPH, TEAMS
from config import PLUGINS, plugin_list

from flask import Flask, request, Response
from flask_apscheduler import APScheduler
import importlib
import termcolor
from urllib.parse import urlparse, parse_qs
import threading


# Load plugins
def load_plugins(plugin_list):
    for plugin in PLUGINS:
        print(termcolor.colored(
            f"Loading plugin: {PLUGINS[plugin]['name']}",
            "green"))

        try:
            module = importlib.import_module(PLUGINS[plugin]['module'])
        except Exception as e:
            print(termcolor.colored(
                f"Error loading the {PLUGINS[plugin]['name']} plugin",
                "red"))
            print(termcolor.colored(
                f"{e}; error while loading the module",
                "red"
            ))
            continue
        print(module)

        try:
            handler = eval('module.' + PLUGINS[plugin]['class'])()
        except Exception as e:
            print(termcolor.colored(
                f"Error loading the {PLUGINS[plugin]['name']} plugin",
                "red"
            ))
            print(termcolor.colored(
                f"{e} error while loading the class",
                "red"
            ))
            continue

        plugin_entry = {
            'name': PLUGINS[plugin]['name'],
            'route': PLUGINS[plugin]['route'],
            'handler': handler,
        }
        plugin_list.append(plugin_entry)


# Import configuration details
WEB_PORT = GLOBAL['web_port']
APPROVED_LIST = TEAMS['approved_ids']


# Initialise a Flask app
app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
schedule_tasks.sched_tasks(scheduler)


# Setup the handler objects
load_plugins(plugin_list)
print(termcolor.colored(f"Plugins: {plugin_list}", "cyan"))


# Setup NLP object
chat_nlp = nlp.ChatNlp()


# Authenticate with Microsoft (for teams)
print('Calling client_auth')
azure = azureauth.AzureAuth()
azure.client_auth()


# Subscribe to the chat(s), so we can see when people send messages
# The callback URL needs to be ready for this to work,
#   so this is run as a separate thread
thread = threading.Thread(target=teamschat.notification_refresh)
thread.start()


# Test URL - Used to confirm the service is running
@app.route("/test")
def test():
    message = "Web Service is running on port " + str(WEB_PORT)
    return message


# Callback URL; Used for MS Identity authentication
# When a user authenticates, a code is returned here
@app.route("/callback", methods=['GET'])
def callback():
    client_code = (request.args['code'])
    if client_code == '':
        return ('There has been a problem retrieving the client code')
    else:
        # Get the token from Microsoft
        azure.get_token(client_code)

        return ('Thankyou for authenticating, this window can be closed')


# Listen for webhooks
@app.route('/<handler>', methods=['POST'])
def webhook_handler(handler):
    # Get the source IP - Use X-Forwarded-For header if it's available
    if 'X-Forwarded-For' in request.headers:
        source_ip = request.headers['X-Forwarded-For']
    else:
        source_ip = request.remote_addr

    # Get the plugin handler module to decide what to do with the request
    # The class must include a 'handle_event' and 'authenticate' method
    for plugin in plugin_list:
        # Confirm that a route exists for this plugin
        if handler == plugin['route']:
            # Authenticate the webhook
            if plugin['handler'].authenticate(request=request, plugin=plugin):
                # If authenticated, send this to the handler
                plugin['handler'].handle_event(raw_response=request.json,
                                               src=source_ip)

            # Return a positive response
            return ('Webhook received')

    return ('Invalid path')


# GraphAPI - Listens for change notifications
# This is when new messages are sent to the chatbot
@app.route("/chat", methods=['POST'])
def chat():
    # Check if this is a callback when subscribing
    url = request.url
    if 'validationToken' in url:
        parsed = urlparse(url)
        validation_string = parse_qs(parsed.query)['validationToken'][0]
        return Response(validation_string, status=200, mimetype='text/plain')

    # Or, is this a webhook
    else:
        # Extract the values we need from the webhook
        body_value = request.json['value']
        encrypted_session_key = body_value[0]['encryptedContent']['dataKey']
        signature = body_value[0]['encryptedContent']['dataSignature']
        data = body_value[0]['encryptedContent']['data']

        # Decrypt the symmetric key
        decrypted_symmetric_key = crypto.rsa_decrypt(encrypted_session_key)
        if not decrypted_symmetric_key:
            print(termcolor.colored("Could not decrypt message", "red"))
            return ('received')

        # Validate the signature - Tamper prevention
        if crypto.validate(decrypted_symmetric_key, data, signature):
            # Decrypt the message
            decrypted_payload = crypto.aes_decrypt(
                decrypted_symmetric_key,
                data
            )

            # Get key fields from the message
            # Sometimes the API sends a message with no name - we can ignore
            try:
                name = decrypted_payload['from']['user']['displayName']
            except Exception:
                return ('received')

            message = decrypted_payload['body']['content']
            chat_msg_id = decrypted_payload['chatId']

            # If it's the chatbot talking, ignore (no need to talk to itself)
            if name == GLOBAL['chatbot_name']:
                return ('received')

            # Check that this sender is authorized, and parse the message
            if chat_msg_id in APPROVED_LIST:
                chat_nlp.parse(phrase=message, chat_id=chat_msg_id)

            else:
                print(termcolor.colored(
                    f"User {name} is not authorized",
                    "red"
                ))
                teamschat.send_chat(
                    f"User {name} tried to chat, but is unauthorized.<br> \
                    ID: {chat_msg_id}",
                    GRAPH['chat_id']
                )
                teamschat.send_chat(
                    "Sorry, I can't chat to you right now. \
                    You need to be authorized. \
                    An admin has been notified",
                    chat_msg_id
                )

        else:
            print("Validation failed")
            print("Data may have been tampered with")
            return "Error"

        return ('received')


# Start the Flask app
if __name__ == '__main__':
    scheduler.start()
    app.run(debug=GLOBAL['flask_debug'], host='0.0.0.0', port=WEB_PORT)
