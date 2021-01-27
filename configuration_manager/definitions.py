import os

"""This file contains the definitions for the constants
such as the paths to different directories, files, etc.
used in different classes.
"""

# Path to the project root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Path to the configuration file
CONFIG_FILE = os.path.join(ROOT_DIR, 'configuration_settings.xml')
# Path to the outputs directory
OUTPUT_DIR = os.path.join(ROOT_DIR, 'outputs')
