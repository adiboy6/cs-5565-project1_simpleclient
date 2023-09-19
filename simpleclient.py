#!/usr/bin/env python
import socket, sys, select

MAGIC_STR = "cs4254fall2023"
secretkey = ""

def validate_input_args():
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: python simpleclient.py <-p port> [hostname] [username]")
        sys.exit(0)
    
    # Default port value
    port = 4254
    hostname = None
    username = None
    
    i = 1
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

def solve(operator, op1, op2):
    if operator == '+': return op1 + op2
    elif operator == '-': return op1 - op2
    elif operator == '*': return op1 * op2
    return int(float(op1) / op2)

def disconnect(sock):
    try:
        sock.close()
    except:
        return

# Get the command-line arguments and validate it
port, hostname, username = validate_input_args()

try:
    address_info = socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)[0]
    af, socktype, proto, canonname, sa = address_info
except socket.error as err:
    print("Unable to get address info. Please check you hostname and port")
    sys.exit(1)

try:
    client = socket.socket(af, socktype, proto)
except socket.error as err:
    print("Unable to create a socket due to %s" %(err))
    sys.exit(1)

try:
    client.connect((hostname, port))
except socket.error as err:
    print("Unable to connect %s" %(err))
    sys.exit(1)

msg = "%s HELLO %s\n" % (MAGIC_STR, username)

client.send(msg.encode())

while True:
    waiting = select.select([client], [], [], 1)[0]
    for sock in waiting:
        try:
            response = sock.recv(1024).decode()
        except Exception as m:
            print(m)
            disconnect(sock)
            continue
        
        expr = response.strip().split(" ")
        
        if len(expr)==3 and expr[2]=="BYE":
            secretkey=expr[1]
            print(secretkey)
            disconnect(sock)
            break
        elif len(expr)!=5 or expr[1]!="STATUS" or expr[0]!=MAGIC_STR :
            disconnect(sock)
            break
        try:
            op1 = int(expr[-3])
            op2 = int(expr[-1])
        except:
            print("Operand(s) should be a numerical.")
            disconnect(sock)
            continue
        operator = expr[-2]
        # Unsigned integer arithmetic
        # Max/Min : +/-1,000,000
        ans = solve(operator, op1, op2)
        #print(ans)
        msg = "%s %s\n" % (MAGIC_STR, str(ans))
        # Check the partial sends
        client.send(msg.encode())
    # If we got the desired secret, then exit from the loop
    if secretkey!="" : break
disconnect(sock)
