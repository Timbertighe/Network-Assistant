# chatbot
A simple Network assistant that takes alerts and events, and sends them to teams


### Script Usage:
    Run this application with 'python web-service.py' to start a Flask instance
    Webhooks can be sent (POST) to a route, as defined by each plugin
    Test the application by browsing to /test
    Uses the MS Graph API to send chat messages to teams
    
### Authentication:
    This application needs to be registered in Microsoft Identity Centre, and a callback URL needs to be set
    Authentication uses OAuth 2.0; You need an application ID and a client secret
    The callback is set to /callback
    A teams user needs to login when the web-service runs, and approve access to teams
    
### Plugins:
    Plugins for specific webhook senders are sub-directories within the 'plugins' folder
    Plugins are enabled in the config.yaml file

### Restrictions:
    Requires the Flask, msal, and requests modules to be installed with pip
    The MS bearer token is saved to disk, as read as needed
    HTTPS is not supported on the web service. Use a separate reverse proxy to add HTTPS
    Needs a public IP for webhooks to be sent to, and for the callback URL
    The public IP and port (tcp/8080 by default) needs to be allowed into the application (check firewall settings)

### Notes:
    Global configuration is done in config.yaml
    Each plugin has with own config.yaml file for plugin-specific configuration
    The spaCy library is used to support natural language with the chatbot



