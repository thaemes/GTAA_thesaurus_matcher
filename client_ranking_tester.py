import socket
import json

def create_client(host, port, main_keyword, other_keywords):
    client_socket = socket.socket()
    try:
        client_socket.connect((host, port))
        print("Connected to server.")

        # Prepare the data to be sent
        data = {
            "main_keyword": main_keyword,
            "other_keywords": other_keywords
        }
        message = json.dumps(data)

        # Sending the data
        client_socket.send(message.encode('utf-8'))
        print("Data sent to server.")

        # Receiving and printing the response
        response = client_socket.recv(4096)
        print("Response from server:")
        print(response.decode('utf-8'))

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 12223
    MAIN_KEYWORD = "hockey"
    OTHER_KEYWORDS = [
        {"label": "studenten", "gtaa": 2323},
        {"label": "vrouwen", "gtaa": 1234},
        {"label": "wedstrijden", "gtaa": 233},
        {"label": "sport", "gtaa": 233},
        {"label": "mascottes", "gtaa": 233},
        {"label": "nationaalsocialisme", "gtaa": 233}
        # Add more keywords as needed
    ]

    create_client(HOST, PORT, MAIN_KEYWORD, OTHER_KEYWORDS)
