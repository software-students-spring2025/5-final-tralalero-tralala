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
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    insert_item(data, session["user"])
    return jsonify({"message": "lost item added"}), 201

@app.route("/items", methods=["GET"])
def get_items():
    '''
    Get all items of a given status
    '''
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    status = request.args.get("status")
    owner = session["user"]
    items = get_all_items(status, owner)
    return jsonify(items), 200

@app.route("/items/<title>", methods=["DELETE"])
def delete_item(title):
    '''
    Delete an entry by title
    '''
    result = delete_item_by_title(title, session["user"])
    if result.deleted_count > 0:
        return jsonify({"message": f"{result.deleted_count} item(s) deleted"}), 200
    else:
        return jsonify({"error": "No matching items found"}), 404

@app.route("/items/id/<item_id>", methods=["DELETE"])
def delete_item_by_id_route(item_id):
    '''
    Delete an entry by id
    '''
    result = delete_item_by_id(item_id, session["user"])
    if result and result.deleted_count > 0:
        return jsonify({"message": f"{result.deleted_count} item(s) deleted"}), 200
    else:
        return jsonify({"error": "No matching item found"}), 404

@app.route("/items/id/<item_id>", methods=["PUT"])
def update_item(item_id):
    '''
    Update an item by id
    '''
    data = request.get_json()
    modified_count = update_item_by_id(item_id, data, session["user"])
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
    Enable user login using email and password (supports JSON or form)
    '''
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

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

'''
The following are only for testing purposes.
These are not used in production.
'''
@app.route("/me", methods=["GET"])
def me():
    return jsonify({"session": dict(session)})

@app.route("/test-login-form")
def test_login_form():
    return '''
    <form action="/login" method="post">
        <input name="email" placeholder="Email"><br>
        <input name="password" placeholder="Password" type="password"><br>
        <button type="submit">Login</button>
    </form>
    '''

if __name__ == "__main__":
    print("🚀 Flask server running at http://localhost:5001")
    app.run(host="0.0.0.0", port=5001)
