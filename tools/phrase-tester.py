"""
Natural Language Processor: Phrase tester

Usage:
    Instantiate the ChatNlp class

Authentication:
    None

Restrictions:
    TBA

To Do:
    TBA

Author:
    Luke Robertson - March 2023
"""

import spacy
import termcolor
import yaml

THRESHOLD = 0.55
MODEL = 'en_core_web_md'


class ChatNlp():
    def __init__(self):
        # Set the similarity threshold
        self.threshold = THRESHOLD

        # Need >= medium model for word vectors
        print(f"Loading spacy {MODEL} model...")
        self.nlp_spacy = spacy.load(MODEL)
        print("done")

        # Create an entity ruler to add custom words
        ruler = self.nlp_spacy.add_pipe("entity_ruler", before="ner")
        patterns = self.dev_list()
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
        phrase_list = [
            {
                "phrase": "juno log",
                "function": "get_logs",
                "module": "plugins.junos.jtac_logs"
            },
            {
                "phrase": "reboot",
                "function": "nlp_reboot",
                "module": "plugins.junos.reboot"
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

        for text in phrase_list:
            self.docs.append(
                {"phrase": self.nlp_spacy(text['phrase']),
                    "function": text['function'],
                    "module": text['module']}
            )

    # Remove stop words, punctuation, and pronouns to improve accuracy
    def cleanup_text(self, text):
        text = text.lower()
        result = []

        # Create a doc with the given text (converted to lower case)
        doc = self.nlp_spacy(text)

        # Remove device names and times
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
        match = {}
        for doc in self.docs:
            similarity = doc['phrase'].similarity(processed_doc)
            if len(match) == 0 or match['similarity'] < similarity:
                match['doc'] = doc
                match['similarity'] = similarity

        print("No match found")
        print(f"\nGiven Text: {text}\n")
        print(f"Cleaned Text: {processed_doc}\n")
        print(f"Closest match: {match['doc']}\n")
        print(f"Closest similarity: {match['similarity']}\n")

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
            # Get the similarity score
            similarity = doc['phrase'].similarity(clean_doc)

            # If there's nothing already in the list, add this in
            if len(similar_list) == 0:
                similar_list = {
                    "nlp_doc": doc['phrase'],
                    "similarity": similarity,
                    "function": doc['function'],
                    "module": doc['module'],
                    "score": similarity
                }

            # If there's already something in the list
            else:
                if similar_list['similarity'] < similarity:
                    similar_list = {
                        "nlp_doc": doc['phrase'],
                        "similarity": similarity,
                        "function": doc['function'],
                        "module": doc['module'],
                        "score": similarity
                    }

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


# Get some input and test the result
def test_input():
    # Get a phrase from the user
    message = input("\nInput: ")
    if message == '':
        return False
    message = message.replace("<p>", "").replace("</p>", "").lower()

    # Run the matcher
    response = chatty.chatbot(message)
    entities = chatty.get_ents(message)

    # Handle bad input
    if response['similarity'] < chatty.threshold:
        print(termcolor.colored("Sorry, I don't understand", "red"))
        print(termcolor.colored(
            f"Closest: {response['function']}() from {response['module']}",
            "red"
        ))

    # Handle good input
    else:
        print(termcolor.colored(
            f"This is {response['function']}() from {response['module']}",
            "green"
        ))

    print(termcolor.colored(
        f"Detected entities: {entities}",
        "yellow"
    ))

    if response['similarity'] >= THRESHOLD:
        print(termcolor.colored(
            f"Similarity: {response['similarity']}",
            "green"
        ))
    else:
        print(termcolor.colored(
            f"Similarity: {response['similarity']}",
            "red"
        ))

    return True


# Instantiate the class
chatty = ChatNlp()

# Repeatedly test phrases until no phrase is given
while test_input():
    pass
