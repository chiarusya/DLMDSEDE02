# to tackle the issue of container starting and stopping after first attempt
import time
import socket

def wait_for_kafka(host, port, retries=5, delay=5):
    for _ in range(retries):
        try:
            with socket.create_connection((host, port), timeout=10):
                print("Kafka is up and running.")
                return True
        except OSError as e:
            print(f"Waiting for Kafka: {e}")
            time.sleep(delay)
    print("Kafka is not available. Exiting.")
    return False
