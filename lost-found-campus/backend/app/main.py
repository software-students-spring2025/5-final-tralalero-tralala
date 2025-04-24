# backend/app/main.py

from flask import Flask, request, jsonify
from db import insert_item

app = Flask(__name__)

@app.route("/items/lost", methods=["POST"])
def submit_lost_item():
    data = request.get_json()
    data["status"] = "lost"
    insert_item(data)
    return jsonify({"message": "lost item added"}), 201

@app.route("/items", methods=["GET"])
def get_all_items():
    from db import get_items  
    items = get_items()
    return jsonify(items), 200


if __name__ == "__main__":
    print("🚀 Flask server running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)


