from flask import Flask, request, redirect, render_template, jsonify
import sqlite3, random, string

app = Flask(__name__)
DB = "db.sqlite3"

def init():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS links(
        id INTEGER PRIMARY KEY,
        code TEXT,
        url TEXT,
        clicks INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

init()

def gen():
    return ''.join(random.choices(string.ascii_letters+string.digits, k=6))


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        url = request.form.get("url")
        code = gen()

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO links(code,url) VALUES(?,?)",(code,url))
        conn.commit()
        conn.close()

        return render_template("index.html", short= request.host_url+code)

    return render_template("index.html")


@app.route("/dashboard")
def dash():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM links")
    data = c.fetchall()
    conn.close()
    return render_template("dashboard.html", data=data)


@app.route("/<code>")
def go(code):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT url,clicks FROM links WHERE code=?",(code,))
    d = c.fetchone()

    if d:
        c.execute("UPDATE links SET clicks=? WHERE code=?",(d[1]+1,code))
        conn.commit()
        conn.close()
        return redirect(d[0])

    return "404"


@app.route("/edit/<id>", methods=["POST"])
def edit(id):
    url = request.form.get("url")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE links SET url=? WHERE id=?",(url,id))
    conn.commit()
    conn.close()
    return redirect("/dashboard")


# ---------- DELETE LINK ----------
@app.route('/delete/<id>')
def delete(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM links WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")


# 🚫 IMPORTANT:
# नीचे कुछ भी नहीं लिखना है
# NO app.run()
# NO if name == "main"
