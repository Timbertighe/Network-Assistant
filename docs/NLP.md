# Natural Language Processing


## spaCy Library
    NLP is provided by the spaCy library.
    This is a rudimentary NLP deployment, as it only simply determines how similar a given sentence is to a known phrase
    This uses token vectors, so the medium model is needed at a minimum

```
python.exe -m pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_md
```

&nbsp;<br>
## Configuration
    Configuration is in the main config.yaml file
    There is a section called 'language'. There are two configuration options within:
    * threshold - How similar phrases have to be to be considered a match
    * log_unknown - When a phrase has no suitable matches, the details can be logged to a file for later analysis


&nbsp;<br>
## Phrase Matching
    There is a list of known phrases, which have been 'sanitized'. That is, they have had stop words, punctuation, and pronouns removed
    For example, one phrase might be 'tell joke'.
    
    When a user enters a phrase, this is also sanatized. spaCy is then used to check the similarity between this phrase, and the list of known phrases.
    The result with the highest similarity, as long as it's over the given threshold (as configured in config.yaml), will be considered a match.
    If there's no result over the threshold, then there is no match for the given phrase.
    
    Each known phrase has a function associated with it. When that phrase is matched, the function is executed.
    
    
&nbsp;<br>
## Devices
    A list of devices are stored in devices.yaml
    As device names and hostnames are usually specially created, NLP does not recognise them by default
    Devices in this config file are added to the NLP pipeline as 'devices', so they can be understood when they are used in chat


&nbsp;<br>
- - - -
## nlp.py
    Contains the ChatNlp class
    This is instantiated during startup
    
### Initialization
    (1) Sets a threshold that needs to be reached to be considered a match (set in the config file)
    (2) Loads the spaCy medium model
    (3) Adds a custom entity ruler into the pipeline
        This includes custom words, such as device names
        This is taken from devices.yaml
        Also loads custom ents from plugins, if applicable (checks if 'entities' exists in the plugin handler class)
    (4) Loads some 'known_phrases', a list of dictionary items that contain a phrase and matching function
        During initialization, a new list of dictionaries (called 'docs') is created. The only difference is that the phrase has been replaced with spacy docs.
        These are 'global' phrases, which are not from plugins
    (5) Loads additional phrases from plugins
        Plugins don't need to have phrases, they are optional
        These phrases include the plugin's module name and function to call when the phrase is matched

### cleanup_text()
    Arguments: 
        'text' (string; the raw text from the user)
    Returns: 
        A string; The raw text after stop words, punctuation, and pronouns are removed
    Purpose:
        This improves matching by removing parts of the sentence that are not needed
        Removes DEVICE and TIME ents from the string (this improves phrase matching); These can still be used after matching is complete

### log_unknown()
    Arguments:
        'text' (string; the raw text from the user)
        'processed_doc' (spacy doc object; The text from the user that has been processed by the spacy pipeline)
    Returns:
        None
    Purpose:
        When there's no match to a known phrase, this function can optionally be used to log this information
        This is logged to a text file, and contains the given phrase, the cleaned text, the closest match, and the similarity value to the closest match
        If there is a typo, there will be no vectors, so the similarity is set to zero

### chatbot()
    Arguments:
        'user_text' (string; the raw text from the user)
    Returns:
        'similar_list' (dict; Contains the doc object for the user's phrase, similarity score, and associated module/function)
    Purpose:
        This is the main chatbot function. It is called when someone sends a message to the chatbot in Teams
        This will first call cleanup_text() to sanatize the given phrase, then create a spacy doc object to represent it
        It will then loop through the 'docs' list to find a match; This list contains doc objects for known phrases
        It will extract the doc object that is most similar, as long as it is over the similarity threshold
        If there is a typo, this will be detected as there are no vectors on the token; This causes the similarity to be zero
        If there is no match, the unknown phrase can be optionally logged (depending on whether the 'log_unknown' option is enabled)
        
### dev_list()
    Arguments:
        None
    Returns:
        'patterns' (a list of dictionaries)
        Contains NLP patterns to add to the entity ruler
    Purpose:
        Uses the devices.yaml file to add custom words (eg, device names) to the NLP pipeline
        This is so the chatbot can understand device names as 'device' and not jibberish
        
### get_ents()
    Arguments:
        'message' (the original message sent to the chatbot)
    Returns:
        'ent_list' (A list of dictionaries, containins ent labels and types
    Purpose:
        Collects entities from the given message
        Returns them to the calling function, so other functions can make use of them as they see fit
        
### load_ents()
    Arguments:
        ent_list - A list of custom entities
            A list of PATTERNs is stored under a LABEL
    Returns:
        patterns - A dictionary of patterns and labels
    Purpose:
        Creates a list of dictionaries
        Each dictionary is a PATTERN/LABEL
        This can be loaded into the entity ruler
        
        
&nbsp;<br>
- - - -
## devices.yaml
    This is a YAML file that contains devices and hostnames, organized by site.
    Each site is in a separate YAML document (but a single physical file)
    Everything in this file is added as entities to the NLP pipeline


&nbsp;<br>
- - - -
## parse_chats.py
    Parses messages sent to the chatbot, so it can respond

### parse()
    Arguments:
        message - The message sent to the chatbot over Teams
        chat_nlp - The NLP object
        chat_id - The chat ID to respond to
    Returns:
        None
    Purpose:
        Takes a raw message and sees if it matches any known NLP phrases (using the chatbot()function in the chat_nlp object)
        Collects additional entities in the message (which are passed in simplified form to the handling function to use)
        Calls an appropriate handler function, if one is found
            Passes it the chat id to respond to, NLP entities, and the original message
        This could be a 'global' function, such as the ones below, or a function that belongs to a plugin
    
### tell_joke()
    A personality module that tells jokes
    
### greeting()
    A personality module that responds to greetings
    
### get_weather()
    A personality module that gives weather information
    
### are_you_human()
    A personality module that responds to questions about being human
    
### day_time()
    A personality module that provides the day and time
   
    



