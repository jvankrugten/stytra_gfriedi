import socket

def main():
    # Host and port
    HOST = 'f462i-8840e6'  # Loopback address
    PORT = 12345        # Arbitrary port number

    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the address and port
        s.bind((HOST, PORT))

        # Listen for incoming connections
        s.listen()

        print(f"Server listening on {HOST}:{PORT}")

        while True:
            # Accept incoming connection
            conn, addr = s.accept()
            print(f"Connected by {addr}")

            with conn:
                # Receive data from client
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Received data from client: {data.decode()}")

if __name__ == "__main__":
    main()
