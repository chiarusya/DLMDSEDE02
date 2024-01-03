import psycopg2
import requests
import time

DB_NAME = 'adsb_db'
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'postgres'
WEB_SOCKET_SERVER = 'http://websocket-server:8080/broadcast'

# Initialize a variable to keep track of the last ID fetched. 
LAST_FETCHED_ID = 0  

def fetch_from_db(conn):
    global LAST_FETCHED_ID
    new_records = []

    with conn.cursor() as cursor:
        # Fetch records with an ID greater than the last one fetched
        cursor.execute("""
            SELECT id, flight_number, latitude, longitude, heading, timestamp
            FROM flight_data
            WHERE id > %s
            ORDER BY id ASC
            ;
        """, (LAST_FETCHED_ID,))
        
        new_records = cursor.fetchall()

    # If new records were fetched, update LAST_FETCHED_ID to the ID of the last record fetched
    if new_records:
        LAST_FETCHED_ID = new_records[-1][0]  # Assuming id is the first field in the SELECT

    return new_records

def send_to_websocket_server(data):
    # Assuming WebSocket server can handle batch data; if not, iterate and send one by one
    try:
        for record in data:  # Send each record individually
            response = requests.post(WEB_SOCKET_SERVER, json={
                "flight_number": record[1],
                "latitude": record[2],
                "longitude": record[3],
                "heading": record[4]
            })
            response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.RequestException as e:
        print(f"Error sending data to WebSocket server: {e}")

def main():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    try:
        while True:  # Infinite loop for continuous polling
            data = fetch_from_db(conn)
            if data:
                send_to_websocket_server(data)
            time.sleep(3)  # Sleep for 3 seconds
    finally:
        conn.close()  # Ensure the connection is closed even if an error occurs

if __name__ == '__main__':
    main()

