# Change Log

&nbsp;<br>
## 0.91
### General
    Improved docstrings on many files
    Moved nlp into a separate package
    Cleaned up the ChatNlp class to startup functions are separate (they don't need to be in the class)
    
### Plugins
    Added a CrowdStrike plugin
    Just basic alerting at this time


&nbsp;<br>
## 0.9
### Platform Improvements
    Improved docstrings across multiple modules
    Remmoved the webhook secret from global config, as it is now per-plugin
    Revamped the chat subscription module in teamschat.py, to be class based and threaded (startup performance imporovement)
    Removed hardcoded filenames in several modules (moved to global config)
    
### General
    Recreated the GitHub repository


&nbsp;<br>
## 0.8
### Chat ID
    Supported plugins to specify which chat ID they want to send their alerts to
    Each plugin config file now has a 'chat_id' for this purpose
    There is still a 'chat_id' in the global config, which can be used for administrative purposes (eg, could not write to SQL)
    The send_chat() function now requires a chat ID to be passed to it
    
### One-to-One chats
    1:1 chats are now supported, so users can communicate with the chatbot directly
    The chatbot subscribes to all message notifications, not just ones for a specific chat-id
    
### Authorized senders
    A list of allowed senders has been added to the global config file
    This prevents unauthorized users from getting the chatbot to share sensitive information, or taking action
    If a user unknown to the chatbot tried to talk to it, the admin chat will be informed
    
### Subscriptions
    Subscriptions can be to 'all chats', which requires additional payment to Microsoft
    Or, separate subscriptions can be made to individual chat IDs, as listed in the 'authorized senders' list
    
### Device Authentication
    The chatbot plugins may connect to remote devices such as routers, switches, and servers; These require authentication
    This version adds a 'secrets.yaml' file in the 'core' folder
    This stored encrypted credentials for these devices, secured with a master password
    
### NLP
    Improved phrase matching
    Added a list of devices in devices.yaml
    Added a custom entity ruler with customer objects (eg, device names)
    Converted functions to a class
        This is instantiated during startup
    The chatbot() function returns a module and function to call when a phrase is matched
        Previously this was just a function
        This supports calling functions in other plugins
    Added a phrase list to the plugin template class
        This is set to False by default (plugin does not use NLP)
        Each plugin can override this and add custom phrases
    Added a function to get entities, and return the label and type for other functions to use
    Improved handling typos
        These are valid SpaCy doc object, but have no vectors
        No vectors causes similarity checking to fail, so we now check that vectors exist first
    Improved phrase cleanup
        Also removes TIME ents from the phrase before checking similarity
        This improves phrase matching
    Enabled loading of custom entities from plugins
    
### teamschat.py
    Added several new functions to make the flow of the code smoother and easier to understand/troubleshoot
        - sub_refresh()
        - read_public()
        - new_sub()
    Updated check_token to return False on error
    Updated subscribe() to handle errors if a token is unavailable
    Removed token checking from check_sub(), as this is already done in subscribe()
    Moved the USER_ID to config.yaml
    Updated error handling if there is no public key available
    
### config.yaml
    Added a 'sub_all' option to the 'teams' section, so we can subscribe to all chats at once, or specific chats
    Moved the teams 'user_id' here, rather than in teamschat.py
    
### crypto.py
    Added error handling for cases when there is no private key available
    
### General Improvements
    Removed coloured logging to the terminal for normal events
      Saving coloured logging for more critical and note worthy events
    Added password encryption and decryption scripts (in the tools folder)
    Added better error handling when sending messages to teams
      POSTing to the API
      Getting a subscription list
      When a message can't be sent
    Added error handling to check_sub(), in case Graph API does not return what we expect it to
    Created an NLP class
      Instantiated during startup by web-service.py
      For chats, this object is passed to the parse() function
    Removed the 'quiet time' module as it wasn't providing any value, and could get in the way


&nbsp;<br>
## 0.7
### NLP
    Added basic support for NLP with spaCy
    This is rudimentary, but allows simple interaction with the chatbot
    Created core/nlp.py

### Quiet Time
    Added support for a 'quiet time' when the chatbot won't send messages to teams
    It will still log events to the SQL server
    This is not plugin dependant
    This is configured in config.yaml, by changing the 'sleep_time' and 'wake_time' variables
    
### Bug Fixes
    Fixed a bug where the previous config and next config were reversed (in the Mist plugin)
    Fixed a bug where the chatbot would always use the same teams response to everything

&nbsp;<br>
## 0.6
### General
    Added colours to terminal logging
    Added support to send messages to the chatbot. This is very rudimentary at this stage, and is only used for testing
        Try typing 'hi' or 'tell me a joke'
    
### Azure Authentication
    Converted 'azureauth' to a class
    Added support for users other than the logged in one (configure in config.yaml)

### Plugins
    Added a template for plugins, to make plugin creation simpler
    Fixed a bug in the plugin loader

&nbsp;<br>
## 0.5
### General Updates
    Updated token read/write to use 'with'
    Moved teams details (secret, app ID, etc) from azureauth.py to a section in config.yaml
    Changed how plugins are loaded, so the list is available globally
    Enabled plugin config refresh as part of the regular Graph API token refresh
  
### SQL Improvements
    Moves SQL functions to a class
    Will now connect, process, and gracefully close the connection for each transaction
    Moved 'sql-create' to each plugins folder
  
### Added a Log Insight plugin
  
### Mist plugin improvements
    Removed sys.exit() on failure, so the whole app doesn't close
    Converted logging to a class
    Updated logging to use 'with'
    Added a 'refresh' method to read config changes
    Switch/Mist config changes will now only show the changes (diff) not the entire config
  
### Junos plugin improvements
    Removed sys.exit() on failure, so the whole app doesn't close
    Added an 'events' section to the config file, to support event filtering
    Added SQL logging
    Added a 'refresh' method to read config changes

- - - -
&nbsp;<br>
## 0.4
### Added PEP8 compliance in python code   

### Broke out project into folders   
    core - Core project files, including Azure authentication, SQL access, hashing, etc   
    plugins - contains various plugins that can be added or removed (eg, mist, junos)   
  
### Plugins   
    Added plugin list to the global config file (route, name, class)   
    Plugins will dynamically create a Flask route   
    No core components, other than the config file, have plugin specific code   
    Each plugin needs to have a class with a method called 'handle_event'   
    Webhool verification is part of the plugin   
    
### Separated hashing functions from Mist, and made it a core function   
  
### SQL   
    Added teams notifications for SQL errors
  
### Mist plugin:   
    Converted the handler to a class   
    
### Junos plugin:   
    Created a basic junos plugin   
    Requires an agent to be added to /var/db/scripts/events/ on the Junos device   
    Requires 'event-options' configuration   
    Authenticates webhooks based on a header   

&nbsp;<br>
- - - -
