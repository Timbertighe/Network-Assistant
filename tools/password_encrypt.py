from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import base64
import getpass
import termcolor

# Get input from the user
print("This script takes a username and password to encrypt, \
    as well as a master password used for then encryption")
username = input("Enter the username: ")
password = getpass.getpass(prompt="Please enter the password to encrypt: ")
master = getpass.getpass(prompt="Enter the master password: ")

# Define a salt and generate a key
salt = os.urandom(16)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000
)
key = base64.urlsafe_b64encode(kdf.derive(master.encode()))

# create a Fernet object using the key
fernet = Fernet(key)

# encrypt the plaintext using AES256 encryption
encrypted_message = fernet.encrypt(password.encode())

print(termcolor.colored(
    "\nYou can add this to your passwords file",
    "green"
))
print(termcolor.colored(
    "my_network_device:",
    'yellow'
))
print(termcolor.colored(
    f"  user: {username}",
    'yellow'
))
print(termcolor.colored(
    f"  salt: {base64.urlsafe_b64encode(salt).decode()}",
    'yellow'
))
print(termcolor.colored(
    f"  secret: {encrypted_message.decode()}",
    'yellow'
))
