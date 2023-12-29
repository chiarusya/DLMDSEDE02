import socket

def check_kafka_connection(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)  # Timeout in seconds
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            print("Kafka is reachable")
        else:
            print("Kafka is not reachable")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

check_kafka_connection("kafka", 9092)
