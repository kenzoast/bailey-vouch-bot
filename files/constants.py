import json


with open('config.json') as f:
    config = json.load(f)
owner_id = config["owner_id"]
token = config["token"]


BOT_TOKEN = token
BOT_PREFIX = "!"
OWNER_ID = owner_id