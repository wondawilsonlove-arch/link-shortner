from flask import Flask, request, redirect, jsonify
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

# ---------- GENERATE SHORT CODE ----------
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# ---------- CREATE SHORT LINK ----------
@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.json
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL required"}), 400

    code = generate_code()

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    try:
        c.execute("INSERT INTO links (code, url) VALUES (?, ?)", (code, original_url))
        conn.commit()
    except:
        return jsonify({"error": "Try again"}), 500

    conn.close()

    return jsonify({
        "short_url": request.host_url + code
    })


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
        return redirect(url, code=302)

    return "Link not found", 404


# ---------- GET STATS ----------
@app.route('/stats/<code>')
def stats(code):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT url, clicks FROM links WHERE code=?", (code,))
    result = c.fetchone()

    conn.close()

    if result:
        return jsonify({
            "url": result[0],
            "clicks": result[1]
        })

    return jsonify({"error": "Not found"}), 404


# ---------- EDIT LINK ----------
@app.route('/edit/<code>', methods=['POST'])
def edit(code):
    data = request.json
    new_url = data.get("url")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("UPDATE links SET url=? WHERE code=?", (new_url, code))
    conn.commit()
    conn.close()

    return jsonify({"message": "Updated successfully"})


# ---------- RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
