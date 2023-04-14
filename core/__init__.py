"""
Core modules for the Network Assistant

Modules
-------
azureauth
    Connects to Microsoft Identity Services API
    Authenticates the app/user, and gets a token

crypto
    Provides cryptographic functions
    Verifies and decrypts Resource Data sent from the Graph API
    Decrypts passwords in the secrets file

hash
    Creates a HMAC hash, to verify the sender of the webhook

nlp
    Natural Language Processor
    Process text input and figure out how to handle it

parse_chats
    Parses messages sent to the chat bot, so it can respond

plugin
    A template class that plugins can inherit
    Includes some default methods that plugins may choose to use

smtp
    Connects to an SMTP server and sends an email

sql
    Creates and reads entries in/from an SQL database

teamschat
    Connects to the Microsoft Graph API, and interacts with MS-Teams chats

"""
