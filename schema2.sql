/* delete tables if exists, for a hard reset */
DROP TABLE IF EXISTS task_table;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS flatmates;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS daily_bonus;
DROP TABLE IF EXISTS awards;
DROP TABLE IF EXISTS powercosts;


CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    first_login DATETIME,
    last_login DATETIME,
    times_logged INTEGER DEFAULT 0,
    table_owner INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0
    );

CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,

    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_rooms_user_id ON rooms(user_id);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    description TEXT NOT NULL,
    points INTEGER NOT NULL,
    room TEXT,
    frequency TEXT NOT NULL,
    used_count INTEGER DEFAULT 1,

    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(room) REFERENCES rooms(id)
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_room ON tasks(room);

CREATE TABLE flatmates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,

    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_flatmates_user_id ON flatmates(user_id);

CREATE TABLE daily_bonus (
    user_id TEXT,
    date DATE,
    points_awarded INTEGER,
    PRIMARY KEY(user_id, date)
);

CREATE TABLE awards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    logged_in INTEGER DEFAULT 1,
    five_tasks_day INTEGER DEFAULT 0,
    ten_tasks_day INTEGER DEFAULT 0,
    fifteen_tasks_day INTEGER DEFAULT 0,
    member_30_days INTEGER DEFAULT 0,
    member_120_days INTEGER DEFAULT 0,
    member_365_days INTEGER DEFAULT 0,
    check_500_points INTEGER DEFAULT 0,
    check_1000_points INTEGER DEFAULT 0,
    check_2500_points INTEGER DEFAULT 0,
    completed_100_tasks INTEGER DEFAULT 0,
    completed_250_tasks INTEGER DEFAULT 0,
    completed_750_tasks INTEGER DEFAULT 0,
    completed_1500_tasks INTEGER DEFAULT 0,
    completed_2500_tasks INTEGER DEFAULT 0,

    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE powercosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    user_id TEXT NOT NULL UNIQUE,
    reassign INTEGER DEFAULT 100,
    skip INTEGER DEFAULT 135,
    procrastinate INTEGER DEFAULT 75,
    lower_reward_threshold FLOAT DEFAULT 0.25,
    higher_reward_threshold FLOAT DEFAULT 0.75,

    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

-- Junction Table for task_table and tasks
CREATE TABLE task_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_owner TEXT, 
    task_date DATE, 
    task_id INTEGER,
    task_complete INTEGER DEFAULT 0,
    room_id INTEGER,
    task_owner TEXT,

    FOREIGN KEY(table_owner) REFERENCES users(user_id),
    FOREIGN KEY(task_id) REFERENCES tasks(id),
    FOREIGN KEY(room_id) REFERENCES rooms(id),
    FOREIGN KEY(task_owner) REFERENCES flatmates(id)
);

CREATE INDEX idx_task_table_table_owner ON task_table(table_owner);
CREATE INDEX idx_task_table_task_id ON task_table(task_id);
CREATE INDEX idx_task_table_room_id ON task_table(room_id);
CREATE INDEX idx_task_table_task_owner ON task_table(task_owner);
