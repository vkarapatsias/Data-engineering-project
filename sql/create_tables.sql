-- Create empty table for arrivals
CREATE TABLE IF NOT EXISTS ARRIVALS (
    name VARCHAR(255) PRIMARY KEY
);
-- Create empty destinations table for arrivals
CREATE TABLE IF NOT EXISTS DESTINATIONS_ARRIVALS (
    name VARCHAR(255) PRIMARY KEY
);

-- Create empty table for departures
CREATE TABLE IF NOT EXISTS DEPARTURES (
    name VARCHAR(255) PRIMARY KEY
);

-- Create empty destinations table for departures
CREATE TABLE IF NOT EXISTS DESTINATIONS_DEPARTURES (
    name VARCHAR(255) PRIMARY KEY
);
