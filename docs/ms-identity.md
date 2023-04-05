# Microsoft Identity Platform and Authentication
MS Teams uses the MS Graph API  
Authentication must first happen with the Identity Platform  

## Overview
    To access teams and send messages, we need to access the MS Graph API  
    There are two parts to this:  
      Authenticating with MS Identity Services  
      Sending messages to the Graph API  
    This doc focuses on authentication  
  
## Authentication
    Graph API uses OAuth 2.0  
    This means we need to authenticate with the identity services API, and get:  
      (1) A client code  
      (2) A bearer token  
    The client code is converted to the bearer token. The token is passed to the Graph API with each request  
  
    The client code is needed, as teams messages are sent as a particular user. The user needs to 'consent' to allowing their account to be used this way  
    A connection to the MS Identity Platform API is made with the MSAL library.  

### Application
    Before authentication, an application needs to be registered in the identity platform. This needs to include a callback URL  
    We have flask listening on /callback for this purpose. Any firewalls in the path need to allow MS to send authentication information to this URL  

### Client Code
    The first step is to send a request for a client code. This requires a list of scopes to be sent. These are the permissions that we need to the user's account  
    This app requires these user permissions:  
      'ChatMessage.Send', 'Chat.ReadWrite', 'Chat.ReadBasic', 'Chat.Read'  
    This app requires these application permissions:
      'Chat.Read.All', 'Chat.ReadWrite.All'
    When the client code is requested, a webbrowser will open with the callback URL inside, as well as the client code  
      If the user has not already consented to the required permissions, they will be asked to do so  
      If they have previously consented, we will just get a message saying the browser can be closed  
    
### Bearer Token
    Once the client code is obtained from the callback, we can use the MSAL library to convert this to a bearer token  
    The response from the API includes details like the token, the valid time, user name, refresh token, and other details  
    This is saved to a file called token.txt. This is so it can be available in any scope from Flask's perspective  
  
### Token Refresh
    Tokens are valid for about one hour. When this is near to expiry, we can refresh it, and get a new token  
    The token refresh timer starts in a separate thread, so it's not blocking any other processes  

## azureauth.py
    Contains the AzureAuth() class
    Create an AzureAuth object, and then call client_auth() to authenticate

### __init__()
    Creates an application with the MSAL library to connect to the identity services API  
    This uses an application ID, client secret, tenant, and scope (permissions)  
  
### client_auth()
    Arguments: None  
    Returns: None  
    Purpose: Connects to the Identity Services API, and requests a client code  
      Opens the web browser for the user to consent  
  
### get_token()
    Arguments: client_code  
      This is the code obtained with client_auth()  
    Returns: None  
    Purpose: Connects to the API and converts a client code into a token (along with other information  
      The token information is saved to a file (token.txt) with save_token()  
      A refresh timer starts with schedule_refresh(), allowing the token to be refreshed before it expires  
    
### refresh_token()
    Arguments: token  
      This is the refresh token, which was sent along with the bearer token when get_token() was called  
    Returns: None  
    Purpose: Connects to the API and refreshed the bearer token  
      The new token information is saved to token.txt using save_token()  
      A new refresh timer starts with schedule_refresh(), allowing the token to be refreshed before it expires      
    
### save_token()
    Arguments: access_token  
      This is the entire information that the API sends when get_token() or refresh_token() are called  
    Returns: None  
    Purpose: Saves all the token information to a file, token.txt  
      This is so it can be retrieved from any scope within Flask  
    
### schedule_refresh()
    Arguments: expiry, refresh_token  
      expiry - The time in seconds until the bearer token expires  
      refresh_token - The refresh token that was sent to us along with the bearer token  
    Returns: None  
    Purpose: Starts a timer, which is 5 minutes before the expiry of the bearer token  
      This runs in a separate thread, so it doesn't block other processes  
    
