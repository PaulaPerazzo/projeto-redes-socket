from socket import *
from threading import *
import random

host_name = gethostname()
server_name = gethostbyname(host_name)
server_port = 9999

client_socket = socket(AF_INET, SOCK_DGRAM)
#client_socket.bind((server_name, random.randint(8000, 9000)))


def receive():
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            print(message.decode())
        except:
            pass


thread = Thread(target=receive)
thread.start()

name = ""

while True:
    message = input("Digite: ")

    if message == "bye":
        client_socket.sendto(message.encode(), (server_name, server_port)) #o name fica guardado?
        client_socket.close()
        name = ""
        exit()
    elif message.startswith("hi, meu nome eh ") and not name:
        name = message[len("hi, meu nome eh "):]
        client_socket.sendto(message.encode(), (server_name, server_port))
    elif name != "":
        client_socket.sendto(message.encode(), (server_name, server_port))
        print('pode enviar arquivo txt')

