"""
NLP personality module

Provides functions for a more human-like response

Modules:
    3rd Party: random, datetime
    Custom: teamschat

Classes:

    None

Functions

    TBA

Exceptions:

    None

Misc Variables:

    None

Limitations/Requirements:

    None

Author:
    Luke Robertson - April 2023
"""


import random
from datetime import datetime

from core import teamschat


# A list of jokes to tell the user


def tell_joke(chat_id, **kwargs):
    '''
    Selects a random joke to send to the user

        Parameters:
            chat_id : str
                The teams chat ID to respond to

        Raises:
            None

        Returns:
            None
    '''

    jokes = [
        "I went to buy some camo pants but couldn't find any.",
        "I want to die peacefully in my sleep, like my grandfather… Not \
            screaming and yelling like the passengers in his car.",
        "It takes a lot of balls to golf the way I do.",
        "My father has schizophrenia, but he's good people.",
        "The easiest time to add insult to injury is when you're signing \
            someone's cast.",
        "Two fish are in a tank. One says, 'How do you drive this thing?'",
        "The problem isn't that obesity runs in your family. It's that no one \
            runs in your family.",
        "I got a new pair of gloves today, but they're both 'lefts,' which on \
            the one hand is great, but on the other, it's just not right.",
        "Two wifi engineers got married. The reception was fantastic.",
        "A dung beetle walks into a bar and asks, 'Is this stool taken?'",
        "I buy all my guns from a guy called T-Rex. He's a small arms dealer.",
        "A Freudian slip is when you say one thing and mean your mother.",
        "How do you get a country girl's attention? A tractor.",
        "What do you call a pudgy psychic? A four-chin teller.",
        "My wife asked me to stop singing “Wonderwall” to her. \
            I said maybe...",
        "Dogs can't operate MRI machines. But catscan.",
        "What kind of music do chiropractors like? Hip pop.",
        "I signed up for a marathon, but how will I know if it's the \
            real deal or just a run through?",
        "When life gives you melons, you might be dyslexic.",
        "I spent a lot of time, money, and effort childproofing my house… \
            But the kids still get in.",
        "The man who survived both mustard gas and pepper spray is a \
            seasoned veteran now.",
        "Dark jokes are like food. Not everyone gets it",
        "I stayed up all night wondering where the sun went, \
            then it dawned on me",
        "I asked my date to meet me at the gym today. She didn't show up. \
            That's when I knew we weren't gonna work out.",
        "What's Blonde and dead in a closet? The Hide and Seek Champion \
            from 1995.",
        "The CEO of IKEA was elected Prime Minister in Sweden. He should have \
            his cabinet together by the end of the weekend.",
        "The problem with trouble shooting is that trouble shoots back.",
        "My boss is going to fire the employee with the worst posture. \
            I have a hunch, it might be me.",
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
    ]

    teamschat.send_chat(random.choice(jokes), chat_id)


def greeting(chat_id, **kwargs):
    '''
    Greets the user

        Parameters:
            chat_id : str
                The teams chat ID to respond to

        Raises:
            None

        Returns:
            None
    '''

    responses = [
        'How are you today?',
        'Hi',
        'Good morning! Or is it afternoon?',
        'Hi there',
        'Good to see you',
        'G\'day',
        'Yo!',
        'What\'s up'
    ]
    teamschat.send_chat(random.choice(responses), chat_id)


def are_you_human(chat_id, **kwargs):
    '''
    Tells the user a bit about itself

        Parameters:
            chat_id : str
                The teams chat ID to respond to

        Raises:
            None

        Returns:
            None
    '''

    responses = [
        'I am a prototype NLP chatbot',
        'I am a friendly network assistant',
        'I am a chatbot, but you can still talk to me',
        'A robot I guess. I can tell jokes 😄'
    ]

    teamschat.send_chat(random.choice(responses), chat_id)


def day_time(chat_id, **kwargs):
    '''
    Gets the time and day for the user

        Parameters:
            chat_id : str
                The teams chat ID to respond to

        Raises:
            None

        Returns:
            None
    '''

    # Get time info
    now = datetime.now()
    time = now.strftime("%H:%M")
    day_name = now.strftime("%A")
    month = now.strftime("%B")
    ampm = now.strftime("%p")

    # Get the day number
    today = datetime.today().date()
    day = today.strftime("%d")
    if day[0] == '0':
        day = day.replace("0", "")

    # Handle 1st, 2nd, 3rd, *th
    if day == '1':
        day_str = '1st'
    elif day == '2':
        day_str = '2nd'
    elif day == '3':
        day_str = '3rd'
    else:
        day_str = f"{day}th"

    teamschat.send_chat(
        f"It is {time}{ampm} on {day_name} the {day_str} of {month}",
        chat_id
    )


def thank(chat_id, **kwargs):
    '''
    Responds to the user thanking the chatbot

        Parameters:
            chat_id : str
                The teams chat ID to respond to

        Raises:
            None

        Returns:
            None
    '''

    responses = [
        'You\'re welcome!',
        'No problem',
        'Glad it was helpful',
        'Any time!',
        'You are most welcome',
        'For you, anything',
        'Don\'t mention it',
        'I\'m happy to have been of assistance',
        'no worries, time for a beer'
    ]
    teamschat.send_chat(random.choice(responses), chat_id)
