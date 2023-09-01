/* delete tables if exists, for a hard reset */
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS flatmates;
DROP TABLE IF EXISTS users; 
DROP TABLE IF EXISTS task_table;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    last_login DATETIME,
    times_logged INTEGER DEFAULT 1,
    default_database INTEGER DEFAULT 0
);

CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,

    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    description TEXT NOT NULL,
    points INTEGER NOT NULL,
    room_id INTEGER,
    frequency TEXT NOT NULL,
    used_count INTEGER DEFAULT 1,

    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(room_id) REFERENCES rooms(id)
);

CREATE TABLE flatmates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,

    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

-- Junction Table for task_table and tasks
CREATE TABLE task_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_owner TEXT, 
    task_date DATE, 
    task_id INTEGER,
    task_frequency TEXT,
    room_id INTEGER,
    task_owner_id INTEGER,

    FOREIGN KEY(table_owner) REFERENCES users(user_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (task_owner_id) REFERENCES flatmates(id),
    FOREIGN KEY (task_frequency) REFERENCES tasks(frequency)
);


