import requests
from flask import current_app

def post_to_linkedin(content):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {current_app.config['LINKEDIN_ACCESS_TOKEN']}"
    }
    post_data = {
        "author": "urn:li:person:{YOUR_LINKEDIN_PERSON_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=post_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error posting to LinkedIn: {response.text}")
        raise Exception(f"Error posting to LinkedIn: {str(e)}")
