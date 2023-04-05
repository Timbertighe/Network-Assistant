"""
Connects to Microsoft Identity Services and authenticates an app and a user

Usage:
    Import the azureauth module in your application
    Run azureauth.client_auth() to get a client code
        This will require a user to authenticate
        Take the resulting code (in the returned URL)
            and put it in the 'client_code' variable
    Run azureauth.get_token() to redeem a valid code for a token
        This will return a dictionary, containing:
            token - The bearer token
            expiry - The validity time in seconds
            user - The user this token has been generated for

Authentication:
    OAuth 2.0
    Requires a user to log in and authorize permissions on their account

Restrictions:
    Requires msal module to be installed (pip install msal)
    Requires an application to be registered in Identity Services
        Needs an App ID, Tenant ID, and Client Secret
        Needs a Callback URL configured (localhost is ok)

To Do:
    Retry token refresh if it fails

Author:
    Luke Robertson - October 2022
"""


import webbrowser
from msal import ConfidentialClientApplication
import threading
from config import TEAMS
from config import plugin_list
import termcolor


class AzureAuth:
    def __init__(self):
        # Application info and required permissions
        APPLICATION_ID = TEAMS['app_id']
        CLIENT_SECRET = TEAMS['secret']
        TENANT = TEAMS['tenant']
        self.SCOPES = ['ChatMessage.Send',
                       'Chat.ReadWrite',
                       'Chat.ReadBasic',
                       'Chat.Read']

        # The login URL for client authentication
        login_url = 'https://login.microsoftonline.com/' + TENANT

        self.app = ConfidentialClientApplication(
            client_id=APPLICATION_ID,
            client_credential=CLIENT_SECRET,
            authority=login_url
        )

    # This generates the URL that user would use to authenticate and
    # authorize the app based on the requested permissions
    # We use the webbrowser module to pop up a request for the user
    def client_auth(self):
        '''Generate the URL that a user would use to authenticate
        Opens a webbrowser to get them to accept'''
        request_url = self.app.get_authorization_request_url(
            scopes=self.SCOPES,
            login_hint=TEAMS['user']
        )

        webbrowser.open(request_url, new=True)

    # This gets a token based on a previously retrieved client code
    # Return a dictionary with the token, expiry, and authenticated user
    def get_token(self, client_code):
        '''Take the client code, and convert it to a token'''
        # Get the access token
        access_token = self.app.acquire_token_by_authorization_code(
            code=client_code,
            scopes=self.SCOPES
        )

        self.save_token(access_token)
        self.schedule_refresh(
            access_token['expires_in'],
            access_token['refresh_token']
        )

    # Refresh the token to Graph API
    def refresh_token(self, token):
        '''Takes a token and refreshes it'''
        # Using the MSAL library
        access_token = self.app.acquire_token_by_refresh_token(
            refresh_token=token,
            scopes=self.SCOPES
        )

        if 'error' in access_token:
            print(termcolor.colored(
                'An error occurred while trying to refresh the token',
                "red"))
            print(access_token['error_description'])

        else:
            print(termcolor.colored(
                'Graph API token refresh successful',
                "green"))
            self.save_token(access_token)
            self.schedule_refresh(access_token['expires_in'],
                                  access_token['refresh_token'])

        # Take this opportunity to refresh the config for each plugin
        for plugin in plugin_list:
            print(termcolor.colored(
                f"Refreshing plugin config: {plugin}",
                "yellow"))
            plugin['handler'].refresh()

    # Save the token to a file
    def save_token(self, access_token):
        '''Saves the given access token to token.txt'''
        # Change single quotes to double quotes (valid JSON)
        temp = str(access_token).replace("'", "\"")

        # Write the token information to a file (overwrite previous contents)
        with open("token.txt", "w") as file:
            file.write(temp)

    # Schedule a token refresh, 5 minutes before the current one expires
    def schedule_refresh(self, expiry, token):
        '''Schedules a refresh of the token
        takes the expiry time in seconds, and the refresh token'''
        print(termcolor.colored('starting token refresh thread', "green"))
        start_time = threading.Timer(
            (expiry - 300),
            self.refresh_token,
            [token]
        )
        start_time.start()
