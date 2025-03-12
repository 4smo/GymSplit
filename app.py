import sqlite3
from flask import Flask, redirect, render_template, request, session, abort, flash, make_response, render_template, jsonify
from werkzeug.security import generate_password_hash
import db, users, config
import markupsafe
import posts
import math, secrets

app = Flask(__name__)
app.secret_key = config.secret_key

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "ERROR: passwords do not match"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "ERROR: username taken"

    return "Registeration successful"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            return "ERROR: wrong username or password"
        
@app.route("/logout")
def logout():
    require_login()

    del session["user_id"]
    return redirect("/")


@app.route("/new_post", methods=["GET", "POST"])
def new_post():
    if request.method == "GET":
        require_login()
        return render_template("new_post.html")

    if request.method == "POST":
        check_csrf()
        require_login()
        title = request.form["title"]
        content = request.form["content"]
        image = request.files["image"]
        tag = request.form["tag"]

        if not title or len(title) > 100 or len(content) > 5000 or len(tag) > 10:
            abort(403)

        if image:
            if not image.filename.endswith(".jpg"):
                flash("VIRHE: Lähettämäsi tiedosto ei ole jpg-tiedosto")
                return redirect("/new_post")

            image_data = image.read()
            if len(image_data) > 100 * 1024:
                flash("VIRHE: Lähettämäsi tiedosto on liian suuri")
                return redirect("/new_post")
        else:
            image_data = None

        user_id = session["user_id"]
        post_id = posts.add_post(title, tag, content, image_data, user_id)

        flash("Postauksen lisääminen onnistui")
        return redirect("/")
    
@app.route("/posts")
def get_posts():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    post_list = posts.get_posts(offset, limit)
    posts_data = [dict(post) for post in post_list]

    if not posts_data:
        return jsonify({"message": "No posts available"}), 204
    
    return jsonify(posts_data)

@app.route("/image/<int:post_id>")
def show_image(post_id):
    image = posts.get_image(post_id)
    if not image:
        return redirect("/static/default.jpg")
    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response