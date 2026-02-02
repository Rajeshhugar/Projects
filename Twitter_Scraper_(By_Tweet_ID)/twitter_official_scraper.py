import tweepy
import json
import time

# ----------------------------
# Replace these with your own keys from the Twitter Developer Portal:
# https://developer.x.com/en/portal/dashboard
# ----------------------------
API_KEY = "DGbNJfGZPFHyVKrCxDBWuRGzy"
API_KEY_SECRET = "6oaZWW9dMMSr2zDtt4mgoGB1TLhbJYnuci8BQDqJ10zjuy9UlR"
ACCESS_TOKEN = "971279896692523008-rIXV4moOrsbvaMF4SuIRt6rqzm2Vfbk"
ACCESS_TOKEN_SECRET = "XmcE9OPUxDaHx1JdtREzWB7bKyA1E6BdeZaWqe3xDZgUe"

# Authenticate via OAuth 1.0a (user context)
auth = tweepy.OAuth1UserHandler(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Initialize Tweepy Client (OAuth 2.0 user context)
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Example Tweet ID
tweet_id = "1820685675899072930"

def get_tweet_data_oauth(tweet_id):
    """Fetch a tweet’s full data (all tweet fields) using OAuth user context."""
    tweet_fields = [
        "attachments",
        "author_id",
        "context_annotations",
        "conversation_id",
        "created_at",
        "edit_controls",
        "edit_history_tweet_ids",
        "entities",
        "geo",
        "id",
        "in_reply_to_user_id",
        "lang",
        "non_public_metrics",
        "organic_metrics",
        "possibly_sensitive",
        "promoted_metrics",
        "public_metrics",
        "referenced_tweets",
        "reply_settings",
        "source",
        "text",
        "withheld"
    ]

    while True:
        try:
            response = client.get_tweet(
                id=tweet_id,
                tweet_fields=tweet_fields,
                user_auth=True  # 👈 important — uses OAuth user context
            )
            return response
        except tweepy.TooManyRequests as e:
            reset_time = int(e.response.headers.get("x-rate-limit-reset", time.time() + 900))
            sleep_time = max(reset_time - int(time.time()), 60)
            print(f"⏳ Rate limit hit. Sleeping for {sleep_time//60} minutes...")
            time.sleep(sleep_time)
        except Exception as e:
            print(f"⚠️ Error fetching tweet {tweet_id}: {e}")
            return None

# Fetch tweet
response = get_tweet_data_oauth(tweet_id)

# Print data
if response and response.data:
    print(json.dumps(response.data, indent=2, default=str))
else:
    print("❌ Tweet not found or you don’t have access.")
