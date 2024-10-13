from pymongo import MongoClient
import certifi
import os
from flask import current_app

def get_db():
    """Returns a MongoDB client instance."""
    client = MongoClient(current_app.config['MONGO_URI'], tlsCAFile=certifi.where())
    return client.post_generator
