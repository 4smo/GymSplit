CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    tag TEXT,
    content_day1 TEXT,
    content_day2 TEXT,
    content_day3 TEXT,
    content_day4 TEXT,
    content_day6 TEXT,
    content_day7 TEXT
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE votes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    post_id INTEGER,
    vote INTEGER
);

CREATE INDEX idx_votes_post_id ON votes (post_id);