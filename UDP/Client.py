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

print("---------------------")

print("BEM VINDO AO CHAT UDP")

print("---------------------")

verification = False

print("Para se conectar ao servidor, digite: hi, meu nome eh (seu nome)")

while verification == False:

    message = input("\nDigite: ")

    if message.startswith("hi, meu nome eh ") and not name:
        name = message[len("hi, meu nome eh "):]
        if name != "":
            client_socket.sendto(message.encode(), address)
            verification = True
        else:
            print("Nome inválido, digite novamente o comando.")
            pass
    else:
        print("Comando inválido, digite novamente!")

while True:
    time.sleep(1)

    print("\n(Para envio de um arquivo txt, \ndigite o caminho do mesmo em sua máquina)")
    print("\n(Para sair do chat, digite: bye)")

    message = input("\nDigite a mensagem: ")

    if message == "bye" and name != "":
        client_socket.sendto(message.encode(), address)
        # Aguarda um curto período de tempo para dar tempo ao servidor
        # de processar a mensagem antes de fechar a conexão
        time.sleep(0.1)

        client_socket.close()
        name = ""
        exit()

    elif name != "":
        path_to_message = Path(message)
        # Verifica se o arquivo tem a extensão .txt
        if path_to_message.suffix.lower() != '.txt':
            print("Erro: Por favor, envie um arquivo no formato .txt")
        else:
            with open(path_to_message, "rb") as file:
                data = file.read(1024)
                while data:
                    client_socket.sendto(data, address)
                    # print(f'enviado: {data}')
                    data = file.read(1024)
            # Enviando um marcador de fim de arquivo
            client_socket.sendto("\\x00".encode(), address)

    time.sleep(0.001)
