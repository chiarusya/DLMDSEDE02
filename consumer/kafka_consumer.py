import json
import psycopg2
from kafka import KafkaConsumer
import requests
from wait_for_kafka import wait_for_kafka
import sys
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import time

# Start up the server to expose the metrics.
start_http_server(9090)
# Create a metric to track time spent and requests made.
REQUESTS_PROCESSED = Counter('kafka_consumer_requests_total', 'Total number of processed requests')
ERRORS_COUNT = Counter('kafka_consumer_errors_total', 'Total number of errors')
PROCESSING_TIME = Histogram('kafka_consumer_processing_seconds', 'Time spent processing request')

# Kafka consumer group ID
CONSUMER_GROUP_ID = 'consumer_group_1'
KAFKA_TOPIC = 'aircraft_data_topic'
KAFKA_SERVER = 'kafka:9092'

# PostgreSQL connection info
DB_NAME = 'adsb_db'
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'postgres'

# Function to insert data into PostgreSQL
def insert_into_db(conn, record):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO flight_data (timestamp, flight_number, ac_type, dep_stn, arr_stn, latitude, longitude, altitude, speed, heading)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (record['timestamp'], record['flight_number'], record['ac_type'], record['dep_stn'], record['arr_stn'], record['latitude'], record['longitude'], record['altitude'], record['speed'], record['heading']))
        conn.commit()

def send_to_websocket_server(data):
    try:
        response = requests.post('http://websocket-server:8080/broadcast', json=data)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending data to WebSocket server: {e}")

# Create a connection to the database
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)

# Call the wait-for function
if wait_for_kafka('kafka', 9092):
# Consume messages from Kafka
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_SERVER],
        group_id=CONSUMER_GROUP_ID,  # Set the consumer group ID
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for message in consumer:
        start_time = time.time()
        data = message.value
        print("Raw Kafka message:", data)
        # Send data to WebSocket server
        send_to_websocket_server(data)
        # Insert data into PostgreSQL
        insert_into_db(conn, data)
        end_time = time.time()
        processing_duration = end_time - start_time  
        # Update metrics
        REQUESTS_PROCESSED.inc()  # Incrementing a counter
        ERRORS_COUNT.inc()       # Incrementing a counter

        # For histogram, observe the time taken or size of request, etc.
        PROCESSING_TIME.observe(processing_duration)  # Replace 'time_taken' with the actual duration
        
    

    # Close the database connection
    conn.close()

else:
    print("Kafka is not available. Exiting the application.")
    sys.exit(1)  # Exit with a non-zero status to indicate an error