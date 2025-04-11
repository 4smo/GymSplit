from flask import Flask, redirect, render_template, request, session, abort, flash, make_response, jsonify
import db, users, config
import markupsafe
import posts
import math, secrets
import sqlite3

app = Flask(__name__)
app.secret_key = config.secret_key

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.template_filter()
def filter_empty_days(content_days):
    return [day for day in content_days if day.strip()]

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route('/')
def index():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    paginated_posts = posts.fetch_posts(offset, limit)
    return render_template('index.html', posts=paginated_posts, offset=offset, limit=limit)

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
        tag = request.form["tag"]
        content_days = [request.form.get(f'content_day{i}', '') for i in range(1, 8)]

        if not title or len(title) > 100:
            abort(403)

        user_id = session["user_id"]
        post_id = posts.add_post(title, content_days, tag, user_id)
   
        return redirect("/")
    
@app.route('/posts')
def get_posts():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    paginated_posts = posts.fetch_posts(offset, limit)
    return jsonify(paginated_posts)

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
            "tag": post["tag"],
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
        tag = request.form["tag"]
        content_days = [request.form.get(f'content_day{i}', '') for i in range(1, 8)]
        if not title or len(title) > 100:
            abort(403)
        user_id = session["user_id"]
        posts.update_post(title, tag, content_days, user_id, post_id)
        return redirect(f"/post/{post_id}")


@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = posts.fetch_post(post_id)
    user_id = session.get("user_id")
    if not post:
        abort(404)

    total_votes = posts.get_post_votes(post_id)
    return render_template("post.html", post=post, user_id=user_id, total_votes=total_votes)


@app.route("/search")
def search():
    query = request.args.get("query")
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 10))
    results_paginated = posts.search(query, offset, limit) if query else []
    return render_template("search.html", query=query, results=results_paginated, offset=offset, limit=limit)

@app.route("/user/<int:user_id>")
def profile(user_id):
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 10))
    user_posts = posts.user_posts(user_id, offset, limit)
    user = users.get_user(user_id)
    total_posts = posts.total_posts_count(user_id)
    return render_template("profile.html", posts=user_posts, user=user, offset=offset, limit=limit, total_posts=total_posts)


@app.route("/post/<int:post_id>/vote", methods=["POST"])
def vote(post_id):
    require_login()
    check_csrf()

    user_id = session.get("user_id")
    vote = request.form.get("vote")

    if user_id is None:
        abort(400)

    existing_vote = posts.get_user_vote(user_id, post_id)
    if existing_vote is not None:
        flash("You have already voted on this post.")
        return redirect(f"/post/{post_id}")

    posts.vote(user_id, post_id, vote)
    return redirect(f"/post/{post_id}")  