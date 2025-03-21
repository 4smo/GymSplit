import db

def add_post(title, content_days, user_id):
    sql = "INSERT INTO posts (title, content_day1, content_day2, content_day3, content_day4, content_day5, content_day6, content_day7, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    params = [title] + content_days + [user_id]
    db.execute(sql, params)

    post_id = db.last_insert_id()
    return post_id

def upvote(user_id, post_id, vote):
    sql = "INSERT INTO votes (user_id, post_id, vote) VALUES (?, ?, ?)"
    db.execute(sql, [user_id, post_id, vote])

def fetch_post(post_id):
    sql = "SELECT id, title, content_day1, content_day2, content_day3, content_day4, content_day5, content_day6, content_day7, user_id FROM posts WHERE id = ?"
    result = db.query(sql, [post_id])
    return result[0] if result else None

def fetch_posts(offset=0, limit=10):
    sql = "SELECT id, title, content_day1, content_day2, content_day3, content_day4, content_day5, content_day6, content_day7, user_id FROM posts LIMIT ? OFFSET ?"
    result = db.query(sql, [limit, offset])

    posts_list = [
        {
            "id": row[0],
            "title": row[1],
            "content_days": row[2:9],
            "user_id": row[9]
        }
        for row in result
    ]
    return posts_list


def remove_post(post_id):
    sql = "DELETE FROM posts WHERE id = ?"
    db.execute(sql, [post_id])

def update_post(title, content_days, user_id, post_id):
    sql = "UPDATE posts SET title = ?, content_day1 = ?, content_day2 = ?, content_day3 = ?, content_day4 = ?, content_day5 = ?, content_day6 = ?, content_day7 = ?, user_id = ? WHERE id = ?"
    params = [title] + content_days + [user_id, post_id]
    db.execute(sql, params)
    
    post_id = db.last_insert_id()
    return post_id