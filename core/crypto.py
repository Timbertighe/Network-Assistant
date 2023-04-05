"""
Provides cryptographic functions
    Verifies and decrypts Resource Data sent from the Graph API
    Decrypts passwords in the secrets file

Modules:
    3rd Party: Crypto, cryptography, base64, hmac, hashlib, json, pycryptodome
        termcolor, yaml, os, re
    Custom: config

Classes:

    None

Functions

    rsa_decrypt()
        Uses a private key to decrypt a message and extract the symmetric key
    validate()
        Validate the Graph API signature
    aes_decrypt()
        Decrypt the body of a Teams message (encryptes symmetrically with AES)
    pw_decrypt()
        Decrypt passwords from the secrets file

Exceptions:

    None

Misc Variables:

    None

Limitations:
    Requires a public/private key to be available (PEM format)

Author:
    Luke Robertson - April 2023
"""


from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import unpad
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
from base64 import b64decode, b64encode
import hmac
import hashlib
import json
import termcolor
import yaml
import os
import re
from config import TEAMS, GLOBAL


# Decrypt the encrypted symmetric key
def rsa_decrypt(encrypted_symmetric_key):
    '''
    Decrypts the encrypted session key, as sent from Graph API.
    Assumes that no passphrase is needed to use the private key
    Returns the decrypted key

        Parameters:
            encrypted_symmetric_key : str
                The encrypted key Graph included in the webhook

        Raises:
            Exception
                When the private key file could not be opened

        Returns:
            decrypted_symmetric_key : str
                The decrypted symmetric key
            False : Boolean
                If there was some error
    '''

    # Read the private key as raw text
    # the 'PRIVATE KEY' tags need to exist in the PEM file
    try:
        with open(TEAMS['private_key'], 'r') as file:
            private_key = file.read()

    except Exception:
        print(termcolor.colored("Could not read the local private key", "red"))
        return False

    # Imports the private key into an 'RsaKey' object
    # Assumes no passphrase is needed
    rsa_key = RSA.import_key(private_key)
    rsa_modulus = rsa_key.n.bit_length() / 8

    # PKCS#1 OAEP is an asymmetric cipher based on RSA with OAEP Padding
    # This can only handle messages smaller than the RSA modulus
    # Create a cipher object that encrypts/decrypts based on the RSA key
    rsa_cipher = PKCS1_OAEP.new(rsa_key)

    # The symmetric key and data from the Graph API is Base64 encoded
    # This decodes both into raw bytes
    # We also need to know how long the symmetric key is
    encrypted_symmetric_key = b64decode(encrypted_symmetric_key)
    symmetric_length = len(encrypted_symmetric_key)

    # The OAEP cipher can only decrypt blocks <= the RSA modulus size
    # If they symmetric key < RSA modulus, just decrypt it
    if symmetric_length < rsa_modulus:
        decrypted_symmetric_key = rsa_cipher.decrypt(encrypted_symmetric_key)

    # If they symmetric key > RSA modulus, break it into blocks,
    #   and decode each individually
    # Each block must be the size of the RSA modulus
    else:
        # The position (block number) in the encrypted string
        offset = 0

        # A list to store decrypted blocks
        blocks = []

        # Loop through each block (256-bit for a 2048-bit RSA key)
        while symmetric_length - offset > 0:
            # Check if there is more than one block remaining
            if symmetric_length - offset > rsa_modulus:
                blocks.append(
                    rsa_cipher.decrypt(
                        encrypted_symmetric_key[offset:offset + rsa_modulus]
                    )
                )

            # If there's just one block left
            else:
                blocks.append(
                    rsa_cipher.decrypt(encrypted_symmetric_key[offset:])
                )

            # Move to the next block (if there is one) and repeat
            offset += rsa_modulus

        # 'blocks' is a list of decrypted blocks
        # Join them into one single value
        decrypted_symmetric_key = b''.join(blocks)

    # Return the decrypted AES key
    return decrypted_symmetric_key


# Validate the Graph API webhook is authentic
def validate(decrypted_symmetric_key, data, signature):
    '''
    Validate that the message sent from Graph API has not been tampered with
    Takes the signature from Graph API (HMAC-SHA256)
    Generates a local signature based on the encrypted webhook
    Compares the two for a match

        Parameters:
            decrypted_symmetric_key : str
                The AES key, previously decrypted
            data : str
                The encrypted data from the webhook
            signature : str
                The crypto signature provided by Graph API

        Raises:
            none

        Returns:
            True : Boolean
                If the validation was successful
            False : Boolean
                If the validation failed
    '''

    # Calculate a local HMAC-SHA256 hash digest of the encrypted data
    # The encrypted data is base64 encoded, and needs to be decoded
    local_hash = hmac.new(
        decrypted_symmetric_key,
        msg=b64decode(data),
        digestmod=hashlib.sha256
    ).digest()
    local_hash = b64encode(local_hash).decode()

    # Check if the signatures match
    if local_hash == signature:
        return True
    else:
        return False


# Decrypt the body of the message
def aes_decrypt(decrypted_symmetric_key, data):
    '''
    Decrypts the body of the message that Graph API sent
    Returns the decrypted data in JSON form

        Parameters:
            decrypted_symmetric_key : str
                The AES key, previously decrypted
            data : str
                The encrypted data from the webhook

        Raises:
            none

        Returns:
            decrypted_payload : str
                The decrypted data
    '''

    # Decrypt the contents of the message
    # The Initialization Vector (IV) is the first 16-bytes of the symmetric key
    # Cipher is AES, PKCS7, mode is CBC
    iv = decrypted_symmetric_key[:16]
    aes_cipher = AES.new(decrypted_symmetric_key, AES.MODE_CBC, iv=iv)

    # Decrypt the payload (block size is 16)
    # Remove AES padding
    decrypted_payload = unpad(
        aes_cipher.decrypt(
            b64decode(data)
        ),
        block_size=16
    ).decode()
    decrypted_payload = json.loads(decrypted_payload)

    return decrypted_payload


# Retrieve a username/password for a device
def pw_decrypt(dev_type, device):
    '''
    Retrieves an encrypted password for a device from the secrets file
    Decrypts password, using the master password in an environment variable

        Parameters:
            dev_type : str
                The type of device (eg, junos, cisco, server)
            device : device
                The device name

        Raises:
            Exception
                If the secrets file cannot be opened

        Returns:
            decrypted payload : dict
                'user' - The user to log on to this device
                'decrypted password' - The password
            False : boolean
                If there was a problem decrypting the password
    '''

    # Open the secrets file
    secrets = ''
    try:
        with open(GLOBAL['secrets_file']) as file:
            yaml_docs = yaml.safe_load_all(file)

            for dev in yaml_docs:
                if dev['type'] == dev_type:
                    secrets = dev
                    break

    except Exception as err:
        print(termcolor.colored("Could not load YAML file", "red"))
        print(termcolor.colored(err, "red"))
        return False

    # Handle error if device type is not present
    if secrets == '':
        print(termcolor.colored(
            f"Could not find {dev_type} in secrets file",
            "red"
        ))
        return False

    # Find entry and handle error if device is not present
    found = False
    for entry in secrets:
        if re.search(entry, device):
            found = True
            user = secrets[entry]['user']
            salt = secrets[entry]['salt']
            encrypted_password = secrets[entry]['secret']
            break

    if not found:
        return False

    # Get master PW from env variable
    master = os.getenv('chat_master_pw')

    # generate a key using PBKDF2HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=base64.urlsafe_b64decode(salt.encode()),
        iterations=100000
    )
    key = base64.urlsafe_b64encode(kdf.derive(master.encode()))

    # create a Fernet object using the key
    fernet = Fernet(key)

    # decrypt the encrypted message using the same key
    try:
        decrypted_password = fernet.decrypt(
            encrypted_password.encode()
        ).decode('utf-8')

    except Exception as err:
        print(termcolor.colored(
            f"Unable to decrypt the password for {user}",
            "red"
        ))
        print(err)
        return False

    # Return decrypted password
    return {
        'user': user,
        'password': decrypted_password
    }
