# Tutorial - Creating a Plugin
In this tutorial, we will create a simple plugin for CloudFlare

&nbsp;<br>
## Preparing the Environment
1. Create a subdirectory for the plugin in the 'plugins' directory
    For this tutorial, all files will be in this directory
3. Create an empty __init__.py file in this directory
4. Create a file called 'config.yaml'
    This will contain your plugin's configuration
6. Create a python file called 'cloudflare.py'
    This will contain your main plugin code

&nbsp;<br>
## Prepare the Plugin Template
This part takes place in your python file.

&nbsp;<br>
(1) Optionally add a description to the beginning of the file to explain how it's used, when it was updated, authentication requirements, and outstanding 'to do' items.
    Take a look at other plugins to get examples

&nbsp;<br>
(2) Next, import these modules:

```
from core import teamschat
from core import plugin
```
You will likely require additional modules for your plugins functionality

&nbsp;<br>
(3) Define the location of your config file

```
# Location of the config file
LOCATION = 'plugins\\cloudflare\\config.yaml'
```

&nbsp;<br>
(4) Create a simple class
    This inherits the template class from the core module
    
```
class CloudFlareHandler(plugin.PluginTemplate):
    def __init__(self):
        super().__init__(LOCATION)
        self.table = ""
```
    The 'table' variable is for the SQL table. As we aren't creating one at this point, we'll leave this as a blank string
        This needs to be specified as other functions try to read this variable


&nbsp;<br>
(5) Add a method to handle events (webhooks) as they arrive
    This is added to the class

```
    def handle_event(self, raw_response, src):
        print(raw_response)    
```
'raw_response' is the raw webhook
'src' is the IP that the webhook was sent from
For now, we will just print this to the terminal


&nbsp;<br>
(6) Optionally add an authentication method
    The template will assume that the webhook sender will send a secret in a custom HTTP header (we'll see this again soon)
    It will also assume that the secret in this header is hashed
    However, not all webhook senders do this. Some send the secret in plain text
    If this is the case (as is true with Cloudflare), we need to write a simple authentication method, to overwrite the one in the template:
    
```
    def authenticate(self, request, plugin):
        local_secret = plugin['handler'].webhook_secret
        sender_secret = request.headers[self.auth_header]

        if local_secret == sender_secret:
            return True
        else:
            return False
```

    'request' is the HTTP message (webhook) that has been sent to us
    'plugin' is oie own plugin details
    This code simply checks that the secret sent in the webhook's auth header, matches the one we have
    We'll see where we set these next


&nbsp;<br>
## Prepare the Configuration File
This part takes place in config.yaml

&nbsp;<br>
(1) Optionally, add a description to the beginning of the file
    Look at other plugins for examples
    

&nbsp;<br>
(2) Add some minimal configuration to the config file

```
config:
  webhook_secret: 'Password'
  auth_header: 'cf-webhook-auth'
  chat_id: '19:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@thread.v2'
```
'webhook_secret' is the secret included with the webhook when it is sent
'auth_header' is the header the secret is sent in
'chat_id' is the Teams chat ID that we will be sending messages to
The auth header the is one mentioned in the last section. The webhook sender typically sends a custom HTTP header in the webhook. This can be found in their documentation
The password is something that we define ourselves. This also needs to be configured in the sending service


&nbsp;<br>
## Registering the Plugin
The plugin needs to be registered with the core chatbot program to be loaded on startup

&nbsp;<br>
(1) In the main chatbot directory, open the 'config.yaml' file


&nbsp;<br>
(2) Under the 'plugins' area, add:
    'name' - The friendly name of the plugin
    'route' - This becomes part of the URL that the webhook will be sent to
        eg, 'cloudflare' will accept webhooks sent to 'my_domain.com/cloudflare'
    'class' - The name of the class we created
    'module' - The plugin module, required for the chatbot to call our plugin functions
        This is essentially the path to our main plugin file

As an example:
```
plugins:
  cloudflare:
    name: 'CloudFlare'
    route: 'cloudflare'
    class: CloudFlareHandler
    module: plugins.cloudflare.cloudflare
```


&nbsp;<br>
## Configuring the Service
We can now start the chatbot.
The sending service, CloudFlare in this example, needs to be configured to send webhooks to our URL.
    Make sure the authentication secret is correct
The service probably has a test feature, where you can send a test webhook. This should print a message to the terminal


&nbsp;<br>
## Sending to Teams
Let's extend this to send messages to teams, not just to the terminal

Within the handle_event method, let's remove the 'print' statement, and add this:
```
    event = {
        'text': raw_response['text'],
        'src_ip': src
    }
```
This creates a simple dictionary of two values.
NOTE: The 'text' field may not exist in the webhook sent to you. It depends on the sending service. You may need to modify this appropriately.


&nbsp;<br>
## Extending Your Plugin

    * SQL creation script
    * SQL in the plugin
    * Refresh
    * NLP
    * Priority levels
    * Add HTML spans to your teams messages
    
