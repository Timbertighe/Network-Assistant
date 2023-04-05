# Web Service
    A web service runs continually, and listens for webhooks and authentication details  
    The web service is built in Flask  

## Routes
### /test
    Method: GET, HEAD  
    A simple route, used to test if the service is up  
    This can be polled by a monitoring solution  
   

&nbsp;<br>
### <handler>
    Method: POST  
    This is a dynamic route, which is created based on plugins   
    Webhooks are sent to this location, and then authenticated using a header, as specified by the plugin   
    The plugins handler method is called to deal with the webhook


&nbsp;<br>
### /callback
    Method: GET  
    This is the callback point for authentication with the MS Identify Platform  
    During authentication, the client code will be sent here  
    This URL needs to be registered in the application on the Identity Platform (see ms-identity.txt)  
  
  
&nbsp;<br>
### /chat
    Method: POST
    This is the callback point for chat subscriptions
    This is also where new chats are sent
    Chats are decrypted, and sent through to the message parser
    Includes a check that it's not the chatbot sending the message
    Includes a check that the sender is on the authorized list
        Informs the admin chat_id if they're not authorized


&nbsp;<br>
- - - -
## web-service.py
### load_plugins()
    Arguments: A list of plugins (from global config)
    Returns: None
    Purpose:
      Loads plugins, and stores details in a table


&nbsp;<br>
### Global
    (1) Read configuration file (using config.py), and set variables  
    (2) Initialize a Flask app  
    (3) Load plugins
    (4) Create an NLP object
    (5) Begin authentication  
    (6) Get a list of known chat IDs and names, and print them
    (7) Subscribe to chat notifications
    (8) Start the Flask routes  
