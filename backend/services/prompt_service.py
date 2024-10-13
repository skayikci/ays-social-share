from db.mongo import get_db
from bson.objectid import ObjectId
from datetime import datetime
from pymongo import MongoClient
import os
import certifi

class PromptService:
    def __init__(self):
        # Initialize the MongoDB client using the environment variable
        mongo_client = MongoClient(os.environ.get('MONGO_URI'), tlsCAFile=certifi.where())
        self.db = mongo_client.post_generator  # Set your database name
        self.prompts = self.db.prompts  # Set your collection name

    def get_db(self):
        if not self.db:
            self.db = get_db()  # Initialize db only when it's first needed
        return self.db

    def save_prompt(self, prompt):
        """
        Save a new prompt in the database.
        """
        prompt_data = {
            'content': prompt,
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow(),
        }
        return self.db.prompts.insert_one(prompt_data).inserted_id

    def get_latest_prompt(self):
        try:
            prompts = list(self.db['prompts'].find())
            if not prompts:
                return {"message": "No prompts found."}

            # Use datetime.min correctly
            latest_prompt = max(prompts, key=lambda x: x.get('timestamp', datetime.min))

            # Ensure timestamp is in ISO format string
            if isinstance(latest_prompt.get('timestamp'), datetime):
                latest_prompt['timestamp'] = latest_prompt['timestamp'].isoformat()

            # Check if 'content' key exists
            if 'content' not in latest_prompt:
                return {"error": "Latest prompt does not contain 'content'."}

            return latest_prompt

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"error": "An unexpected error occurred."}


    def get_prompt_by_id(self, prompt_id):
        """
        Retrieve a prompt by its ID.
        """
        return self.db.prompts.find_one({'_id': ObjectId(prompt_id)})

    def update_prompt(self, prompt_id, new_content):
        """
        Update the content of an existing prompt.
        """
        return self.db.prompts.update_one(
            {'_id': ObjectId(prompt_id)},
            {'$set': {'content': new_content, 'updated_at': datetime.datetime.utcnow()}}
        )

    def delete_prompt(self, prompt_id):
        """
        Delete a prompt by its ID.
        """
        return self.db.prompts.delete_one({'_id': ObjectId(prompt_id)})

    def get_all_prompts(self):
        """
        Retrieve all prompts (useful for history or list display).
        """
        return list(self.db.prompts.find())
