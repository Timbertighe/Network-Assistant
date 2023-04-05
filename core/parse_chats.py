
"""
Parses messages sent to the chat bot, so it can respond

Usage:
    import this module into the application

Authentication:
    None

Restrictions:
    Uses nlp.py

To Do:
    Move get_logs() to the juniper plugin

Author:
    Luke Robertson - March 2023
"""


from core import teamschat
import random
import importlib


jokes = [
    "I went to buy some camo pants but couldn't find any.",
    "I want to die peacefully in my sleep, like my grandfather… Not screaming \
        and yelling like the passengers in his car.",
    "It takes a lot of balls to golf the way I do.",
    "My father has schizophrenia, but he's good people.",
    "The easiest time to add insult to injury is when you're signing \
        someone's cast.",
    "Two fish are in a tank. One says, 'How do you drive this thing?'",
    "The problem isn't that obesity runs in your family. It's that no one \
        runs in your family.",
    "I got a new pair of gloves today, but they're both 'lefts,' which on the \
        one hand is great, but on the other, it's just not right.",
    "Two wifi engineers got married. The reception was fantastic.",
    "A dung beetle walks into a bar and asks, 'Is this stool taken?'",
    "I buy all my guns from a guy called T-Rex. He's a small arms dealer.",
    "A Freudian slip is when you say one thing and mean your mother.",
    "How do you get a country girl's attention? A tractor.",
    "What do you call a pudgy psychic? A four-chin teller.",
    "My wife asked me to stop singing “Wonderwall” to her. I said maybe...",
    "Dogs can't operate MRI machines. But catscan.",
    "What kind of music do chiropractors like? Hip pop.",
    "I signed up for a marathon, but how will I know if it's the real deal \
        or just a run through?",
    "When life gives you melons, you might be dyslexic.",
    "I spent a lot of time, money, and effort childproofing my house… \
        But the kids still get in.",
    "The man who survived both mustard gas and pepper spray is a \
        seasoned veteran now.",
    "Dark jokes are like food. Not everyone gets it",
    "I stayed up all night wondering where the sun went, then it dawned on me",
    "I asked my date to meet me at the gym today. She didn't show up. \
        That's when I knew we weren't gonna work out.",
    "What's Blonde and dead in a closet? The Hide and Seek Champion \
        from 1995.",
    "The CEO of IKEA was elected Prime Minister in Sweden. He should have his \
        cabinet together by the end of the weekend.",
    "The problem with trouble shooting is that trouble shoots back.",
    "My boss is going to fire the employee with the worst posture. I have a \
        hunch, it might be me.",
    "Two windmills are standing in a field and one asks the other, \
        \"What kind of music do you like?\" The other says \
        \"I'm a big metal fan.\"",
    "A courtroom artist was arrested today for an unknown reason... \
        details are sketchy.",
    "I just found out I'm colorblind. The diagnosis came completely \
        out of the purple.",
    "I saw an ad for burial plots, and thought to myself this is the \
        last thing I need.",
    "My dad died when we couldn't remember his blood type. As he died, \
        he kept insisting for us to \"be positive,\" \
        but it's hard without him.",
    "I'm glad I know sign language, it's pretty handy.",
    "I gave up my seat to a blind person in the bus. That is how I lost \
        my job as a bus driver.",
    "How did I escape Iraq? Iran.",
    "A clean house is the sign of a broken computer.",
    "You know you're ugly when it comes to a group picture and they \
        hand you the camera.",
    "My driving instructor told me to pull over somewhere safe. \
        After 10 minutes he asked me why I hadn't pulled over. \
            I said we are still in Windale",
    "My girlfriend is always stealing my t-shirts and sweaters... \
        But if I take one of her dresses, suddenly \"we need to talk\".",
    "A computer once beat me at chess, but it was no match for me at \
        kick boxing.",
    "Two wrongs don't make a right, take your parents as an example.",
    "What's the difference of deer nuts and beer nuts? Beer nuts are \
        a $1.75, but deer nut are under a buck."
]


# Functions to respond to known phrases
def tell_joke(chat_id, **kwargs):
    teamschat.send_chat(random.choice(jokes), chat_id)


def greeting(chat_id, **kwargs):
    teamschat.send_chat("How are you today?", chat_id)


def get_weather(chat_id, **kwargs):
    teamschat.send_chat("It's rainy!", chat_id)


def are_you_human(chat_id, **kwargs):
    teamschat.send_chat("I am a prototype NLP chatbot", chat_id)


def day_time(chat_id, **kwargs):
    teamschat.send_chat("It's today of course", chat_id)


# Take a given chat message, and decide what to do with it
def parse(message, chat_nlp, chat_id):
    message = message.replace("<p>", "").replace("</p>", "").lower()
    response = chat_nlp.chatbot(message)
    entities = chat_nlp.get_ents(message)

    # Call a handler function, as long as the input makes sense
    if response is None:
        teamschat.send_chat("Sorry, I don't understand", chat_id)
    else:
        # If the module is 'global', just set the function as returned
        if response['module'] == 'global':
            function = globals()[response['function']]

        # If the module is a plugin, import the module and set the function
        else:
            module = importlib.import_module(response['module'])
            function = getattr(module, response['function'])

        function(chat_id, ents=entities, message=message)
