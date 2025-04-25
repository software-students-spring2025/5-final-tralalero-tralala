# backend/app/main.py

from flask import Flask, request, jsonify, session
from db import *



app = Flask(__name__)
app.secret_key = "supersecret"


@app.route("/items/lost", methods=["POST"])
def submit_lost_item():
    '''
    Allows users to submit entry for a lost item and adds it to the database
    '''
    data = request.get_json()
    insert_item(data)
    return jsonify({"message": "lost item added"}), 201

@app.route("/items", methods=["GET"])
def get_items():
    '''
    Get all items of a given status
    '''
    status = request.args.get("status")
    items = get_all_items(status)
    return jsonify(items), 200

@app.route("/items/<title>", methods=["DELETE"])
def delete_item(title):
    '''
    Delete an entry by title
    '''
    result = delete_item_by_title(title)
    if result.deleted_count > 0:
        return jsonify({"message": f"{result.deleted_count} item(s) deleted"}), 200
    else:
        return jsonify({"error": "No matching items found"}), 404

@app.route("/items/id/<item_id>", methods=["DELETE"])
def delete_item_by_id_route(item_id):
    '''
    Delete an entry by id
    '''
    result = delete_item_by_id(item_id)
    if result and result.deleted_count > 0:
        return jsonify({"message": f"{result.deleted_count} item(s) deleted"}), 200
    else:
        return jsonify({"error": "No matching item found"}), 404

@app.route("/items/id/<item_id>", methods=["PUT"])
def update_item():
    '''
    Update an item by id
    '''
    data = request.get_json()
    modified_count = update_item_by_id(item_id, data)
    if modified_count is None:
        return jsonify({"error": "Invalid item ID"}), 400
    if modified_count == 0:
        return jsonify({"message": "No item updated"}), 404
    return jsonify({"message": "Item updated"}), 200



@app.route("/register", methods=["POST"])
def register():
    '''
    User registration including email, username, and password
    '''
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not all([email, username, password]):
        return jsonify({"error": "Missing fields"}), 400

    create_user(email, username, password)
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    '''
    Enable user login using email and password
    '''
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if verify_user(email, password):
        session["user"] = email
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    '''
    Log the user out by clearing the session
    '''
    session.clear()
    return jsonify({"message": "Logout successful"}), 200

if __name__ == "__main__":
    print("🚀 Flask server running at http://localhost:5001")
    app.run(host="0.0.0.0", port=5001)
