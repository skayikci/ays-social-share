from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pymongo import MongoClient
import tweepy
import requests
from dotenv import load_dotenv
import anthropic
from dataclasses import dataclass
from typing import List
import certifi
from bson import json_util
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__, static_folder='../frontend/build')
CORS(app)

# Initialize services
mongo_client = MongoClient(os.environ.get('MONGO_URI'), tlsCAFile=certifi.where())
db = mongo_client.post_generator

# Twitter setup
twitter_auth = tweepy.OAuthHandler(
    os.environ.get('TWITTER_API_KEY'),
    os.environ.get('TWITTER_API_SECRET')
)
twitter_auth.set_access_token(
    os.environ.get('TWITTER_ACCESS_TOKEN'),
    os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
)
twitter_api = tweepy.API(twitter_auth)

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
LINKEDIN_ACCESS_TOKEN = os.environ.get('LINKEDIN_ACCESS_TOKEN')

def generate_anthropic_completion(prompt):
    print(prompt)
    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
    )
    try:
        # response = client.messages.create(
        #     model="claude-3-5-sonnet-20240620",
        #     max_tokens=1024,
        #     messages=[
        #         {"role": "user", "content": prompt}
        #     ]
        # )
        # print(response)
        # text_block = response.content[0]
        # print(text_block)
        # return text_block.text
        return "I apologize, but I don't have access to real-time weather information. Weather conditions can change rapidly, and without a current data source, I can't provide you with accurate information about the weather in Hamburg right now.\n\nTo get the most up-to-date and accurate weather information for Hamburg, you could:\n\n1. Check a weather website or app\n2. Look at the local weather forecast for Hamburg\n3. Check the website of the German Weather Service (Deutscher Wetterdienst)\n\nThese sources will give you current conditions, forecasts, and any weather alerts for Hamburg."
    except Exception as e:
        print(f"Error calling Anthropic API: {str(e)}")
        return f"Error: Unable to generate completion. {str(e)}"

def post_to_linkedin(content):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"
    }
    post_data = {
        "author": "urn:li:person:{YOUR_LINKEDIN_PERSON_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    response = requests.post(url, headers=headers, json=post_data)
    if response.status_code != 201:
        raise Exception(f"Error posting to LinkedIn: {response.text}")

@app.route('/api/generate_posts', methods=['POST'])
def generate_posts():
    prompt = request.json['prompt']
    completion = generate_anthropic_completion(prompt)
    if completion.startswith("Error:"):
        return jsonify({'status': 'error', 'message': completion}), 400
    posts = completion.split('\n\n')  # Assuming each post is separated by two newlines
    print('inserting data into db')
    # for post in posts:
    #     db.posts.insert_one({
    #         'content': post,
    #         'platform': 'twitter' if len(post) <= 280 else 'linkedin',
    #         'status': 'pending'
    #     })
    return jsonify({'status': 'success', 'count': len(posts)})

@app.route('/get_pending_posts', methods=['GET'])
def get_pending_posts():
    pending_posts = list(db.posts.find({'status': 'pending'}))
    return json_util.dumps(pending_posts)

@app.route('/update_post', methods=['POST'])
def update_post():
    post_id = request.json['post_id']
    updated_content = request.json['content']
    db.posts.update_one({'_id': post_id}, {'$set': {'content': updated_content}})
    return jsonify({'status': 'success'})

@app.route('/approve_post', methods=['POST'])
def approve_post():
    post_id = request.json['post_id']
    post = db.posts.find_one({'_id': post_id})
    
    if post['platform'] == 'twitter':
        twitter_api.update_status(post['content'])
    elif post['platform'] == 'linkedin':
        post_to_linkedin(post['content'])
    
    db.posts.update_one({'_id': post_id}, {'$set': {'status': 'posted'}})
    return jsonify({'status': 'success'})

@dataclass
class TextBlock:
    text: str
    type: str

@dataclass
class Usage:
    input_tokens: int
    output_tokens: int

@dataclass
class Message:
    id: str
    content: List[TextBlock]
    model: str
    role: str
    stop_reason: str
    stop_sequence: str | None
    type: str
    usage: Usage

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(use_reloader=True, port=8181, threaded=True)