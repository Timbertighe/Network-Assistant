"""
Connects to the Microsoft Graph API, and interacts with MS-Teams chats

Sends messages to Teams chats. These can be one-on-one or groups
Subscribes to resources (chats) to get notified of new messages
Graph API uses OAuth2 authentication, which is used in the azureauth module
A valid bearer token is needed for API calls

Modules:
    3rd Party: Requests, json, datetime, termcolor, threading
    Custom: config

Classes:

    ChatSubscribe
        Maintain subscriptions to resources

Functions

    check_token()
        Check there is a valid bearer token, and return it
    send_chat()
        Send a message to Teams
    notification_refresh()
        Refresh resource subscriptions

Exceptions:

    None

Misc Variables:

    None

Limitations:
    There is a limit to the API calls made to Graph before throttling occurs
        (https://learn.microsoft.com/en-us/graph/throttling)
    Only one public/private key-pair supported for encrypted chats

Author:
    Luke Robertson - April 2023
"""


import requests
from config import GRAPH, TEAMS
import json
from datetime import datetime, timedelta
import termcolor
import threading


# Check teams token is available
def check_token():
    '''
    Confirms that we are authenticated with Graph API
    Reads the token from the token file, and returns it

        Parameters:
            None

        Raises:
            Exception
                If the token file can't be opened

        Returns:
            full_token : str
                The full token, as given to us from Graph API
            False : Boolean
                Returned if there was a problem
    '''

    # Try to open the token file, where the bearer token is stored
    # Exception if the file cannot be opened
    try:
        with open(GRAPH['token_file']) as f:
            data = str(f.read())

    except Exception as err:
        print(termcolor.colored(
            f"Error '{err}' while trying to read from the token file",
            "red"
        ))
        return False

    # Load the full token from the file
    # This includes the bearer token and other information (eg, refresh token)
    full_token = json.loads(str(data))

    # Check that we have a token
    if full_token == '':
        print(termcolor.colored(
            "The token in the token file is empty",
            "red"
        ))
        return False

    # If all is good, return the full token
    return full_token


# Send a messages to a teams chat
def send_chat(message, chat_msg_id):
    '''
    takes a message, and sends it to a teams chat
    Requires that a bearer token has already been allocated,
    and saved in the token file

        Parameters:
            message : str
                An HTML formatted string that is sent to Teams
            chat_msg_id : str
                The chat ID to send the message to

        Raises:
            Exception
                If there was an error connecting to the API

        Returns:
            chat_id : str
                An ID returned from Graph that represents this message
            False : Boolean
                Returned if there was a problem
    '''

    # Make sure authentication is complete first
    full_token = check_token()

    # Setup standard REST details for the API call
    headers = {
        "Content-Type": "application/json",
        "Authorization": full_token['access_token']
    }
    endpoint = GRAPH['base_url'] + 'chats'

    body = {
        "body": {
            "contentType": "html",
            "content": message
        }
    }

    # API Call
    try:
        response = requests.post(
            f"{endpoint}/{chat_msg_id}/messages", json=body, headers=headers
        )
    except Exception as err:
        print(termcolor.colored(
            "Error connecting to the API to POST a message",
            "red"
        ))
        print(termcolor.colored(
            err,
            "red"
        ))
        return False

    # Check that we got a valid response
    match response.status_code:
        # HTTP 200 or 201 is a good response
        case 200 | 201:
            chat_id = json.loads(response.content)
            return chat_id

        # All other response codes are bad
        case _:
            print(termcolor.colored(
                f"Received {response.status_code} code when sending to teams",
                "red"
            ))
            return False


# Refresh class based subscription
def notification_refresh():
    '''
    Subscribes for notifications to a chats. This can be all chats or a list.
    The 'sub_all' option in the global config file determines this bahaviour.
    Schedules a thread to refresh this before they expire

            Parameters:
                None

            Returns:
                None
    '''

    # Check if we're subscribing to all chats
    if TEAMS['sub_all']:
        USER_ID = TEAMS['user_id']
        resource = f'/users/{USER_ID}/chats/getAllMessages'
        subscription = ChatSubscribe(resource)
        subscription.start()

    # Or, are we subscribing to a list of chats
    else:
        for chat in TEAMS['approved_ids']:
            resource = f'/chats/{chat}/messages'
            subscription = ChatSubscribe(resource)
            subscription.start()

    # Schedule a time to refresh these subscriptions
    print(termcolor.colored('starting subscription refresh thread', "green"))
    start_time = threading.Timer(3300, notification_refresh)
    start_time.start()


# Subscription Class
class ChatSubscribe(threading.Thread):
    """Subscribe to Teams chat IDs to get notified of new chats

    Threaded for better performance

    Attributes
    ----------
    threading.Thread
        Inherited thread class, enabling each instance to be threaded

    Methods
    -------
    token()
        Gets the Graph API token
    public_key()
        Retrieves our public key
    get_sub()
        Check if this is an active subscription
    new_sub()
        Create a new subscription
    refresh_sub()
        Refresh an existing subscription
    expiry_time()
        Get an expiry time for a subscription
    """

    def __init__(self, resource):
        """Constructs the class

        Sets up threading for class functions
        Sets up API details for the subscriptions

        Parameters
        ----------
        resource : str
            The Graph API resource to subscribe to

        Raises
        ------
        None

        Returns
        -------
        None
        """

        threading.Thread.__init__(self)

        # Setup standard REST details for the API call
        self.resource = resource
        self.endpoint = GRAPH['base_url']
        full_token = self.token()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": full_token['access_token']
        }

    def run(self):
        """Provides threading support for this class

        This overrides the inherited run() function in the Thread class
        Calls the methods used to set up the class when its instantiated
        (1) Gets the public key
        (2) Check if there is already a subscription
        (3) Refresh or create a new subscription

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

        # Get the public key
        self.pkey = self.public_key()

        # Check if there's already a subscription to the resource
        sub_id = self.get_sub()
        if sub_id:
            # Refresh this subscription
            self.refresh_sub(sub_id)
        else:
            # Create a new subscription
            self.new_sub()

    def token(self):
        """Gets the Graph API token

        Parameters
        ----------
        None

        Raises
        ------
        Exception
            If the token can't be found, or is empty

        Returns
        -------
        full_token : str
            The entire API token, as returned by Graph API
        """

        # Open the token file, and retrieve the token
        try:
            with open(GRAPH['token_file']) as f:
                data = str(f.read())
        except Exception as err:
            raise Exception(f"Could not open the token file: {err}")

        full_token = json.loads(str(data))

        # Check that we have a token
        if full_token == '':
            raise Exception("Token was empty")

        return full_token

    def public_key(self):
        """Reads the public key that is sent to Graph API

        Parameters
        ----------
        None

        Raises
        ------
        Exception
            When the key can't be read (eg, the file is missing)

        Returns
        -------
        pkey : str
            The public key in PEM format
        """

        try:
            with open(TEAMS['public_key'], 'r') as file:
                pkey = file.read()
        except Exception as err:
            raise Exception(f"Could not read the public key: {err}")

        # Strip back to raw keys
        pkey = pkey.replace("-----BEGIN CERTIFICATE-----\n", "")
        pkey = pkey.replace("\n-----END CERTIFICATE-----\n", "")

        return pkey

    def get_sub(self):
        """Check if this is already an active subscription

        Parameters
        ----------
        None

        Raises
        ------
        Exception
            If a list of subscriptions couldn't be obtained from Graph API
            If invalid information was returned from Graph API

        Returns
        -------
        sub_id : string
            The ID of the subscription, if found
        False : Boolean
            If there is no active subscription
        """

        # Get a list of active subscriptions
        try:
            response = requests.get(
                f"{self.endpoint}/subscriptions",
                headers=self.headers
            )

        except Exception as err:
            raise Exception(f"Could not get Teams subscription list: {err}")

        # Check if valid data was returned
        # The API returns a list of active subscriptions under the 'value' key
        # This key should be here whether there are active subscriptions or not
        # If it's not here, then the API call failed
        try:
            sub_list = json.loads(response.content)['value']
        except Exception:
            print(json.loads(response.content))
            raise Exception("Could not get the subscription list from Graph")

        # Check if we already have a subscription to this resource
        # Loop through the active subscriptions until we find a match, or fail
        for sub in sub_list:
            # Check if this entry has our chat ID in it
            # If it does, there is already an active subscription for this ID
            if self.resource == sub['resource']:
                print(termcolor.colored(
                    "Already subscribed for change notifications",
                    "green"
                ))

                print(termcolor.colored(
                    f"Resource: {sub['resource']}\n \
                        Expiry: {sub['expirationDateTime']}\n \
                        ID: {sub['id']}",
                    "green"
                ))

                return sub['id']

        # If our chat ID was not in the subscription list, return False
        return False

    def new_sub(self):
        """Subscribe to a chat ID

        Parameters
        ----------
        None

        Raises
        ------
        Exception
            If we could not access the API
            If the API returned invalid data

        Returns
        -------
        sub_id['resource'] : str
            The resource that has been subscribed to
        """

        # The HTTP body to POST to the API
        body = {
            'resource': self.resource,
            'notificationUrl': GRAPH['chat_url'],
            'changeType': 'created',
            'expirationDateTime': self.expiry_time(),
            'encryptionCertificate': self.pkey,
            'encryptionCertificateId': GRAPH['key_id'],
            'includeResourceData': 'true'
        }

        # API Call
        try:
            response = requests.post(
                f"{self.endpoint}/subscriptions",
                json=body,
                headers=self.headers
            )
        except Exception as err:
            raise Exception(f"Error accessing the API: {err}")

        # Check the response is valid
        sub_id = json.loads(response.content)
        if 'error' in sub_id:
            raise Exception(
                f"Error subscribing to chat: {sub_id['error']['message']}"
            )

        # Subscription was successful
        else:
            print(termcolor.colored(
                f"Subscribed to Teams chat: {sub_id['resource']}\n \
                Expiry: {sub_id['expirationDateTime']}",
                "green"
            ))
            return sub_id['resource']

    def refresh_sub(self, sub_id):
        """Refresh an existing subscription

        Parameters
        ----------
        sub_id : string
            The ID of the subscription to be renewed

        Raises
        ------
        Exception
            If the API PATCH was unsuccessful

        Returns
        -------
        None
        """

        # The HTTP body that we will POST to the API
        body = {
            'expirationDateTime': self.expiry_time()
        }

        # Send a PATCH to the API
        try:
            response = requests.patch(
                f"{self.endpoint}subscriptions/{sub_id}",
                json=body,
                headers=self.headers
            )
        except Exception as err:
            raise Exception(f"Failed to update the subscription: {err}")

        # Check if the refresh was successful
        # If successful, the 'resource' key will be present in the API response
        result = response.json()

        try:
            print(termcolor.colored(
                f"Subscription Refresh: {result['resource']}\n \
                    New Expiry: {result['expirationDateTime']}\n \
                    ID: {result['id']}",
                "green"
            ))

        except Exception:
            print(termcolor.colored(
                f"Raw message: {result}",
                "cyan"
            ))

    def expiry_time(self):
        """Get an expiry time (now + 1 hour); This is passed to the API

        Parameters
        ----------
        None

        Raises
        ------
        none

        Returns
        -------
        time : str
            The expiry time for the new/refreshed subscription
        """

        time = str(datetime.utcnow() + timedelta(hours=1))
        return time.replace(" ", "T") + 'Z'
