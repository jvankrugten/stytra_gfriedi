#python C:\Users\vankjaap\AppData\Local\anaconda3\envs\stytra_env\Lib\site-packages\stytra_gfriedi\tcpservertest.py

import socket

def main():
    # Host and port
    HOST = 'f462i-8840e6'  # Loopback address
    PORT = 12345        # Arbitrary port number

    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to server
        s.connect((HOST, PORT))
        print(f"Connected to server {HOST}:{PORT}")

        # Send data to server
        data = "Hello, server!"
        s.sendall(data.encode())
        print(f"Sent data to server: {data}")

if __name__ == "__main__":
    main()
