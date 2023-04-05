"""
Loads configuration from a YAML file into a dictionary

Usage:
    from config import GRAPH
    from config import GLOBAL

Authentication:
    N/A - Just needs to be able to read the YAML file

Restrictions:
    Requires the pyyaml module (pip install pyyaml)
    Requires config.yaml to be created and formatted correctly

To Do:
    None

Author:
    Luke Robertson, Richard Chapman - October 2022
"""


import sys
import yaml
import termcolor


# Define the dictionaries we're going to use
GRAPH = {}
GLOBAL = {}
SMTP = {}
TEAMS = {}
LANGUAGE = {}


# Create the empty list of plugins
plugin_list = []


# Open the YAML file, and store in the 'config' variable
with open('config.yaml') as config:
    try:
        config = yaml.load(config, Loader=yaml.FullLoader)
    except yaml.YAMLError as err:
        print(termcolor.colored('Error parsing config file, exiting', "red"))
        print('Check the YAML formatting at \
            https://yaml-online-parser.appspot.com/')
        print(err)
        sys.exit()

# Update our dictionaries with the config
GLOBAL = config['global']
GRAPH = config['graph']
SMTP = config['smtp']
PLUGINS = config['plugins']
TEAMS = config['teams']
LANGUAGE = config['language']
