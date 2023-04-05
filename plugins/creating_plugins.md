# Creating plugins
Customised plugins can be written for any service. These typically inject webhooks, but may send API requests a well.  
While much of this is customized, there are some guidelines that must be followed


### Plugin Location:
    All plugins are located in their own folder under the 'plugins' folder
    Within the plugin folder, be sure to create an __init__.py file
    The __init__.py may be left empty
    
    
### Configuration File
    Each plugin should have a YAML file for configuration
    The file name can be flexible, but something like 'config.yaml' is suggested
    The config file should have a 'config' section
    Under the config section there should be:
        'webhook_secret' - Set a secret here, or leave blank for unauthenticated
        'auth_header' - The name of the header that contains the authentication information
        'sql_table' - The name of the SQL table in the SQL DB
        'chat_id' - The ID of the chat to send alerts to
    Additional plugin specific configuration can also be stored here
    
    
### Python files
    The plugin will need to have at least one python file. 
    The name of the file is flexible, as long as it doesn't conflict with other imports
    Optionally, consider creating a standalone SQL script to create tables and fields in an SQL DB
    
    
### Python Modules
    Several modules will need to be imported:
        - teamschat (from core)
        - plugin (from core)
        
        
### Template
    In the 'core' folder there is a plugin.py file, containing the PluginTemplate() class
    This class can be inherited by other plugins to make them simpler and standardized
        These methods can be overwritten by a plugin, or not inherited at all
    The template contains:
        - __init__()
            Initialise the class
            Read the config.yaml file
        - ip2integer()
            Convert an IP address to an integer
        - refresh()
            Reread the config.yaml file (eg, if there have been changes)
        - sql_write()
            Write entries to an SQL database
        - authenticate()
            Authenticate a webhook
            
            
#### NLP Phrases
    The plugin template has a 'phrase_list' variable; This is set to False
    If plugins do not use NLP, they can leave this as it is
    If plugins do use NLP, they can set this to a list of dictionaries, containing phrases, modules, and functions
        An example of this can be found in the Junos plugin
        
        
#### NLP Entities
    The plugin has an 'entities' variable, which is set to False by default
    If plugins do not use NLP, they can leave this as it is
    If plugins do use NLP, they can set this to a list LABELS, which has a sub list of PATTERNS
        An example of this can be found in the Junos plugin    
    
    
### Class
    The plugin will need a class with these methods as a minimum (names can be customised):
        __init__() - Reads the configuration file
            Needs to refer to the location of the config file
        handle_event(raw_response, src) - Process webhooks when they arrive
            'raw_response' is the unedited webhook
            'src' is the IP address of the sender
        
    Optionally, the plugin may want to support methods to:
        Log information to SQL
        Assign priorities to events, to improve handling
        Filter events
        Log debugging information to a text file
        

### Registering the Plugin
    To be loaded, the plugin needs to be registered. This is done in the config.yaml file in the main app
    Under the 'plugins' section, create a new entry. This needs to contain:
        name - The friendly name of the plugin
        route - The Flask route (URL) that the app listens on 
        class - The name of the class, as defined in the plugin
        module - The module that gets imported. This includes these fields
            'plugins' - Represents the plugins folder (do not change)
            plugin folder - The folder the plugin is stored in
            module - The mpodule name (the python file to import into the app)
            
            
 ### Authentication
    Webhooks should be authenticated when the arrive
    The plugin template class has a method to authenticate webhooks, which compares headers in the webhook with configured values
    However each source system uses different settings, so a custom method may need to be written for the plugin
    
