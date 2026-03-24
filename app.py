from flask import Flask, request, redirect, jsonify, render_template_string
import sqlite3
import string
import random
import os

app = Flask(__name__)

DB = "database.db"

# ---------- DB INIT ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            url TEXT,
            clicks INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------- GENERATE CODE ----------
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# ---------- UI HOME ----------
@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = None

    if request.method == 'POST':
        original_url = request.form.get('url')
        code = generate_code()

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO links (code, url) VALUES (?, ?)", (code, original_url))
        conn.commit()
        conn.close()

        short_url = request.host_url + code

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Link Shortener</title>
        <style>
            body {
                font-family: Arial;
                text-align: center;
                margin-top: 100px;
                background: #f4f4f4;
            }
            input {
                padding: 10px;
                width: 300px;
            }
            button {
                padding: 10px 20px;
                background: black;
                color: white;
                border: none;
                cursor: pointer;
            }
            .result {
                margin-top: 20px;
                font-size: 18px;
                color: green;
            }
        </style>
    </head>
    <body>

        <h2>🔗 Simple Link Shortener</h2>

        <form method="POST">
            <input type="text" name="url" placeholder="Enter your link" required>
            <br><br>
            <button type="submit">Shorten</button>
        </form>

        {% if short_url %}
            <div class="result">
                Short Link: <br>
                <a href="{{ short_url }}" target="_blank">{{ short_url }}</a>
            </div>
        {% endif %}

    </body>
    </html>
    """)


# ---------- REDIRECT ----------
@app.route('/<code>')
def redirect_url(code):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT url, clicks FROM links WHERE code=?", (code,))
    result = c.fetchone()

    if result:
        url, clicks = result
        c.execute("UPDATE links SET clicks=? WHERE code=?", (clicks + 1, code))
        conn.commit()
        conn.close()
        return redirect(url)

    return "Link not found", 404


# ---------- RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
