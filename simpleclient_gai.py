import socket
import sys
import re

def validate_input_args():
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: ./simpleclient_gai <-p port> [hostname] [username]")
        sys.exit(1)
    
    port = None
    hostname = None
    username = None
    
    i = 1
    print(sys.argv)
    while i < len(sys.argv):
        if sys.argv[i] == "-p":
            if i + 1 < len(sys.argv):
                try:
                    port = int(sys.argv[i + 1])
                except ValueError:
                    print("Invalid port number.")
                    sys.exit(1)
                if port < 1024 or port > 65535:
                    print("Port number must be between 1024 and 65535.")
                    sys.exit(1)
                i += 2
            else:
                print("Missing port number after -p option.")
                sys.exit(1)
        else:
            if hostname is None:
                hostname = sys.argv[i]
            elif username is None:
                username = sys.argv[i]
            else:
                print("Too many arguments.")
                sys.exit(1)
            i += 1
    
    if hostname is None or username is None:
        print("Missing hostname or username.")
        sys.exit(1)
    
    return port, hostname, username

def send_message(sock, message):
    sock.sendall(message.encode())

def receive_message(sock):
    data = sock.recv(1024).decode()
    return data


port, hostname, username = validate_input_args()

try:
    # Create a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to the server
        print("Connecting to server....")
        s.connect((hostname, port))

        # Send the initial message
        initial_message = f"cs4254fall2023 HELLO {username}\n"
        send_message(s, initial_message)

        while True:
            # Receive a message from the server
            response = receive_message(s)
            print(response)
            
            # Check if the message matches the expected format
            if re.match(r'^cs4254fall2023 STATUS (-?\d+) ([+\-*/]) (-?\d+)\n$', response):
                operand1, operator, operand2 = re.match(r'^cs4254fall2023 STATUS (-?\d+) ([+\-*/]) (-?\d+)$', response).groups()
                operand1 = int(operand1)
                operand2 = int(operand2)

                # Perform the calculation
                if operator == '+':
                    solution = operand1 + operand2
                elif operator == '-':
                    solution = operand1 - operand2
                elif operator == '*':
                    solution = operand1 * operand2
                elif operator == '/':
                    solution = operand1 / operand2
                else:
                    solution = "Invalid operator"
                
                # Send the solution back to the server
                send_message(s, f"cs4254fall2023 {solution}\n")
            elif re.match(r'^cs4254fall2023 [A-Za-z0-9+/=]{64} BYE\n$', response):
                secret_flag = re.search(r'[A-Za-z0-9+/=]{64}', response).group()
                print(secret_flag)
                break
            else:
                print("Received an unexpected message format.")
except Exception as e:
    print(f"An error occurred: {e}")
