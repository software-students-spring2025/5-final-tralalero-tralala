# backend/app/main.py

from flask import Flask, request, jsonify, session
from db import *



app = Flask(__name__)
app.secret_key = "supersecret"


@app.route("/items/lost", methods=["POST"])
def submit_lost_item():
    data = request.get_json()
    insert_item(data)
    return jsonify({"message": "lost item added"}), 201

@app.route("/items", methods=["GET"])
def get_items():
    status = request.args.get("status")
    items = get_all_items(status)
    return jsonify(items), 200

@app.route("/items/<title>", methods=["DELETE"])
def delete_item(title):
    result = delete_item_by_title(title)
    if result.deleted_count > 0:
        return jsonify({"message": f"{result.deleted_count} item(s) deleted"}), 200
    else:
        return jsonify({"error": "No matching items found"}), 404

@app.route("/items/id/<item_id>", methods=["DELETE"])
def delete_item_by_id_route(item_id):
    result = delete_item_by_id(item_id)
    if result and result.deleted_count > 0:
        return jsonify({"message": f"{result.deleted_count} item(s) deleted"}), 200
    else:
        return jsonify({"error": "No matching item found"}), 404

@app.route("/items/id/<item_id>", methods=["PUT"])
def update_item():
    data = request.get_json()
    modified_count = update_item_by_id(item_id, data)
    if modified_count is None:
        return jsonify({"error": "Invalid item ID"}), 400
    if modified_count == 0:
        return jsonify({"message": "No item updated"}), 404
    return jsonify({"message": "Item updated"}), 200



@app.route("/register", methods=["POST"])
def register():
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
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if verify_user(email, password):
        session["user"] = email
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    print("🚀 Flask server running at http://localhost:5001")
    app.run(host="0.0.0.0", port=5001)
