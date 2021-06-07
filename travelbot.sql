DROP TABLE onewayflights

CREATE TABLE onewayflights (flight_id SERIAL PRIMARY KEY, origin TEXT, destination TEXT, price FLOAT, date DATE)