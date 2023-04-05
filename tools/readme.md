# Tools
    Contains stand alone tools to help with the operation of the chatbot

## password_encrypt.py
    Encrypts a password, which can then be stored in the secrets.yaml file
    These passwords are used to connect to remote devices. They are only needed if the chatbot needs to connect to devices
    This script takes a master password, username, and password to encrypt
    The master password is used with a salt to encrypt the password
    It then outputs the details that need to go into the secrets.yaml file
    The master password should be added as a system environment variabled called chat_master_pw


## password_decrypt.py
    This can reverse the encryption on a file
    This requires the encrypted password, the salt that goes with it, and the master password used to encypt it


## phrase-tester.py
    Input phrases, and see what they will evaluate to
    Test different phrase/function/module combinations
    Uses a modified version of nlp.py
