"""
Natural Language Processor: Process text input and figure out how to handle it

Usage:
    Instantiate the ChatNlp class

Authentication:
    None

Restrictions:
    Limited responses at this time

To Do:
    Improve responses

Author:
    Luke Robertson - March 2023
"""

import spacy
from config import LANGUAGE
from config import plugin_list
from datetime import datetime
import termcolor
import yaml


class ChatNlp():
    def __init__(self):
        # Set the similarity threshold
        self.threshold = LANGUAGE['threshold']

        # Need >= medium model for word vectors
        self.nlp_spacy = spacy.load("en_core_web_md")

        # Create an entity ruler to add device names as words
        ruler = self.nlp_spacy.add_pipe("entity_ruler", before="ner")
        patterns = self.dev_list()
        ruler.add_patterns(patterns)

        # Add custom words from plugins
        for plugin in plugin_list:
            if plugin['handler'].entities:
                patterns = self.load_ents(plugin['handler'].entities)
        ruler.add_patterns(patterns)

        # Load a list of phrases we have
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
                "phrase": "weather city",
                "function": "get_weather",
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
                "phrase": "real person",
                "function": "are_you_human",
                "module": "global"
            },
        ]

        # Create a list of docs and corresponding functions
        # Adds global phrases, as well as plugin specific phrases
        self.docs = []
        for text in known_phrases:
            self.docs.append(
                {"phrase": self.nlp_spacy(text['phrase']),
                    "function": text['function'],
                    "module": text['module']}
            )

        # Add custom NLP for plugins
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

    # Remove stop words, punctuation, and pronouns to improve accuracy
    def cleanup_text(self, text):
        text = text.lower()
        result = []

        # Create a doc with the given text (converted to lower case)
        doc = self.nlp_spacy(text)

        # Remove any device names and times
        # This makes it easier to match functions
        for ent in doc.ents:
            if ent.label_ == "DEVICE" or ent.label_ == "TIME":
                text = text.replace(ent.text, "")
                doc = self.nlp_spacy(text)

        # Unless stop word, punctuation, or pronoun, add tokens to a list
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
            return text

        # Return the list of tokens as a string
        return " ".join(result)

    # Log details of unknown input
    # Take the raw text and the doc
    def log_unknown(self, text, processed_doc):
        month = datetime.now().strftime("%B")
        match = {}
        for doc in self.docs:
            # Check that vectors exist
            # Typos have no vectors, so can't be compared
            if processed_doc and processed_doc.vector_norm:
                similarity = doc['phrase'].similarity(processed_doc)
            else:
                similarity = 0

            # Record closest match for the log
            if len(match) == 0 or match['similarity'] < similarity:
                match['doc'] = doc
                match['similarity'] = similarity

        with open(f"nlp_log-{month}.txt", "a") as file:
            file.write(f"\nGiven Text: {text}\n")
            file.write(f"Cleaned Text: {processed_doc}\n")
            file.write(f"Closest match: {match['doc']}\n")
            file.write(f"Closest similarity: {match['similarity']}\n")

    # Define the chatbot's response for certain keywords
    def chatbot(self, message):
        # Cleanup the text
        message = message.lower()
        clean_text = self.cleanup_text(message)

        # Create a doc with our input phrase
        original_doc = self.nlp_spacy(message)
        clean_doc = self.nlp_spacy(clean_text)

        print(termcolor.colored("Original Text: ", "yellow"), original_doc)
        print(termcolor.colored("Cleaned Text: ", "yellow"), clean_doc)

        # Calculate the similarities between every pair of Doc objects
        similar_list = {}
        for doc in self.docs:
            # Get the similarity score (as long as vectors exist)
            if clean_doc and clean_doc.vector_norm:
                similarity = doc['phrase'].similarity(clean_doc)
            else:
                print("There is no vectors for this word; Was it a typo?")
                if LANGUAGE['log_unknown']:
                    self.log_unknown(message, clean_doc)
                return

            # If suitably similar...
            if similarity >= self.threshold:
                # If there's nothing already in the list, add this in
                if len(similar_list) == 0:
                    similar_list = {
                        "nlp_doc": doc['phrase'],
                        "similarity": similarity,
                        "function": doc['function'],
                        "module": doc['module']
                    }

                # If there's already something in the list
                else:
                    if similar_list['similarity'] < similarity:
                        similar_list = {
                            "nlp_doc": doc['phrase'],
                            "similarity": similarity,
                            "function": doc['function'],
                            "module": doc['module']
                        }

        # Handle unknown inputs
        if len(similar_list) == 0:
            # Check if we want to log this
            if LANGUAGE['log_unknown']:
                self.log_unknown(message, clean_doc)
            return

        # Return the dictionary containing the doc and handler function
        else:
            return similar_list

    # Get a list of entities and their type
    def get_ents(self, message):
        # Extract entities from the original message
        doc = self.nlp_spacy(message)
        ent_list = []

        for ent in doc.ents:
            entity = {
                "ent": ent.text,
                "label": ent.label_
            }
            ent_list.append(entity)

        return ent_list

    # Collect a list of devices and sites
    def dev_list(self):
        patterns = []

        # open the YAML file and load it
        # Need to use 'load_all' where there are multiple documents in a file
        try:
            with open('devices.yaml') as file:
                all_devices = yaml.safe_load_all(file)

                for dev in all_devices:
                    patterns.append(
                        {"label": "SITE", "pattern": dev['site']}
                    )

                    # Need to check if the type is None (an empty entry)
                    # None type will throw an error, so we ignore None entries
                    if dev['devices'] is not None:
                        for device in dev['devices']:
                            patterns.append(
                                {"label": "DEVICE", "pattern": device}
                            )
        except Exception as err:
            print(termcolor.colored(
                "NLP Entity Ruler: Could not load YAML file",
                "red"
            ))
            print(termcolor.colored(
                err,
                "red"
            ))

        return patterns

    # Load custom entities
    def load_ents(self, ent_list):
        patterns = []
        for label in ent_list:
            for ent in ent_list[label]:
                patterns.append(
                    {
                        "label": label.upper(),
                        "pattern": ent
                    }
                )

        return patterns
