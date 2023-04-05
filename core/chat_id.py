"""
Collects chat_id information from Teams

Usage:
    TBA

Authentication:
    Requires previous authentication with Graph API
    A bearer token is required with each transaction

Restrictions:
    N/A

To Do:
    Move USER to a better place

Author:
    Luke Robertson - February 2023
"""


from config import GRAPH, TEAMS
from core import teamschat
import requests


USER = 'chatbot@my-domain.com'


def get_chats():
    # Make sure authentication is complete first
    full_token = teamschat.check_token()

    # Get a list of active chats
    headers = {
        "Content-Type": "application/json",
        "Authorization": full_token['access_token']
    }
    endpoint = GRAPH['base_url']

    # This paramater is needed to get a username in 1:1 chats
    params = {
        '$expand': 'members'
    }

    response = requests.get(
        url=f"{endpoint}/users/{TEAMS['user']}/chats",
        headers=headers,
        params=params
    )
    response.raise_for_status()

    # Add active chats to a list
    chat_list = []
    for item in response.json()['value']:
        details = {
            'id': item['id'],
            'type': item['chatType'],
        }

        if details['type'] == 'oneOnOne':
            details['name'] = item['members'][1]['displayName']
            details['email'] = item['members'][1]['email']
        else:
            details['name'] = item['topic']
            details['email'] = None

        chat_list.append(details)

    return chat_list
