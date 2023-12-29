import csv
import json
import sys
import time
import logging
import itertools
from kafka import KafkaProducer

# Path to the CSV file
csv_file_path = '/shared_data/ADSB_dataset.csv'
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from wait_for_kafka import wait_for_kafka

# Call the wait-for function
if wait_for_kafka('kafka', 9092):
    print("Kafka is up and running.")
    # Kafka is ready. Initialize and start Kafka producer here
    # Kafka configuration
    KAFKA_TOPIC = 'aircraft_data_topic'
    KAFKA_SERVER = 'kafka:9092'

    # Initialize Kafka producer
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER],
                            value_serializer=lambda x: json.dumps(x).encode('utf-8'))
   
    def read_csv_in_chunks(csv_file_path, chunk_size=1000):
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            while True:
                chunk = list(itertools.islice(reader, chunk_size))
                if not chunk:
                    break
                yield chunk

    def publish_data(data):
        for row in data:
            # Serialize and send each row to Kafka
            producer.send(KAFKA_TOPIC, row)
            logging.info(f"Published data: {row}")
        # Flush the messages
        producer.flush()

    def main(csv_file_path, delay=3):
        while True:  # Infinite loop to simulate continuous data streaming
            for chunk in read_csv_in_chunks(csv_file_path):
                # Process each chunk (batch) of data
                publish_data(chunk)
                # Optional: Simulate processing time
                time.sleep(delay)  # Simulate real-time delay

    # Start processing
    logging.info("Simulation Started")
    main(csv_file_path)
    logging.info("Simulation Finished")  # This line will actually never be reached

else:
    print("Kafka is not available. Exiting the application.")
    sys.exit(1)  # Exit with a non-zero status to indicate an error