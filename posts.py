import db

def add_post(title, tag, content, image_data, user_id):
    sql = "INSERT INTO posts (title, tag, content, image_data, user_id) VALUES (?, ?, ?, ?, ?)"
    db.execute(sql, [title, tag, content, image_data, user_id])

    post_id = db.last_insert_id()
    print(post_id)
    return post_id

def upvote(user_id, post_id, vote):
    sql = "INSERT INTO votes (user_id, post_id, vote) VALUES (?, ?, ?)"
    db.execute(sql, [user_id, post_id, vote])

def get_post(post_id):
    sql = "SELECT id, title, image_data FROM posts WHERE id = ?"
    result = db.query(sql, [post_id])
    return result[0] if result else None

def get_image(post_id):
    sql = "SELECT image_data FROM posts WHERE id = ?"
    result = db.query(sql, [post_id])
    return result[0][0] if result else None

def get_posts(offset=0, limit=10):
    sql = "SELECT id, title, image_data FROM posts LIMIT ? OFFSET ?"
    result = db.query(sql, [limit, offset])

    posts_list = [
        {
            "id": row[0],
            "title": row[1],
            "has_image": bool(row[2])
        }
        for row in result
    ]
    return posts_list