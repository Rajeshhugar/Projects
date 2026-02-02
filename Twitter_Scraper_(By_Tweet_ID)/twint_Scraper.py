import twint
import json

c = twint.Config()
c.Search = ""
c.Store_json = True
c.Custom["user"] = ["id", "tweet", "user_id", "username", "hashtags", "mentions"]
c.User_full = True
c.Output = "tweets.json"
c.Since = "2019-05-20"
c.Hide_output = True

twint.run.Search(c)