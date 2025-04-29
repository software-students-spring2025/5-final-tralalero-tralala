# backend/app/main.py

import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from .db import (
    insert_item,
    get_all_items,
    delete_item_by_title,
    delete_item_by_id,
    update_item_by_id,
    create_user,
    verify_user,
)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecret")

CORS(app, supports_credentials=True)

@app.route("/items/lost", methods=["POST"])
def submit_lost_item():
    """Submit a new lost-item entry (protected)."""
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    insert_item(data, session["user"])
    return jsonify({"message": "Lost item added"}), 201


@app.route("/items", methods=["GET"])
def get_items():
    """List items filtered by optional status (protected)."""
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    status = request.args.get("status")
    owner = session["user"]
    items = get_all_items(status=status, owner=owner)
    return jsonify(items), 200


@app.route("/items/<title>", methods=["DELETE"])
def delete_item(title):
    result = delete_item_by_title(title, session.get("user"))
    if result.deleted_count > 0:
        return jsonify({"message": f"{result.deleted_count} item(s) deleted"}), 200

    return jsonify({"error": "No matching items found"}), 404


@app.route("/items/id/<item_id>", methods=["DELETE"])
def delete_item_by_id_route(item_id):
    result = delete_item_by_id(item_id, session.get("user"))
    if result and result.deleted_count > 0:
        return jsonify({"message": f"{result.deleted_count} item(s) deleted"}), 200

    return jsonify({"error": "No matching item found"}), 404


@app.route("/items/id/<item_id>", methods=["PUT"])
def update_item_route(item_id):
    data = request.get_json()
    modified_count = update_item_by_id(item_id, data, session.get("user"))

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
    data = request.get_json() if request.is_json else request.form
    email = data.get("email")
    password = data.get("password")

    if verify_user(email, password):
        session["user"] = email
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200


# Endpoints for testing only (not for production)
@app.route("/me", methods=["GET"])
def me():
    """Return current session for debugging."""
    return jsonify({"session": dict(session)}), 200


@app.route("/test-login-form")
def test_login_form():
    return """
    <form action="/login" method="post">
        <input name="email" placeholder="Email"><br>
        <input name="password" placeholder="Password" type="password"><br>
        <button type="submit">Login</button>
    </form>
    """


if __name__ == "__main__":
    print("🚀 Flask server running at http://localhost:5001")
    app.run(host="0.0.0.0", port=5001)
