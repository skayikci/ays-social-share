import tweepy
from flask import current_app

def get_twitter_api():
    auth = tweepy.OAuthHandler(
        current_app.config['TWITTER_API_KEY'],
        current_app.config['TWITTER_API_SECRET']
    )
    auth.set_access_token(
        current_app.config['TWITTER_ACCESS_TOKEN'],
        current_app.config['TWITTER_ACCESS_TOKEN_SECRET']
    )
    return tweepy.API(auth)

def post_to_twitter(content):
    try:
        twitter_api = get_twitter_api()
        twitter_api.update_status(content)
    except tweepy.TweepError as e:
        current_app.logger.error(f"Error posting to Twitter: {e}")
        raise Exception(f"Error posting to Twitter: {str(e)}")
