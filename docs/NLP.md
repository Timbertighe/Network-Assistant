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
    
### ChatNLP class
    Uses the spaCy library for NLP processing
    Adds custom ENTs to the pipeline
    Cleans up input (removes stop words, processes lemma, etc)
    Logs requests that couldn't be recognised for later improvement
    Plugin-aware, so plugins can have phrases too
    
#### Initialization
    Loads the similarity threshold value
        This is how similar a sentence has to be to match a known phrase
    Loads the spaCy NLP model
    Defines a new entity ruler for custom words
    Creates a list of doc containers with known phrases, and their
        corresponding functions

#### cleanup_text()
    Convert a phrase to its simplest form

    Remove stop words, punctuation, and pronouns
    Convert tokens to their lemma form

    Parameters
    ----------
    phrase : str
        The user's phrase that we want to try to match against
            a known phrase

    Raises
    ------
    None

    Returns
    -------
    phrase : str
        The phrase after it has been cleaned up
        This may return the original phrase

#### log_unknown()
    Log details of a phrase that couldn't be understood

    Sometimes phrases can't be understood
    This logs this information to improve on later
    A new log file is created every month

    Parameters
    ----------
    phrase : str
        The user's original phrase

    processed_doc : spaCy doc container
        The doc after processing

    Raises
    ------
    None

    Returns
    -------
    None

#### chatbot()
    Define the chatbot's response to a phrase

    Uses the cleanup_text() method to get a simpler phrase
        This improves matching against known phrases
    Checks for a match by comparing the similarity of the cleaned phrase
        to known phrases

    Parameters
    ----------
    phrase : str
        The user's original phrase

    Raises
    ------
    None

    Returns
    -------
    match : dict
        Details of the matching phrase (eg, function to call)
    False: boolean
        If there was a problem
        
#### get_ents()
    Arguments:
        'message' (the original message sent to the chatbot)
    Returns:
        'ent_list' (A list of dictionaries, containins ent labels and types
    Purpose:
        Collects entities from the given message
        Returns them to the calling function, so other functions can make use of them as they see fit
        
### load_devices()
    Loads a list of devices and sites into a list
    These are formatted as entities, so they can be handled by spaCy

        Parameters:
            filename : str
                The filename containing the list of devices and sites

        Raises:
            Exception
                When there's a problem loading the file
            Exception
                When there's a problem loading YAML content

        Returns:
            patterns : list
                A list of dictionaries
                This is a list of words that will be added to the pipeline
            False : boolean
                If there is a problem loading the file or YAML
        
### load_entities()
    Loads custom words as entities, so they can be handled by spaCy

        Parameters:
            ent_list : str
                The list of custom words

        Raises:
            None

        Returns:
            patterns : list
                A list of dictionaries
                This is a list of words that will be added to the pipeline
        
        
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
   
    



