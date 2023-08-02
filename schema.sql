/* delete tables if exists, for a hard reset */
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS flatmates; 

CREATE TABLE room (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    points INTEGER NOT NULL,
    room_id INTEGER
);

CREATE TABLE flatmates (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE task_assignment (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    flatmate_id INTEGER
);
