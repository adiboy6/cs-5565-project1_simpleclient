import sys, socket, select, random, time, datetime

MAGIC_STR = "cs4254fall2023"

port = random.randint(1000,5000)
try:
    x = sys.argv.index('-p')
    if x != -1 and x + 1 < len(sys.argv):
        port = int(sys.argv[x + 1])
except:
    pass


#sample student pid and secret key
sample_pid='hokiebird'
sample_secret_key='5f6b0b4e201f2a7e66927abb5cadeec81624dcc8efe6644b78aa182213f653a2'

class Client:
    def __init__(self):
        self.rounds = 10
        self.rand1 = 0;
        self.rand2 = 0;
        self.operator = 0;
        self.student_id = "";
        self.last_active = time.time()

    #calculate the result of two random number as the answer
    def solve(self):
        if self.operator == '+': return client.rand1 + client.rand2
        elif self.operator == '-': return client.rand1 - client.rand2
        elif self.operator == '*': return client.rand1 * client.rand2
        return int(float(client.rand1) / client.rand2)

def accept(listen, sockets, clients, waiting):
    waiting.remove(listen)

    try:
        sock = listen.accept()[0]
    except:
        return

    sockets.append(sock)
    clients[sock] = Client()

def disconnect(sock, sockets, clients):
    try:
        sock.close()
    except:
        return
    clients.pop(sock)
    sockets.remove(sock)

#send two random numbers and one operator
def send_status(sock, client):
    client.rand1 = random.randint(1, 10)
    client.rand2 = random.randint(1, 10)
    client.operator = random.choice(('+', '-', '*', '/'))
    client.last_active = time.time()

    msg = "%s STATUS %i %s %i\n" % (MAGIC_STR, client.rand1, client.operator, client.rand2)
    try:
        sock.send(msg.encode("ascii"))
        return True
    except:
        return False

def send_bye(sock, client):
    if client.student_id != sample_pid: flag = 'Unknown_Hokie_NetID'
    else: flag = sample_secret_key

    msg = "%s %s BYE\n" % (MAGIC_STR, flag)
    print("%s [%s] success" % (datetime.datetime.now(), str(client.student_id)))
    sys.stdout.flush()
    try:
        sock.send(msg.encode("ascii"))
        return True
    except:
        return False

#open listen sockets
listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print("Running on host: %s" % socket.gethostname())

try:
    listen.bind((socket.gethostname(), port)) #host address
except OSError:
    print(f"Unable to bind to port {port}! It's probably already in use, try restarting or using a different port.")
    exit(-1)
print(f"listening at port {port}")
listen.listen(1)
sockets = [listen,]

clients = {}

while True:
    waiting = select.select(sockets, [], [], 1)[0]

    if listen in waiting:
        accept(listen, sockets, clients, waiting)

    for sock in waiting:
        try:
            raw_msg = sock.recv(1024)
            msg = raw_msg.decode()
            print(msg)
        except:
            disconnect(sock, sockets, clients)
            continue

        if len(msg) == 0 or msg[-1] != '\n':
            print('disconnect')
            disconnect(sock, sockets, clients)
            continue

        elem = msg.split()

        #elem number less than two or first elem is not correct, disconnect
        if len(elem) < 2 or elem[0] != MAGIC_STR:
            disconnect(sock, sockets, clients)
            continue

        #right format, hello infor:
        client = clients[sock]
        if len(elem) == 3 and elem[1] == 'HELLO' and client.rand1 == 0:
            client.student_id = elem[2]
            print("%s [%s] start" % (datetime.datetime.now(), str(client.student_id).strip()))
            sys.stdout.flush()
            send_status(sock, client)
            continue

        if len(elem) == 2:
            # check solution
            try:
                i = int(elem[1])
                #print msg;
            except:
                disconnect(sock, sockets, clients)
                continue

            if i != client.solve():


                disconnect(sock, sockets, clients)
                continue

            client.rounds -= 1

            if client.rounds == 0: send_bye(sock, client)
            elif send_status(sock, client): continue

        disconnect(sock, sockets, clients)
        print("disconnect one client")

    # garbage collect
    t = time.time()
    for sock, client in list(clients.items()):
        if t - client.last_active > 60: # 60 second timeout
            disconnect(sock, sockets, clients)
            print("disconnect one client")
