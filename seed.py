import random
import sqlite3

db = sqlite3.connect("database.db")

# Delete all data and reset autoincrement
db.execute("DELETE FROM users")
db.execute("DELETE FROM posts")
db.execute("DELETE FROM votes")
db.execute("DELETE FROM sqlite_sequence WHERE name='posts'")
db.execute("DELETE FROM sqlite_sequence WHERE name='users'")
db.execute("DELETE FROM sqlite_sequence WHERE name='votes'")

user_count = 1000
post_count = 10**5
vote_count = 10**6
tags = ["U/L", "FB", "other", "PPL"]

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username) VALUES (?)",
               ["user" + str(i)])

for i in range(1, post_count + 1):
    tag = random.choice(tags)
    content_day1 = "day 1 for post " + str(i)
    content_day2 = "day 2 for post " + str(i)
    content_day3 = "day 3 for post " + str(i)
    content_day4 = "day 4 for post " + str(i)
    content_day5 = "day 5 for post " + str(i)
    content_day6 = "day 6 for post " + str(i)
    content_day7 = "day 7 for post " + str(i)
    user_id = random.randint(1, user_count)
    
    db.execute("""INSERT INTO posts (title, tag, content_day1, content_day2, content_day3, content_day4, content_day5, content_day6, content_day7, user_id)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
               ["post" + str(i), tag, content_day1, content_day2, content_day3, content_day4, content_day5, content_day6, content_day7, user_id])

for i in range(1, vote_count + 1):
    user_id = random.randint(1, user_count)
    post_id = random.randint(1, post_count)
    db.execute("""INSERT INTO votes (user_id, post_id, vote)
                  VALUES (?, ?, ?)""",
               [user_id, post_id, 1])

db.commit()
db.close()