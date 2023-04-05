from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
import getpass

# Get input from the user
print("This script decrypts a password from the passwords file")
salt = input("Enter the salt value: ")
encrypted_password = input("Please enter the encrypted password (secret): ")
master = getpass.getpass(prompt="Enter the master password: ")


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
decrypted_password = fernet.decrypt(
    encrypted_password.encode()
).decode('utf-8')

print('Decrypted plaintext:', decrypted_password)
