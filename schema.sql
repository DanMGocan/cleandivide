/* delete tables if exists, for a hard reset */
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS flatmates;
DROP TABLE IF EXISTS users; 

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL
);

CREATE TABLE rooms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    description TEXT NOT NULL,
    points INTEGER NOT NULL,
    room TEXT,
    FOREIGN KEY(user_id) REFERENCES users(email)

);

CREATE TABLE flatmates (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- CREATE TABLE task_assignment (
--     id INTEGER PRIMARY KEY,
--     task_id INTEGER,
--     flatmate_id INTEGER,
--     flatmate_email TEXT
-- );
