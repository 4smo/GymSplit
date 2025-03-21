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
    return render_template("index.html", csrf_token=session.get("csrf_token"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled={})

    if request.method == "POST":
        username = request.form["username"]
        if not username or len(username) > 16:
            abort(403)
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if password1 != password2:
            flash("Passwords do not match")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

        try:
            users.create_user(username, password1)
            flash("Registering successful. You can now log in")
            return redirect("/")
        except sqlite3.IntegrityError:
            flash("Username taken")
            filled = {"username": username}
            return render_template("register.html", filled=filled)


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
            flash("Wrong username or password")
            return render_template("login.html")
        
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
        content_days = [request.form.get(f'content_day{i}', '') for i in range(1, 8)]

        if not title or len(title) > 100:
            abort(403)
        

        user_id = session["user_id"]
        post_id = posts.add_post(title, content_days, user_id)
   
        return redirect("/")
    
@app.route('/posts')
def get_posts():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    posts_data = posts.fetch_posts(offset, limit)
    return jsonify(posts_data)

@app.route("/image/<int:post_id>")
def show_image(post_id):
    image = posts.get_image(post_id)
    if not image:
        return redirect("/static/default.jpg")
    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response


@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    require_login()
    check_csrf()
    post = posts.fetch_post(post_id)
    if not post or post["user_id"] != session["user_id"]:
        abort(403)
    posts.remove_post(post["id"])
    return redirect("/")

@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):

    if request.method == "GET":
        require_login()
        post = posts.fetch_post(post_id)
        if not post or post["user_id"] != session["user_id"]:
            abort(403)
        filled = {
            "title": post["title"],
            "content_day1": post["content_day1"],
            "content_day2": post["content_day2"],
            "content_day3": post["content_day3"],
            "content_day4": post["content_day4"],
            "content_day5": post["content_day5"],
            "content_day6": post["content_day6"],
            "content_day7": post["content_day7"]
        }
        return render_template("edit.html", filled=filled, post_id=post_id)
    
    if request.method == "POST":
        require_login()
        check_csrf()

        post = posts.fetch_post(post_id)
        if not post or post["user_id"] != session["user_id"]:
            abort(403)

        title = request.form["title"]
        content_days = [request.form.get(f'content_day{i}', '') for i in range(1, 8)]
        if not title or len(title) > 100:
            abort(403)
        user_id = session["user_id"]
        posts.update_post(title, content_days, user_id, post_id)
        return redirect(f"/post/{post_id}")


@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = posts.fetch_post(post_id)
    if not post:
        abort(404)
    return render_template("post.html", post=post)