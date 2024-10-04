from flask import Flask, request, jsonify
import os
from pymongo import MongoClient
import tweepy
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize services
mongo_client = MongoClient(os.environ.get('MONGO_URI'))
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
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": ANTHROPIC_API_KEY,
    }
    data = {
        "prompt": prompt,
        "model": "claude-3-sonnet-20240229",
        "max_tokens_to_sample": 1000,
    }
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/complete",
            headers=headers,
            json=data
        )
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return response.json()['completion']
    except requests.exceptions.RequestException as e:
        print(f"Error calling Anthropic API: {str(e)}")
        if response.status_code == 402:
            return "Error: Insufficient credit in Anthropic account. Please check your account balance."
        return "Error: Unable to generate completion. Please try again later."

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
    for post in posts:
        db.posts.insert_one({
            'content': post,
            'platform': 'twitter' if len(post) <= 280 else 'linkedin',
            'status': 'pending'
        })
    return jsonify({'status': 'success', 'count': len(posts)})

@app.route('/get_pending_posts', methods=['GET'])
def get_pending_posts():
    pending_posts = list(db.posts.find({'status': 'pending'}))
    return jsonify(pending_posts)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)