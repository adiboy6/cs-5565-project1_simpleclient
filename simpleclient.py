# Import socket module
import socket, sys, select

MAGIC_STR = "cs4254fall2023"
secretkey = ""

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

# Port? Left empty or use ephemeral port
PORT = int(sys.argv[1])
SERVER = sys.argv[2]
USERNAME = sys.argv[3]

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

msg = "%s HELLO %s\n" % (MAGIC_STR, USERNAME)

client.send(msg.encode())

total=0
ops=set()

while True:
    waiting = select.select([client], [], [], 1)[0]
    for sock in waiting:
        try:
            response = sock.recv(1024).decode()
            #print(response)
        except:
            disconnect(sock)
            continue
        
        expr = response.strip().split(" ")
        
        if len(expr)==3 and expr[2]=="BYE":
            # Validate if it's a 64-byte secret code or not
            secretkey=expr[1]
            print(secretkey)
            disconnect(sock)
            break
        elif len(expr)!=5 or expr[1]!="STATUS" or expr[0]!=MAGIC_STR :
            client.close()
            break
        op1 = int(expr[-3])
        op2 = int(expr[-1])
        ops.add(op1)
        ops.add(op2)
        operator = expr[-2]
        # Unsigned integer arithmetic
        # Max/Min : +/-1,000,000
        ans = solve(operator, op1, op2)
        #print(ans)
        msg = "%s %s\n" % (MAGIC_STR, str(ans))
        # Check the partial sends
        client.send(msg.encode())
    total+=1
    if secretkey!="" : break
disconnect(sock)
