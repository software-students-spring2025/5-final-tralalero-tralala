# backend/app/db.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["lostfound"]
items = db["items"]

def insert_item(data):
    return items.insert_one(data)

def get_items():
    return list(items.find({}, {"_id": 0}))



def get_all_items(status=None):
    query = {}
    if status:
        query["status"] = status
    return list(items.find(query))
