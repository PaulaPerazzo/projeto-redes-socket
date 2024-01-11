from socket import *
from threading import *
import random

host_name = gethostname()
server_name = gethostbyname(host_name)
server_port = 9999

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.bind((server_name, random.randint(8000, 9000)))

name = input("NICKNAME: ")

def receive():
    while True:
        try:
            message, _ = client_socket.recvfrom(2048)
            print(message.decode())
        except:
            pass


thread = Thread(target=receive)
thread.start()

client_socket.sendto(f"bem vindo: {name}".encode(), (server_name, server_port))

while True:
    message = input("digite: ")

    if message == "!q":
        client_socket.sendto(f"{name}: saiu da sala".encode(), (server_name, server_port))
        client_socket.close()
        exit()
    else:
        client_socket.sendto(f"{name}: {message}".encode(), (server_name, server_port))
