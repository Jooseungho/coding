import socket
from datetime import datetime

HOST = '0.0.0.0'
PORT = 5000
OUTPUT_FILE = 'sensor_data.csv'


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f'Listening on {HOST}:{PORT}')
        conn, addr = s.accept()
        print('Connection from', addr)
        with conn, open(OUTPUT_FILE, 'a') as f:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                text = data.decode('utf-8')
                f.write(text)
                f.flush()


if __name__ == '__main__':
    start_server()
