from flask import Flask, jsonify, request, send_from_directory 
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
import boto3
import os
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)


def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


@app.route("/")
def home():
    return "Portfolio Backend is running!"
@app.route("/admin.html")
def admin():
    return send_from_directory("../", "admin.html")


@app.route("/api/hero", methods=["GET"])
def get_hero():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, description, image_url FROM hero_content LIMIT 1"
    )
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
    name = request.form.get("name")
    description = request.form.get("description")
    image = request.files.get("image")

    if not name or not description:
        return jsonify({
            "error": "Name and description are required"
        }), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, image_url FROM hero_content LIMIT 1")
    existing = cur.fetchone()

    image_url = existing[1] if existing else ""

    # Upload new image to S3 if a file was selected
    if image:
        file_extension = os.path.splitext(image.filename)[1].lower()

        if file_extension not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            cur.close()
            conn.close()
            return jsonify({
                "error": "Only JPG, JPEG, PNG, GIF and WEBP images are allowed"
            }), 400

        unique_filename = f"hero/{uuid.uuid4()}{file_extension}"

        s3.upload_fileobj(
            image,
            S3_BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                "ContentType": image.content_type
            }
        )

        image_url = (
            f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/"
            f"{unique_filename}"
        )

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
        "message": "Hero content updated successfully!",
        "image_url": image_url
    })


if __name__ == "__main__":
    app.run(debug=True)