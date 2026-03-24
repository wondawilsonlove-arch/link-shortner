from flask import Flask, request, redirect, jsonify, render_template_string
import sqlite3
import string
import random
import os

app = Flask(__name__)

DB = "database.db"

# ---------- INIT DB ----------
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


# ---------- HOME UI ----------
@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = None

    if request.method == 'POST':
        url = request.form.get('url')
        code = generate_code()

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO links (code, url) VALUES (?, ?)", (code, url))
        conn.commit()
        conn.close()

        short_url = request.host_url + code

    return render_template_string("""
    <h2>Advanced Link Shortener</h2>
    <form method="POST">
        <input name="url" placeholder="Enter URL" required>
        <button type="submit">Shorten</button>
    </form>

    {% if short_url %}
    <p>Short URL: <a href="{{ short_url }}">{{ short_url }}</a></p>
    {% endif %}

    <br>
    <a href="/dashboard">Dashboard</a>
    """)


# ---------- REDIRECT ----------
@app.route('/<code>')
def redirect_url(code):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT url, clicks FROM links WHERE code=?", (code,))
    data = c.fetchone()

    if data:
        url, clicks = data
        c.execute("UPDATE links SET clicks=? WHERE code=?", (clicks+1, code))
        conn.commit()
        conn.close()
        return redirect(url)

    return "Not found", 404


# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT code, url, clicks FROM links")
    data = c.fetchall()
    conn.close()

    html = "<h2>Dashboard</h2><table border=1><tr><th>Code</th><th>URL</th><th>Clicks</th><th>Edit</th></tr>"

    for row in data:
        html += f"""
        <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
            <td>
                <form action="/edit/{row[0]}" method="post">
                    <input name="url" placeholder="New URL">
                    <button type="submit">Update</button>
                </form>
            </td>
        </tr>
        """

    html += "</table><br><a href='/'>Back</a>"
    return html


# ---------- EDIT LINK ----------
@app.route('/edit/<code>', methods=['POST'])
def edit(code):
    new_url = request.form.get("url")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE links SET url=? WHERE code=?", (new_url, code))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------- API ----------
@app.route('/api/shorten', methods=['POST'])
def api_shorten():
    data = request.json
    url = data.get("url")
    code = generate_code()

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO links (code, url) VALUES (?, ?)", (code, url))
    conn.commit()
    conn.close()

    return jsonify({
        "short_url": request.host_url + code
    })


# ---------- RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
