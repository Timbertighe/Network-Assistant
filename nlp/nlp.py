"""
Natural Language Processor

Gets text input from a user, via teams
Uses NLP techniques to determine their meaning
Uses rule-based matching to execute an applicable action

Modules:
    3rd Party: spacy, datetime, termcolor, yaml, importlib
    Custom: config, teamschat, parse_chats

Classes:

    ChatNlp
        A chat object that processes NLP input
        Loads custom content (new words and ents)

Functions

    load_devices()
        Load a list of devices and sites as entities into a list
    load_entities()
        Load custom entities from plugins

Exceptions:

    None

Misc Variables:

    known_phrases : list
        A list of dictionaries
        Contains 'global' phrases and the functions to call

Limitations/Requirements:
    Requires the spaCy medium english model to be downloaded/installed
    Only very simple responses are available at this time

Author:
    Luke Robertson - April 2023
"""

import spacy
from datetime import datetime
import termcolor
import yaml
import importlib

from config import LANGUAGE
from config import plugin_list
from core import teamschat
import nlp.personality as personality


# Load a list of 'global' phrases we have
#   NLP matches these phrases and executes the corresponding function
known_phrases = [
    {
        "phrase": "Tell joke",
        "function": "tell_joke",
        "module": "global"
    },
    {
        "phrase": "hello",
        "function": "greeting",
        "module": "global"
    },
    {
        "phrase": "hi",
        "function": "greeting",
        "module": "global"
    },
    {
        "phrase": "Good morning",
        "function": "greeting",
        "module": "global"
    },
    {
        "phrase": "human",
        "function": "are_you_human",
        "module": "global"
    },
    {
        "phrase": "day",
        "function": "day_time",
        "module": "global"
    },
    {
        "phrase": "tell time",
        "function": "day_time",
        "module": "global"
    },
    {
        "phrase": "real person",
        "function": "are_you_human",
        "module": "global"
    },
    {
        "phrase": "thank",
        "function": "thank",
        "module": "global"
    }
]


# Collect a list of devices and sites
def load_devices(filename):
    '''
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
    '''

    patterns = []

    # Open the YAML file
    try:
        with open(filename) as file:
            # Use 'load_all' where there are multiple documents in a file
            try:
                all_devices = yaml.safe_load_all(file)

            except Exception as err:
                print(termcolor.colored(
                    "NLP Entity Ruler: Could not load YAML content",
                    "red"
                ))

                print(termcolor.colored(
                    err,
                    "red"
                ))

                return False

            # Go through each site
            for dev in all_devices:
                # Add the site name to the list
                patterns.append(
                    {"label": "SITE", "pattern": dev['site']}
                )

                # Loop through devices under the site
                # Need to check if the type is None (an empty entry)
                #   None type will throw an error, so we ignore None entries
                if dev['devices'] is not None:
                    # Add the device name to the list
                    for device in dev['devices']:
                        patterns.append(
                            {"label": "DEVICE", "pattern": device}
                        )

    # If there was a problem opening the file
    except Exception as err:
        print(termcolor.colored(
            "NLP Entity Ruler: Could not load site/devices file",
            "red"
        ))

        print(termcolor.colored(
            err,
            "red"
        ))

        return False

    return patterns


# Load custom entities
def load_entities(ent_list):
    '''
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
    '''

    # Loop through each custom word
    patterns = []
    for label in ent_list:
        # Entities will be categorised under a LABEL
        for ent in ent_list[label]:
            patterns.append(
                {
                    "label": label.upper(),
                    "pattern": ent
                }
            )

    return patterns


# Main NLP class
class ChatNlp():
    """Process natural language input input

    Uses the spaCy library for NLP processing
    Adds custom ENTs to the pipeline
    Cleans up input (removes stop words, processes lemma, etc)
    Logs requests that couldn't be recognised for later improvement
    Plugin-aware, so plugins can have phrases too

    Attributes
    ----------
    None

    Methods
    -------
    cleanup_text()
        Removes stop words, punctuation, and pronouns
    log_unknown()
        Logs phrases that couldn't be understood for review later
    chatbot()
        Process a given phrase, and return a function to run
    get_ents()
        Get a list of entities from a phrase
    parse()
        Takes a phrase from a user and responds
    """

    def __init__(self):
        """Constructs the class

        Loads the similarity threshold value
            This is how similar a sentence has to be to match a known phrase
        Loads the spaCy NLP model
        Defines a new entity ruler for custom words
        Creates a list of doc containers with known phrases, and their
            corresponding functions

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        """

        # Set the similarity threshold
        self.threshold = LANGUAGE['threshold']

        # Need >= medium model for word vectors
        self.nlp_spacy = spacy.load("en_core_web_md")

        # Create a new entity ruler for custom words and entities
        #   Add to the pipline before the default NER
        ruler = self.nlp_spacy.add_pipe("entity_ruler", before="ner")

        # Load device and site names into a list of patterns
        patterns = load_devices(filename=LANGUAGE['device_file'])
        if patterns:
            ruler.add_patterns(patterns)

        # Load custom words from plugins into the list of patterns
        #   Not all plugins will implement this
        for plugin in plugin_list:
            if plugin['handler'].entities:
                patterns = load_entities(plugin['handler'].entities)

        # Add the list of patterns into the entity ruler
        ruler.add_patterns(patterns)

        # Create a list of docs for  known phrases and corresponding functions
        self.docs = []

        # Add the global phrases
        for text in known_phrases:
            self.docs.append(
                {"phrase": self.nlp_spacy(text['phrase']),
                    "function": text['function'],
                    "module": text['module']}
            )

        # Add custom NLP phrases for plugins
        #   Not all plugins will have phrases
        for plugin in plugin_list:
            # Add custom phrase lists (if they exist)
            if plugin['handler'].phrase_list:
                for text in plugin['handler'].phrase_list:
                    self.docs.append(
                        {
                            "phrase": self.nlp_spacy(text['phrase']),
                            "function": text['function'],
                            "module": text['module']
                        }
                    )

    def cleanup_text(self, phrase):
        """Convert a phrase to its simplest form

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
        """

        # Simple cleanup (lower case, remove question marks)
        phrase = phrase.lower()
        phrase = phrase.replace("?", "")
        doc = self.nlp_spacy(phrase)

        # Remove any device names and times
        # This makes it easier to match functions
        for ent in doc.ents:
            if ent.label_ == "DEVICE" or ent.label_ == "TIME":
                phrase = phrase.replace(ent.text, "")
                doc = self.nlp_spacy(phrase)

        # Unless stop word, punctuation, or pronoun, add tokens to a list
        result = []
        for token in doc:
            if not (
                token.text in self.nlp_spacy.Defaults.stop_words
            ) or (
                token.is_punct
            ) or (
                token.lemma_ == '-PRON-'
            ):
                result.append(token.lemma_)

        # If everything is removed, return the original text
        if len(result) == 0:
            return phrase

        # Return the list of tokens as a string
        return " ".join(result)

    def log_unknown(self, phrase, processed_doc):
        """Log details of a phrase that couldn't be understood

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
        """

        # Look through the list of phrases that are known (self.docs)
        match = {}
        for doc in self.docs:
            # Check that vectors exist
            #   Typos have no vectors, so can't be compared
            if processed_doc and processed_doc.vector_norm:
                # Get the similarity of this phrase
                similarity = doc['phrase'].similarity(processed_doc)

            else:
                # If there are no vectors, set the similarity to 0
                similarity = 0

            # Record closest match for the log
            #   If this is the first match, add it to the dictionary
            #   Otherwise, check if it's a better match than what we have
            if len(match) == 0 or match['similarity'] < similarity:
                match['doc'] = doc
                match['similarity'] = similarity

        # Write the information to the log file
        #   A new log file is created for each month
        month = datetime.now().strftime("%B")
        with open(f"nlp_log-{month}.txt", "a") as file:
            file.write(f"\nGiven Text: {phrase}\n")
            file.write(f"Cleaned Text: {processed_doc}\n")
            file.write(f"Closest match: {match['doc']}\n")
            file.write(f"Closest similarity: {match['similarity']}\n")

    def chatbot(self, phrase):
        """Define the chatbot's response to a phrase

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
        """

        # Cleanup the text
        phrase = phrase.lower()
        clean_text = self.cleanup_text(phrase)

        # Create docs with the original and cleaned phrases
        original_doc = self.nlp_spacy(phrase)
        clean_doc = self.nlp_spacy(clean_text)

        # Print debug information to the terminal
        print(termcolor.colored("Original Text: ", "yellow"), original_doc)
        print(termcolor.colored("Cleaned Text: ", "yellow"), clean_doc)

        # Calculate the similarities between the cleaned phrase and
        #   known phrases (all stored in doc containers)
        match = {}
        for doc in self.docs:
            # Get the similarity score (as long as vectors exist)
            if clean_doc and clean_doc.vector_norm:
                similarity = doc['phrase'].similarity(clean_doc)

            # If there are no vectors, it's likely this is a typo
            else:
                print("There are no vectors for this word; Was it a typo?")

                # If logging is enabled, log this phrase
                if LANGUAGE['log_unknown']:
                    self.log_unknown(phrase, clean_doc)

                return False

            # If we have a similar phrase, we add the details to a dict
            if similarity >= self.threshold:
                # If there's nothing already in the list, add this in
                # Or if this is more similar than something already in the list
                if (len(match) == 0) or \
                  (match['similarity'] < similarity):
                    match = {
                        "nlp_doc": doc['phrase'],
                        "similarity": similarity,
                        "function": doc['function'],
                        "module": doc['module']
                    }

        # If similar_list is empty, there has been no match
        if len(match) == 0:
            # Check if we want to log this
            if LANGUAGE['log_unknown']:
                self.log_unknown(phrase, clean_doc)
            return False

        # Return the dictionary containing the doc and handler function
        else:
            return match

    def get_ents(self, phrase):
        """Get entities and their type

        Parameters
        ----------
        phrase : str
            A phrase in which we want to find entities

        Raises
        ------
        None

        Returns
        -------
        ent_list : list
            A list of dictionaries
            Each dict contains an entity and its label
        """

        # Create a doc for the given phrase
        doc = self.nlp_spacy(phrase)

        # Extract entities from the original message
        ent_list = []
        for ent in doc.ents:
            entity = {
                "ent": ent.text,
                "label": ent.label_
            }
            ent_list.append(entity)

        return ent_list

    def parse(self, phrase, chat_id):
        """Parse a phrase and find a function to call

        Parameters
        ----------
        phrase : str
            The user's original phrase
        chat_id : str
            The Teams chat Id to reply to

        Raises
        ------
        None

        Returns
        -------
        match : dict
            Details of the matching phrase (eg, function to call)
        False: boolean
            If there was no matching response
        """

        # Strip out any HTML 'p' tags
        phrase = phrase.replace("<p>", "").replace("</p>", "").lower()

        # Find a match for this phrase
        response = self.chatbot(phrase)

        # If there is no matching response, write back to the user
        if not response:
            teamschat.send_chat("Sorry, I don't understand", chat_id)
            return False

        # If there is a phrase match, we need to call the associated function
        if response['module'] == 'global':
            function = getattr(personality, response['function'])

        # If the module is a plugin, import the module and set the function
        else:
            module = importlib.import_module(response['module'])
            function = getattr(module, response['function'])

        # Call the function, passing the list of entities and the phrase
        entities = self.get_ents(phrase)
        function(chat_id, ents=entities, message=phrase)
