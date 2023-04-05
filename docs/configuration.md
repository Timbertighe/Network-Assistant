# Global Configuration
    There are several settings that are needed for Flask, Graph API, and for plugins  
    These are configured in config.yaml, and read by config.py  
    For example, web-server port number, API endpoint, etc  
  

## config.py
### Global
    (1) Creates five dictionaries:  
      GRAPH - Contains settings for Graph API  
      GLOBAL - Contains settings for the web-service  
      SMTP - Contains settings for the SMTP server
      TEAMS - Contains teams specific configuration
      LANGUAGE - Contains NLP configuration
    
    (2) Reads config.yaml  
      Stores setting in the dictionaries  
    
    
    
&nbsp;<br>
- - - -
## config.yaml
    This is a standard YAML file, which makes it easy for admins to configure  
    There are six sections:  
      global - Settings that apply to the web-service  
      plugins - A list of plugins to be loaded
      graph - Settings that apply to the Graph API  
      teams - Teams settings
      language - NLP settings
      smtp - Email settings

&nbsp;<br>
### Global
    web_port - The port the web server runs on. Set to 8080 by default  
    webhook_secret - The secret (password) that must be set on webhook messages  
    flask_debug - Enables debug mode
      This applies to Flask, as well as to SQL (log the query strings sent to the SQL server)
    db_server - The name or IP address of the database server
    db_name - The name of the database
    chatbot_name - The name of the chatbot (so it won't respond to its own teams messages)
    sleep_time - The time at which 'quiet time' begins
    wake_time - The time at which 'quiet time' ends
    
    Note, if the sleep and wake times are the same, Quiet Time is effectively disabled
    

&nbsp;<br>
### Plugins
    Contains a list of plugins
    Each plugin contains:
      A name
      A route (used with Flask)
      A class (contains methods to handle the webhook messages)
      A module (a method in the class that Flask will use when webhooks come in)

### Graph
    base_url - The base URL of the Graph API  
      https://graph.microsoft.com/v1.0/ by default  
    chat_id - The chat ID of the Teams chat that messages are sent to  
      Used for administrative purposes (eg, SQL errors, quiet time, etc)
    key_id - An optional value used when subscribing to Graph notifications
    chat_url - The URL that chat notifications are sent to

### Teams
    app_id - The ID of the Teams application in the MS Identity portal
    secret - The secret (password) for the application
    tenant - The tenant's ID
    user - The UPN of the account that sends messages to Teams
    approved_ids - A list of chat IDs that the chatbot is allowed to interact with
    
### Language
    threshold - The minimum similarity value that needs to be met for a match to be positive (see NLP docs)
    log_unknown - True or False. Enables us to log chats that the chatbot could not understand
  
### SMTP
    This is used to send an email alert if there is a problem connecting to Teams  
    This is not used for general notifications

    server - The name or IP address of the SMTP server
    port - The destination port of the SMTP server (eg, 25)
    sender - The sending email address
    receivers - A list of addresses that receive the alert


