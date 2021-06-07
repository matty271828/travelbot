DROP TABLE onewayflights

CREATE TABLE onewayflights (flight_id SERIAL PRIMARY KEY, source TEXT, dest TEXT, price FLOAT, outdate DATE)