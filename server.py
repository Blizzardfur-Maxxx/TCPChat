import socket
import threading
import json

MAX_MESSAGE_LENGTH = 75

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

                    # Check message length
                    if len(message) > MAX_MESSAGE_LENGTH:
                        print(f"Ignoring message: Message length exceeds maximum allowed length")
                        continue

                    broadcast_to_clients(message)
                    print(f"New message: {message}")

                elif packet['type'] == 'file':
                    # Ignore or reject file packets
                    print("File packets are not allowed. Ignoring.")

                else:
                    print("Unknown packet type")
            
            else:
                print("Packet missing 'type' field")

        except Exception as e:
            print(f"Error handling client: {e}")
            break

    # Notify all clients about the updated number of users online
    number_of_clients = len(clients)
    broadcast_to_clients(f"Number of users online: {number_of_clients}")

    # Remove the client from the list when disconnected
    clients.remove(client_socket)
    client_socket.close()
    print(f"Connection from {address} closed")

# Function to broadcast a message to all connected clients
def broadcast_to_clients(message):
    for client in clients:
        try:
            # Modify this line to send the message in the desired format
            client.send(json.dumps({"type": "chat", "message": message}).encode("utf-8") + b'\n')
        except Exception as e:
            print(f"Error broadcasting to a client: {e}")
            client.close()
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
