import socket
import json

client_socket = socket.socket()
host = '127.0.0.1'
port = 12223

try:
    client_socket.connect((host, port))

    print("Connected to server. Type your input and press enter. Type 'quit' to exit.")

    while True:
        # Wait for user input
        user_input = input("Enter your input: ")
        if user_input.lower() == 'quit':
            break

        # Send user input to server
        client_socket.send(user_input.encode('utf-8'))

        while True:
            response = client_socket.recv(1024).decode('utf-8')

            if response == "!slow matching":
                print("Server is initiating slow matching. Please wait...")
            else:
                print("Response from server:", response)
                break  # Exit the inner loop when a response is received

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    client_socket.close()
    print("Socket closed")