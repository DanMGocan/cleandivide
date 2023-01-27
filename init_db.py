import sqlite3
connection = sqlite3.connect('database.db')

with open ('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Adding a few tasks
cur.execute(
            'INSERT INTO tasks (points, room, content) VALUES (?, ?, ?)',
            ('5', 'Bathroom', 'Cleaning the toilet'),
            )

cur.execute(
            'INSERT INTO tasks (points, room, content) VALUES (?, ?, ?)',
            ('4', 'Bathroom', 'Cleaning the shower'),
            )

cur.execute(
            'INSERT INTO tasks (points, room, content) VALUES (?, ?, ?)',
            ('15', 'Kitchen', 'Doing all the dishes'),
            )

cur.execute(
            'INSERT INTO tasks (points, room, content) VALUES (?, ?, ?)',
            ('5', 'Bedroom', 'Changing the sheets'),
            )


# Adding a few rooms
cur.execute(
    'INSERT INTO room (name, difficulty) VALUES (?, ?)',
    ('Bathroom', '1.1'),
)

# Adding four flatmates
cur.execute(
    'INSERT INTO flatmates (name, multiplier) VALUES (?, ?)',
    ('Marius', '1'),
)

connection.commit()
connection.close()