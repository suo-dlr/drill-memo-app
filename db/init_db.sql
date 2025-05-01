CREATE DATABASE db_memo;
USE db_memo;

CREATE TABLE IF NOT EXISTS memo(
    id INT AUTO_INCREMENT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);


INSERT INTO memo (title, content)
VALUES
    ("memo1", "content1")