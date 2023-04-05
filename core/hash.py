
"""
Creates a HMAC hash, to verify the sender of the webhook

Usage:
    import this module into the application

Authentication:
    Webhooks can be sent with a secret, which authenticates the source
    No authentication required to access functions in this module

Restrictions:
    None

To Do:
    None

Author:
    Luke Robertson - March 2022
"""


import hmac
import hashlib


# Authenticate if a message was genuine
# HMAC_SHA256(secret, body)
# Take the secret (as a string) and the complete webhook message
def auth_message(header, secret, webhook):
    '''
    Takes a secret, and the webook sent by a plugin
    Creates a hash of the secret and webhook body (HMAC SHA256)
    and compares the result
    '''

    # Check that the signature is in the header
    if header in webhook.headers:
        # Get the message body
        data = webhook.get_data()

        # Get the hash that was sent
        sender_hash = webhook.headers[header]

        # Generate our own hash
        hash = hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()

        # Compare the sender's hash with our hash
        if sender_hash == hash:
            return ('success')
        else:
            return ('fail')

    # If the signature wasn't sent, report it
    else:
        return ('unauthenticated')
