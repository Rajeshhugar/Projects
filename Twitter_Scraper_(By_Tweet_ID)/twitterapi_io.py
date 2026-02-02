import requests

url = "https://api.twitterapi.io/twitter/tweets"

querystring = {"tweet_ids":"1854026234339938528"}

headers = {"X-API-Key": "810bb9f5b430426ab3a86a2337c80de4"}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())