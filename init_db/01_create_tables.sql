DO $$
BEGIN
    -- Check if the flight_data table exists
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename  = 'flight_data') THEN
        -- If it exists, truncate the table
        EXECUTE 'TRUNCATE TABLE public.flight_data';
    ELSE
        -- If it does not exist, create the table
        CREATE TABLE public.flight_data (
            id SERIAL PRIMARY KEY,  -- Add this line for Sequence ID
            timestamp TIMESTAMP,
            flight_number VARCHAR(255),
            ac_type VARCHAR(255),
            dep_stn VARCHAR(255),
            arr_stn VARCHAR(255),
            latitude FLOAT,
            longitude FLOAT,
            altitude FLOAT,
            speed FLOAT,
            heading FLOAT
        );
    END IF;
END
$$;
