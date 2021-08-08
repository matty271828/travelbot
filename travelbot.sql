DROP TABLE best_flights
DROP TABLE countries_continents
DROP TABLE onewayflights
DROP TABLE place_info
DROP TABLE return_flights

CREATE TABLE best_flights (id SERIAL PRIMARY KEY UNIQUE, source TEXT, dest TEXT, price DOUBLE PRECISION, outdate DATE, indate DATE, origin_id TEXT, destination_id TEXT, continent TEXT, country TEXT);

CREATE TABLE countries_continents (id SERIAL PRIMARY KEY, country TEXT UNIQUE, continent TEXT);

CREATE TABLE onewayflights (id SERIAL PRIMARY KEY, source TEXT, dest TEXT, price DOUBLE PRECISION, outdate DATE, origin_id TEXT, destination_id TEXT);

CREATE TABLE place_info (id SERIAL, skyscanner_code TEXT, country TEXT, placename TEXT, continent TEXT);

CREATE TABLE return_flights (id SERIAL PRIMARY KEY UNIQUE, source TEXT, dest TEXT, price DOUBLE PRECISION, outdate DATE, indate DATE, origin_id TEXT, destination_id TEXT);