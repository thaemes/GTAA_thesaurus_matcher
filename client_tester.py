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

        # Receive and print response from server
        try:
            t = client_socket.recv(1024)
            if not t:
                print("No response from server. Exiting.")
                break  # Break the loop if no data is received (socket closed by server)
            
            print("Response from server:", t.decode('utf-8'), "\n")
        except KeyboardInterrupt:
            print("Interrupted by user.")
            break  # Break the loop if KeyboardInterrupt occurs

finally:
    client_socket.close()
    print("Socket closed")




# import socket
# import json

# client_socket = socket.socket()
# host = '127.0.0.1'
# port = 12223

# try:
#     client_socket.connect((host, port))
#     client_socket.send(b'bananen en aardbeien')

#     while True:
#         try:
#             t = client_socket.recv(1024)
#             if not t:
#                 break  # Break the loop if no data is received (socket closed by server)
            
#             print(t.decode('utf-8'))
#         except KeyboardInterrupt:
#             break  # Break the loop if KeyboardInterrupt occurs

# finally:
#     client_socket.close()
#     print("Socket closed")
