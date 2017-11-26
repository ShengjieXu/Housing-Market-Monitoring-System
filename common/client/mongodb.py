# -*- coding: utf-8 -*-

"""MongoDB client"""

import json
import os

from pymongo import MongoClient

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
with open(CONFIG_FILE) as json_config_file:
    CONFIG = json.load(json_config_file)

DB_URI = CONFIG["mongodb"]["uri"]
DB_NAME = CONFIG["mongodb"]["name"]

CLIENT = MongoClient(DB_URI)


def get_db(database_name=DB_NAME):
    """get database"""

    database = CLIENT[database_name]
    return database
