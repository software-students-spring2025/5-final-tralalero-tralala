"""
This module handles database operations for the Lost and Found backend.
"""
import os
from datetime import datetime
from bson.objectid import ObjectId

from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt
import requests

load_dotenv()

# MongoDB setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client["lostfound"]
items = db["items"]
users = db["users"]


def geocode_location(location_text):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location_text, "format": "json"}
        headers = {"User-Agent": "LostFoundApp/1.0"}
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        # In production you might log this exception
        pass
    return None, None


def insert_item(data, user_email):
    """
    Insert a new lost item.
    Adds status, timestamps, owner, and geo-coordinates if location provided.
    """
    data["status"] = "lost"
    data["created_at"] = datetime.utcnow().isoformat()
    data["owner"] = user_email

    location = data.get("location")
    if location:
        lat, lon = geocode_location(location)
        if lat is not None and lon is not None:
            data["location_coords"] = {
                "type": "Point",
                "coordinates": [lon, lat],
            }

    return items.insert_one(data)


# def get_all_items(status=None, owner=None):
#     query = {}
#     if status:
#         query["status"] = status
#     if owner:
#         query["owner"] = owner
#     return list(items.find(query, {"_id": 0}))

def get_all_items(status=None, owner=None):
    query = {}
    if status:
        query["status"] = status
    if owner:
        query["owner"] = owner

    items_list = []
    for item in items.find(query):
        item["_id"] = str(item["_id"])  # important!
        items_list.append(item)

    return items_list

def update_item(query, update_fields):
    update_fields["updated_at"] = datetime.utcnow().isoformat()
    return items.update_one(query, {"$set": update_fields})


def delete_item_by_title(title, owner_email):
    return items.delete_many({"title": title, "owner": owner_email})


def delete_item_by_id(item_id, owner_email):
    try:
        return items.delete_one({
            "_id": ObjectId(item_id),
            "owner": owner_email
        })
    except Exception:
        return None


def update_item_by_id(item_id, update_fields, owner_email):
    update_fields["updated_at"] = datetime.utcnow().isoformat()
    try:
        result = items.update_one(
            {"_id": ObjectId(item_id), "owner": owner_email},
            {"$set": update_fields}
        )
        return result.modified_count
    except Exception:
        return None


def create_user(email, username, password):
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = {"email": email, "username": username, "password": hashed}
    return users.insert_one(user)


def find_user_by_email(email):
    return users.find_one({"email": email})


def verify_user(email, password):
    user = find_user_by_email(email)
    if not user:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), user["password"])


__all__ = [
    "insert_item",
    "get_all_items",
    "update_item",
    "delete_item_by_title",
    "delete_item_by_id",
    "update_item_by_id",
    "create_user",
    "find_user_by_email",
    "verify_user",
]
