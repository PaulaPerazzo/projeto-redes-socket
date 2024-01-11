from socket import *
from threading import *
from queue import *

messages = Queue()
clients = []

server_port = 9999
host_name = gethostname()
server_address = gethostbyname(host_name)

server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((server_address, server_port))
print("server is ready to receive")

def receive():
    while True:
        try:
            message, addr = server_socket.recvfrom(2048)
            messages.put((message, addr))
        except:
            pass


def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            print(message.decode())

            if addr not in clients:
                clients.append(addr)
            
            for client in clients:
                try:
                    if message.decode().startswith("NICKNAME:"):
                        name = message.decode()[message.decode().index(":") + 1 :]
                        print(f"{name} entrou!")
                        server_socket.sendto(f"{name} entrou!".encode(), client)
                    else:
                        server_socket.sendto(message, client)
                
                except:
                    clients.remove(client)


first_thread = Thread(target=receive)
second_thread = Thread(target=broadcast)

first_thread.start()
second_thread.start()
