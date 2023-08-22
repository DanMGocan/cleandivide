/* delete tables if exists, for a hard reset */
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS flatmates;
DROP TABLE IF EXISTS users; 

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    last_login DATETIME,
    times_logged INTEGER DEFAULT 1
);

CREATE TABLE rooms (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    modifier INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(email)
 
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    description TEXT NOT NULL,
    points INTEGER NOT NULL,
    room TEXT,
    frequency TEXT NOT NULL DEFAULT "Daily",
    FOREIGN KEY(user_id) REFERENCES users(email)

);

CREATE TABLE flatmates (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    modifier INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(email)
);

-- CREATE TABLE task_assignment (
--     id INTEGER PRIMARY KEY,
--     task_id INTEGER,
--     flatmate_id INTEGER,
--     flatmate_email TEXT
-- );
