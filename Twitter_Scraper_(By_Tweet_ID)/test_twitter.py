import requests
 
# Replace with your own Bearer Token from the X Developer Portal
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAADidmgEAAAAA37o1NFfxPnn742tpD9JEi4AppyI%3DXTz1DlYZNM3Ss0ucRP2fbHEhTquwwBaghU4bfFQzrTebBueG3u"
 
# Replace with the Tweet ID you want to fetch
tweet_id = "1518677066325053441"
 
url = f"https://api.x.com/2/tweets/{tweet_id}"
 
headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "User-Agent": "v2TweetLookupPython"
}
 
response = requests.get(url, headers=headers)
 
if response.status_code == 200:
    tweet_data = response.json()
    print("✅ Tweet Data:")
    print(tweet_data)
else:
    print(f"❌ Error {response.status_code}: {response.text}")