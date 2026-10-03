from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


@app.route("/")
def home():
    return "Portfolio Backend is running!"


@app.route("/api/hero", methods=["GET"])
def get_hero():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, description, image_url FROM hero_content LIMIT 1")
    hero = cur.fetchone()

    cur.close()
    conn.close()

    if hero:
        return jsonify({
            "id": hero[0],
            "name": hero[1],
            "description": hero[2],
            "image_url": hero[3]
        })

    return jsonify({
        "message": "No hero content found"
    }), 404


@app.route("/api/hero", methods=["PUT"])
def update_hero():
    data = request.json

    name = data.get("name")
    description = data.get("description")
    image_url = data.get("image_url")

    if not name or not description or not image_url:
        return jsonify({
            "error": "All fields are required"
        }), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM hero_content LIMIT 1")
    existing = cur.fetchone()

    if existing:
        cur.execute("""
            UPDATE hero_content
            SET name = %s,
                description = %s,
                image_url = %s
            WHERE id = %s
        """, (name, description, image_url, existing[0]))
    else:
        cur.execute("""
            INSERT INTO hero_content (name, description, image_url)
            VALUES (%s, %s, %s)
        """, (name, description, image_url))

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "message": "Hero content updated successfully!"
    })


if __name__ == "__main__":
    app.run(debug=True)