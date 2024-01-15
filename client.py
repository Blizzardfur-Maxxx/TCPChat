import socket
import threading
import json

# Function to receive messages from the server
def receive_messages(client_socket):
    incomplete_message_buffer = ""

    while True:
        try:
            # Receive data from the server
            data = client_socket.recv(1024)

            # Combine with any incomplete message from previous data
            data = incomplete_message_buffer + data.decode("utf-8")

            # Split data into individual messages based on newline characters
            messages = data.split("\n")

            # Process each message
            for msg in messages:
                if not msg:
                    continue

                try:
                    packet = json.loads(msg)

                    # Check if the packet has a 'type' field
                    if 'type' in packet:
                        if packet['type'] == 'chat':
                            # Extract and print the chat message
                            message = packet.get('message', '')
                            print(f"{message}")

                        else:
                            # print("Unknown packet type")
                            pass

                    else:
                        # print("Packet missing 'type' field")
                        pass

                except json.JSONDecodeError:
                    print("Invalid JSON format")
                    continue

            # Save any incomplete message for the next iteration
            incomplete_message_buffer = messages[-1] if len(messages) > 1 else ""

        except Exception as e:
            print(f"Error receiving data from server: {e}\n")
            break


# Function to send messages to the server
def send_messages(client_socket, name):
    while True:
        try:
            # Allow the user to input a message
            message = input("> ")

            # Check message length
            if len(message) > 75:
                print("Message length exceeds maximum allowed length (75 characters). Please enter a shorter message.")
                continue

            # Send the chat message to the server
            packet = {"type": "chat", "message": name + ": " + message}
            client_socket.send(json.dumps(packet).encode("utf-8"))

        except Exception as e:
            print(f"Error sending data to server: {e}\n")
            break


print("Welcome to TCPChat")
name = input("Enter Your Username\n> ")
ip = input("Enter Server IP\n> ")
port = input("Enter Server Port\n> ")

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((ip, int(port)))

# Create threads for receiving and sending messages
receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
send_thread = threading.Thread(target=send_messages, args=(client_socket, name))  # Pass the 'name' parameter

# Start the threads
receive_thread.start()
send_thread.start()

# Wait for the threads to finish
receive_thread.join()
send_thread.join()

# Close the socket when done
client_socket.close()
