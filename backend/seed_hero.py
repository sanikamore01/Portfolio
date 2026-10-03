from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

name = "Sanika More"

description = (
    "I'm a full-stack and app developer specializing in building "
    "exceptional digital experiences. Currently focused on creating "
    "accessible, human-centered applications."
)

image_url = (
    "https://media.licdn.com/dms/image/v2/D4D03AQHXERy7W4i-zw/"
    "profile-displayphoto-scale_400_400/B4DZxiZBFNKEAk-/0/"
    "1771177253809?e=1781740800&v=beta&t=UvkyEGTJWhjP5xNfg_ASVXZxKrE8NUEwLXaTkGQFxAw"
)

cur.execute("SELECT id FROM hero_content LIMIT 1")
existing = cur.fetchone()

if existing:
    cur.execute(
        """
        UPDATE hero_content
        SET name = %s, description = %s, image_url = %s
        WHERE id = %s
        """,
        (name, description, image_url, existing[0])
    )
else:
    cur.execute(
        """
        INSERT INTO hero_content (name, description, image_url)
        VALUES (%s, %s, %s)
        """,
        (name, description, image_url)
    )

conn.commit()

cur.close()
conn.close()

print("Hero data inserted successfully!")