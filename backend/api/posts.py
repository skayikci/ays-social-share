from flask import Blueprint, request, jsonify
from db.mongo import get_db
from models.post import Post
from validators.post_validator import PostSchema
from api.twitter import post_to_twitter
from api.linkedin import post_to_linkedin
from api.anthropic import generate_anthropic_completion
from datetime import datetime
from bson import json_util
from bson.objectid import ObjectId


posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/generate_posts', methods=['POST'])
def generate_posts():
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({'status': 'error', 'message': 'Prompt is required'}), 400

    completion = generate_anthropic_completion(prompt)
    if completion.startswith("Error:"):
        return jsonify({'status': 'error', 'message': completion}), 400
    
    posts = completion.split('\n\n')  # Assuming posts are split by two newlines
    db = get_db()
    
    for content in posts:
        platform = 'twitter' if len(content) <= 280 else 'linkedin'
        post = Post(content=content, platform=platform)
        db.posts.insert_one(post.__dict__)
    
    return jsonify({'status': 'success', 'count': len(posts)})

@posts_bp.route('/approve_post', methods=['POST'])
def approve_post():
    post_id = request.json.get('post_id')
    db = get_db()
    post = db.posts.find_one({'_id': ObjectId(post_id)})

    if not post:
        return jsonify({'status': 'error', 'message': 'Post not found'}), 404

    if post['platform'] == 'twitter':
        post_to_twitter(post['content'])
    elif post['platform'] == 'linkedin':
        post_to_linkedin(post['content'])
    
    db.posts.update_one({'_id': ObjectId(post_id)}, {'$set': {'status': 'posted'}})
    return jsonify({'status': 'success'})

@posts_bp.route('/grouped', methods=['GET'])
def get_grouped_posts():
    try:
        db = get_db()
        posts = list(db.posts.find({'status': 'pending'}))
        grouped_posts = {}

        for post in posts:
            # Use a default date if timestamp is missing
            timestamp = post.get('timestamp', datetime.now())
            day = timestamp.strftime('%A')
            platform = post['platform']
            content = post['content']
            post_id = str(post['_id'])  # Convert ObjectId to string

            if day not in grouped_posts:
                grouped_posts[day] = {}
            
            if platform not in grouped_posts[day]:
                grouped_posts[day][platform] = []
            
            # Append both content and id in a dictionary
            grouped_posts[day][platform].append({
                'id': post_id,
                'content': content
            })

        return json_util.dumps(grouped_posts)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }), 500



@posts_bp.route('<post_id>', methods=['PUT'])
def update_prompt(post_id):
    """
    Endpoint to update a prompt's content.
    """
    new_content = request.json.get('content')
    db = get_db()
    print('writing to db: ' , new_content)
    if not new_content:
        return jsonify({'status': 'error', 'message': 'New content is required'}), 400
    
    result = db.posts.update_one({'_id': ObjectId(post_id)}, {'$set': {'content': new_content['content']}})
    if result.matched_count == 0:
        return jsonify({'status': 'error', 'message': 'Prompt not found'}), 404
    
    return jsonify({'status': 'success', 'message': 'Prompt updated successfully'})
