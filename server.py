import socket
import threading
import json
import string

MAX_MESSAGE_LENGTH = 75

# Function to check if the content is a valid text message with printable keyboard characters
def is_valid_text_message(content):
    if isinstance(content, bytes):
        try:
            # Try decoding the content as UTF-8
            decoded_content = content.decode('utf-8')
        except UnicodeDecodeError:
            return False
    elif isinstance(content, str):
        decoded_content = content
    else:
        return False

    # Check if the content contains only printable keyboard characters
    return all(char in string.printable and char.isprintable() for char in decoded_content)

# Function to handle a client connection
def handle_incoming_packets(client_socket, address):
    global number_of_clients  # Declare as global to access the variable

    print(f"Accepted connection from {address}")
    
    # Notify all clients about the new user
    broadcast_to_clients("New Chater Just Joined Say hi!")
    broadcast_to_clients(f"Number of users online: {number_of_clients}") 

    while True:
        try:
            # Receive data from the client
            data = client_socket.recv(1024)

            if not data:
                # No data received, indicating the client has closed the connection
                break

            # Parse the received JSON data
            try:
                packet = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                # print("Invalid JSON format")
                continue

            # Check if the packet has a 'type' field
            if 'type' in packet:
                if packet['type'] == 'chat':
                    # Handle chat messages
                    message = packet.get('message', '')

                    if not is_valid_text_message(message):
                        print("Invalid text message format: Dropping packet")
                        continue

                    # Check if the message is valid UTF-8
                    try:
                        message.encode('utf-8').decode('utf-8')
                    except UnicodeDecodeError:
                        print("Invalid UTF-8 message: Dropping packet")
                        continue

                    # Check message length
                    if len(message) > MAX_MESSAGE_LENGTH:
                        print(f"Ignoring message: Message length exceeds maximum allowed length")
                        continue

                    broadcast_to_clients(message)
                    print(f"New message: {message}")

                else:
                    print("Unknown packet type")
            
            else:
                print("Packet missing 'type' field")

        except ConnectionResetError:
            # Client forcibly closed the connection
            print(f"Connection from {address} closed")
            break

    # Notify all clients about the updated number of users online
    number_of_clients = len(clients)
    broadcast_to_clients(f"Number of users online: {number_of_clients}")

    # Mark the client as inactive
    client_socket.close()

# Function to broadcast a message to all connected clients
def broadcast_to_clients(message):
    # Create a copy of the clients list to avoid modification during iteration
    clients_copy = clients.copy()
    for client in clients_copy:
        if isinstance(client, socket.socket) and client.fileno() != -1:
            try:
                # Modify this line to send the message in the desired format
                client.send(json.dumps({"type": "chat", "message": message}).encode("utf-8") + b'\n')
            except (ConnectionResetError, BrokenPipeError):
                # Client forcibly closed the connection
                clients.remove(client)

print("Welcome to TCPChat Server")
port = input("What port do you want the server to use?\n> ")

# Start listening!
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', int(port)))
server_socket.listen(5)
print(f"Server listening on port {port}\n")

# List of connected Clients
clients = []
number_of_clients = 0  # Initialize the variable

try:
    while True:
        # Accept a connection from a client
        client_socket, address = server_socket.accept()
        
        # Add the client to the list
        clients.append(client_socket)

        # Create a thread to handle the client
        client_handler = threading.Thread(target=handle_incoming_packets, args=(client_socket, address))
        client_handler.start()
        number_of_clients = len(clients)

except KeyboardInterrupt:
    print("Server shutting down")
    server_socket.close()