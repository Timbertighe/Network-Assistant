# CloudFlare plugin
Handles webhooks from the CloudFlare platform

# Using the plugin
## Webhooks
### Enabling Webhooks
    This requires webhook alerts to be configured on CloudFlare
    This uses a global webhook definition
    Then, enable the webhook as an alert destination on individual services
    
### Webhook Authentication
    CloudFlare webook authentication uses the 'cf-webhook-auth' header
    This contains a secret that is defined in the cloudflare platform
    This secret is sent in plain text
    

## Configuration
### Overview
    Plugin configuration is in the 'config.yaml' file
    
#### Plugin Config
    Set 'webhook_secret' to the secret, as set in the CloudFlare webhook configuration
    Set the 'auth_header' to cf-webhook-auth


&nbsp;<br>
- - - -
## Files
### config.yaml
    A YAML file that contains all the config for the plugin
    This includes:
        * webhook_secret - The secret we expect to see from the device sending the webhook
        * auth_header - The header we expect to see in the webhook message
        * chat_id - The chat ID to send alerts to

&nbsp;<br>
### cloudflare.py
    The CloudFlareHandler class that handles events as they are received
    
#### __init__()
    Loads the config file
    
#### handle_event(raw_response, src)
    Handles a webhook when it arrives
        'raw_response' is the raw webhook
        'src' is the IP that sent the webhook
    Creates a dictionary of useful information
    Creates a message for the user
    Sends the message to teams
    
