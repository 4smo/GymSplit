import db

def add_post(title, content_days, tag, user_id):
    sql = "INSERT INTO posts (title, tag, content_day1, content_day2, content_day3, content_day4, content_day5, content_day6, content_day7, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    params = [title, tag] + content_days + [user_id]
    db.execute(sql, params)

    post_id = db.last_insert_id()
    return post_id

def vote(user_id, post_id, vote):
    sql = "INSERT INTO votes (user_id, post_id, vote) VALUES (?, ?, ?)"
    db.execute(sql, [user_id, post_id, vote])

def fetch_post(post_id):
    sql = "SELECT id, title, tag, content_day1, content_day2, content_day3, content_day4, content_day5, content_day6, content_day7, user_id FROM posts WHERE id = ?"
    result = db.query(sql, [post_id])
    return result[0] if result else None

def fetch_posts(offset=0, limit=10):
    sql = "SELECT id, title, tag, content_day1, content_day2, content_day3, content_day4, content_day5, content_day6, content_day7, user_id FROM posts LIMIT ? OFFSET ?"
    result = db.query(sql, [limit, offset])

    posts_list = [
        {
            "id": row[0],
            "title": row[1],
            "tag": row[2],
            "content_days": row[3:10],
            "user_id": row[10]
        }
        for row in result
    ]
    return posts_list

def remove_post(post_id):
    sql = "DELETE FROM posts WHERE id = ?"
    db.execute(sql, [post_id])

def update_post(title, tag, content_days, user_id, post_id):
    sql = "UPDATE posts SET title = ?, tag = ?, content_day1 = ?, content_day2 = ?, content_day3 = ?, content_day4 = ?, content_day5 = ?, content_day6 = ?, content_day7 = ?, user_id = ? WHERE id = ?"
    params = [title, tag] + content_days + [user_id, post_id]
    db.execute(sql, params)
    
    post_id = db.last_insert_id()
    return post_id

def search(query, offset=0, limit=10):
    sql = "SELECT id, title, tag, content_day1, content_day2, content_day3, content_day4, content_day5, content_day6, content_day7, user_id FROM posts WHERE tag = ? LIMIT ? OFFSET ?"
    result = db.query(sql, [query, limit, offset])
    posts_list = [
        {
            "id": row[0],
            "title": row[1],
            "tag": row[2],
            "content_days": row[3:10],
            "user_id": row[10]
        }
        for row in result
    ]
    return posts_list

def user_posts(user_id, offset=0, limit=10):
    sql = "SELECT id, title, tag, content_day1, content_day2, content_day3, content_day4, content_day5, content_day6, content_day7, user_id FROM posts WHERE user_id = ? LIMIT ? OFFSET ?"
    result = db.query(sql, [user_id, limit, offset])
    posts_list = [
        {
            "id": row[0],
            "title": row[1],
            "tag": row[2],
            "content_days": row[3:10],
            "user_id": row[10]
        }
        for row in result
    ]
    return posts_list


def total_posts_count(user_id):
    sql = "SELECT COUNT(*) FROM posts WHERE user_id = ?"
    result = db.query(sql, [user_id])
    return result[0][0]

def get_user_vote(user_id, post_id):
    sql = "SELECT vote FROM votes WHERE user_id = ? AND post_id = ?"
    result = db.query(sql, [user_id, post_id])
    if result:
        return result[0]
    else:
        return None
    
def get_post_votes(post_id):
    sql = "SELECT SUM(vote) as total_votes FROM votes WHERE post_id = ?"
    result = db.query(sql, [post_id])
    if result:
        return result[0]['total_votes']
    return 0

def get_received_upvotes(user_id):
    sql = """
    SELECT SUM(vote) as received_upvotes 
    FROM votes 
    JOIN posts ON votes.post_id = posts.id 
    WHERE posts.user_id = ? AND vote > 0
    """
    result = db.query(sql, [user_id])
    if result:
        return result[0]['received_upvotes']
    return 0

def get_sent_votes(user_id):
    sql = "SELECT SUM(vote) as sent_votes FROM votes WHERE user_id = ?"
    result = db.query(sql, [user_id])
    if result:
        return result[0]['sent_votes']
    return 0