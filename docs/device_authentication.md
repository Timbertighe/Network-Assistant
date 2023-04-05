# Device Authentication
    Plugins within the chatbot may connect to remote devices to perform certain tasks
    These devices would normally require a username and password, or similar authentication
    This is privilleged information, which needs to be kept secure
  
### Overview
    The 'secrets.yaml' file, in the 'core' folder, contains encrypted authentication details
    When making connections to devices, plugins can refer to this file to get the required authentication details
    The passwords are encypted with AES256 encryption, and each one uses a salt
    
### secrets.yaml
    The 'secrets.yaml' file contains several YAML documents.
    These documents are user definable, and are used to collect similar device types together.
    For example, a doc could be arranged by a vendor (eg, Juniper or Cisco), a device type (eg, router or switch), or by site name
    Each document begins with a 'type' field, which is the name of the document
    
    Within each document we have a list of devices or services. Underneath each device are three values:
      * user - The username for this device/service
      * salt - The salt that goes with the encrypted password
      * secret - The encrypted password
      
    Each device can be listed individually, or regex may be used
    
### Adding Credentials
    The standalone script 'password_encrypt.py' (in the 'tools' folder) has been provided to encrypt passwords
    Run this script and follow the prompts. You will be prompted for:
      * A username
      * The password that goes with the username (the one to be encrypted and stored in the secrets file)
      * A master password
      
    The script will output some YAML code, which can then be copied into the secrets file
    
    The 'password_decrypt.py' script can be used to decrypt passwords for troubleshooting purposes
      
### Master Password
    The master password is used to encrypt all the passwords that go in the secrets file
    This password should be long, secure, and not used for other purposes
    
    This should is installed in a system environment variable called 'chat_master_pw'
        (as of version 0.8, this has been tested in Windows, but not Linux)
    A privileged user on the system will be able to read this password, while other users will not
    
### Decryption
    The pw_decrypt() function in the crypto.py file decrypts passwords as they're needed (not on startup)
    This will search through the YAML file for the given document type, and then search for the device
    NOTE: Matching is top-down, so put the more specific entries at the top of the file
    Once it's found a corresponding entry, it uses the salt in the secrets file, along with the master password in the environment variable, to decrypt the password
    It will return the username and password to the calling function



    

