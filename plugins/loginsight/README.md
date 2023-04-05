# LogInsight plugin
Receive alerts from vRealize Log Insight
This has been tested with Log Insight 8.6

# Using the plugin
### Enabling Webhooks
    Webhooks need to be enabled in Log Insight. This is done by creating a webhook, and assigning to alerts
    
#### Creating a Webhook
    (1) Administration > Webhook
    (2) New Webhook
    (3) Add a name
    (4) Change the endpoint to 'custom;
    (4) Add the Webhook URL
    (5) Set the content type to JSON, and the action to POST
    (6) Authorization is currently unsupported by the plugin, as it is sent in CLEARTEXT
    (7) Add the Webhook Payoad (notice 'messages' has no quotes):
    
```json
{
  "source": "Log Insight",
  "alert_name": "${AlertName}",
  "timestamp": "${TriggeredAt}",
  "messages": ${messages},
  "recommendation": "${Recommendation}",
  "url": "${Url}"
}
```

#### Creating an alert
    (1) Go to Interactive Analytics
    (2) Enter your query terms as appropriate
    (3) On the right, click the bell, and then 'Create Alert from Query'
    (4) Enter an alert name
    (5) Enter a description
    (6) Set your trigger conditions
    (7) In the 'notify' area, select the webhook you want to send to
    (8) Optionally, add some recommendations, should this alert be triggered
    
### Authentication
    Currently, this plugin does not use authentication; This will be added in future

### Configuration
    Plugin configuration is in the 'config.yaml' file
    There is very little in this file at this time

#### Event Filtering
    There is no event filtering availble in the plugin at this time
    The filtering should instead be done at the source (Log Insight alert queries)
    

- - - -
## Files
### loginsight.py
    The main class of the plugin (LogInsight)
    
#### __init__()
    Loads the configuration file
    Sets up the framework for webhook authentication (to be added in future)
    
#### handle_event(raw_response, src)
    Takes an event and sends to to parse_message() to be normalized
    Prepares a messages for teams, and sends it to log()

#### parse_message(event)
    Takes the events, and puts them into a standard dictionary for better handling

#### log(message, event)
    Takes a message (as output to teams), and an event (dictionary of event information)
    Prints the event to the terminal
    Sends the message to teams
    Logs the details in SQL

#### authenticate(request, plugin)
    Checks webhook is valid
    The webhook is sent with a username and password in the HTTP header (in CLEARTEXT)
    The names of the headers are in config.yaml
    The user and secret are also in config.yaml
    The values in the headers are validated against the ones in the config file
