/* selects ALL values from celebs table */
SELECT * FROM /* <- also a clause */ celebs

/* Data types in SQL */
INT , REAL , TEXT , CHAR , VARCHAR , DATE

/* Creating a table */
CREATE /* <- this is a clause */ TABLE test (
    column_1 data_type, /* <- these are parameters */
    column_2 data_type
    )

/* Inserting data into a table */
INSERT INTO celebs (id, name, age)
    VALUES (1, "Person man", 59);

/* We use SELECT to query data */
SELECT column_1 FROM test  /* or */
SELECT * FROM test /* star is a wildcard characer, means select all */ 
/* SELECT statement always returns a new table called the result set */

/* Adding new columns to the table */
ALTER TABLE test ADD COLUMN column_3 TEXT;

/* Updating values in row */
UPDATE test SET column_3 = "New value" WHERE column_1 = 1;

/* Deleting row */
DELETE FROM test WHERE column_3 IS NULL; 

/* Constraings in SQL */
CREATE TABLE test_2 (
    id INTEGER PRIMARY KEY /* This becomes the primary key of the table. This means that
                           the id value is used to uniquely identify the row and new values
                           cannot be inserted if there is already a row with the same value */
    name TEXT UNIQUE /* The value has to be unique. Similar to primary key but there can be
                     more than one UNIQUE data type */
    grade INTEGER NOT NULL /* Value inserted must not be empty */
    age INTEGER DEFAULT 10 /* Defaults to 10 when no value is inserted */

    /* Please note that this list is non-exhaustive */
    )

/* ----------------------------- MANIPULATION ----------------------------------*/

/* Selecting data from specific columns */
SELECT column1, column2 FROM test;

/* Renaming a column */
SELECT column1 AS "Title";

/* Returning unique values in a column */
SELECT DISTINCT tools FROM inventory; 

/* Query the database using wild card characters */
SELECT * FROM movies WHERE name LIKE 'T__t'; /* T__t contains two wildcard 
characters, that can be anything. The final word must be 4 characters long */
SELECT * FROM movies WHERE name LIKE '%t' /* The % wild character means 
zero or more characters. %t means all words that end with t */

/* Finding values between certain ranges */
SELECT * FROM movies WHERE year BETWEEN 2001 AND 2010;
SELECT * FROM names WHERE first_name BETWEEN 'A' AND 'J'; 

/* Using AND and OR to combine multiple conditions */
SELECT * FROM movies WHERE year BETWEEN 1999 AND 2001 AND; /* here we could 
have OR instead of AND */ age > 10;

/* Ordering the results */
SELECT name, year, imdb_rating FROM movies ORDER BY imdb_rating DESC; /* can be 
ordered ASC or DESC */

/* Limiting the number of queries that are displayed to us */
SELECT * FROM movies LIMIT 10;

/* if / else logic in SQL */
SELECT name,
  CASE
    WHEN genre = 'romance' THEN "Chill"
    WHEN genre = 'comedy' THEN "Chill"
    ELSE 'Intense'
  END AS 'Mood'
FROM movies; 

/* ----------------------------- Aggregates ----------------------------------*/

/* Functions: */
COUNT(); /* WHERE condition can be added */
SUM(); /* adds a whole column */
MIN(); MAX(); /* returns the min / max value in a column */
AVG(); /* Takes all the values in a column and returns an average */
ROUND(column, dec_places); /* rounds the values in a column */

/* Group will asses identical data into groups */
SELECT year, AVG(imdb_rating) FROM movies GROUP BY year ORDER BY year; /* will
give us the average rating of movies from each year */
SELECT price, COUNT(*) FROM fake_apps GROUP BY price /* will give us the count
of each price */

/* SQL can take column reference, like 1, 2, etc. instead of names */
SELECT category, price, AVG(downloads) FROM fake_apps GROUP BY 1, 2;

/* HAVING is just WHERE, but to filter groups */

/* Function to work with data */
SELECT timestamp,
   strftime('%H', timestamp) /* Selects only the hour */
FROM hacker_news GROUP BY 1 LIMIT 20;

/* -------------------------- Joining tables -------------------------------*/
SELECT * FROM orders JOIN subscriptions /* The two tables to be joined */
ON orders.subscription_id = subscriptions.subscription_id /* This is the joining 
                                                            point */
WHERE subscriptions.description = 'Fashion Magazine';
/* The inner join operations is only performed when the rows match the
ON condition */

/* A LEFT JOIN operation will keep all the rows from the first table
regardless if they match or not and discard all the rows in the
second table */
SELECT * FROM table1 LEFT JOIN table2
ON table1.column1 = table2.column1
WHERE table2.column1 IS NULL /* To find out what value that is 
present in table 1 is not in table 2 */

/* A union is the operation of combining to tables. However they
must have the same number of columns and the same data types */
SELECT * FROM table1
UNION
SELECT * FROM table2

/* ----------------------- With statement -------------------------------*/
/* Using WITH, we can perform a separate query and pass the data from that
one to our main statement if that makes sense */

WITH previous_query AS (
   SELECT customer_id,
      COUNT(subscription_id) AS 'subscriptions'
   FROM orders
   GROUP BY customer_id
)
SELECT customers.customer_name, 
   previous_query.subscriptions
FROM previous_query
JOIN customers
  ON previous_query.customer_id = customers.customer_id;

/* ----------------------- Primary and foreign keys----------------------*/

PRIMARY KEY: have to be not null, unique
A primary key in a table can be a foreign key in another. 
For example, each student id can be enrolled in a course id




