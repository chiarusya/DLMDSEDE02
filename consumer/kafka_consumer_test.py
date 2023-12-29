# test connection within Docker Exec
from kafka import KafkaConsumer

KAFKA_TOPIC = 'aircraft_data_topic'
KAFKA_SERVER = 'kafka:9092'

consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=[KAFKA_SERVER])

for message in consumer:
    print(f"Received message: {message.value.decode('utf-8')}")

