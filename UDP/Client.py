from socket import *
from threading import *
import random
from pathlib import Path
import os
import time


host_name = gethostname()
server_name = gethostbyname(host_name)
server_port = 9999

client_port = random.randint(8000, 9000)
client_socket = socket(AF_INET, SOCK_DGRAM)
address = (server_name, server_port)
client_socket.connect(address)
name = ""


def receive():
    complete_message = ""
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            decoded_message = message.decode()
            if decoded_message != "\\x00":
                complete_message += decoded_message
            else:
                print(complete_message)
                complete_message = ""
        except:
            pass

thread = Thread(target=receive)
thread.start()

def get_file_packet_count(filename, buffer_size):
    byte_size = os.stat(filename).st_size
    
    packet_count = byte_size//buffer_size

    if byte_size%buffer_size:
        packet_count += 1

    return packet_count


while True:
    message = input("Digite: ")

    if message.startswith("hi, meu nome eh ") and not name:
        name = message[len("hi, meu nome eh "):]
        client_socket.sendto(message.encode(), address)
    
    elif message == "bye" and name != "":
        client_socket.sendto(message.encode(), address)
        # Aguarda um curto período de tempo para dar tempo ao servidor
        # de processar a mensagem antes de fechar a conexão
        time.sleep(0.1)

        client_socket.close()
        name = ""
        exit()

    elif name != "":
        path_to_message = Path(message)
       # packet_count = get_file_packet_count(path_to_message, 1024)
        with open(path_to_message, "rb") as file:
            data = file.read(1024)
            while data:
                client_socket.sendto(data, address)
                print(f'enviado: {data}')
                data = file.read(1024)
        client_socket.sendto("\\x00".encode(), address)

    else:
        print("Para se conectar ao servidor, digite hi, meu nome eh (seu nome)")
    time.sleep(0.001)
