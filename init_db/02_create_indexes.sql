-- create-indexes.sql
CREATE INDEX idx_flight_number ON flight_data (flight_number);
CREATE INDEX idx_dep_stn ON flight_data (dep_stn);
CREATE INDEX idx_arr_stn ON flight_data (arr_stn);
CREATE INDEX idx_timestamp on flight_data (timestamp);
