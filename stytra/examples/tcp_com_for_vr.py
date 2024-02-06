import socket

""" 
This is an an attempt to add sending something over tcp
"""

if __name__ == "__main__":
    def __init__(self):
        super().__init__()
        self.start_tcp_client()

    def start_tcp_client(self):
        # Create a TCP/IP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the server's address and port
        server_address = ('f462i-8840e6', 12345)
        print(f"Connecting to TCP server on {server_address[0]}:{server_address[1]}")
        self.client_socket.connect(server_address)

    def send_data_over_tcp(self, data):
        try:
            # Send data
            self.client_socket.sendall(data.encode())
            print("Data sent successfully")
        except Exception as e:
            print("Error sending data:", e)

    def run(self):
        # Example of sending data
        data = "fish_vel: <put your data here>"
        self.send_data_over_tcp(data)