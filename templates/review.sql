CREATE TABLE reviews(id SERIAL PRIMARY KEY,
comments VARCHAR NOT NULL,
book_id INTEGER REFERENCES books,
user_id INTEGER REFERENCES users);