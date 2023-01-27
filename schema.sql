/* delete tables if exists, for a hard reset */
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS flatmates; 

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    points INTEGER NOT NULL DEFAULT 10,
    room TEXT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE room (
    name TEXT NOT NULL,
    difficulty REAL NOT NULL
);

CREATE TABLE flatmates (
    name TEXT NOT NULL, 
    multiplier REAL NOT NULL
);
