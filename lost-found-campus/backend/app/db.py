# backend/app/db.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import bcrypt
import requests
from datetime import datetime, timezone


load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["lostfound"]
items = db["items"]

def geocode_location(location_text):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location_text, "format": "json"}
        headers = {"User-Agent": "LostFoundApp/1.0"}  
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
    except:
        pass  
    return None, None

def insert_item(data, user_email):
    data["status"] = "lost"
    data["created_at"] = datetime.utcnow().isoformat()
    data["owner"] = user_email

    location = data.get("location")
    if location:
        lat, lng = geocode_location(location)
        if lat is not None and lng is not None:
            data["location_coords"] = {
                "type": "Point",
                "coordinates": [lng, lat]  
            }

    return items.insert_one(data)

def get_all_items(status=None, owner=None):
    query = {}
    if status:
        query["status"] = status
    if owner:
        query["owner"] = owner
    return list(items.find(query, {"_id": 0}))

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
    except:
        return None
    
def update_item_by_id(item_id, update_fields, owner_email):
    update_fields["updated_at"] = datetime.utcnow().isoformat()
    try:
        result = items.update_one(
            {"_id": ObjectId(item_id), "owner": owner_email},
            {"$set": update_fields}
        )
        return result.modified_count
    except:
        return None
    
users = db["users"]

def create_user(email, username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {
        "email": email,
        "username": username,
        "password": hashed
    }
    return users.insert_one(user)

def find_user_by_email(email):
    return users.find_one({"email": email})

def verify_user(email, password):
    user = find_user_by_email(email)
    if not user:
        return False
    return bcrypt.checkpw(password.encode('utf-8'), user["password"])
    

__all__ = [
    "insert_item",
    "update_item",
    "get_all_items",
    "delete_item_by_title",
    "delete_item_by_id",
    "update_item_by_id",
    "create_user", 
    "verify_user"
]