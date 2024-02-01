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


def receive(): #função pra receber
    complete_message = "" 
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            decoded_message = message.decode()
            if decoded_message != "\\x00": # se o pacote tiver apenas esse marcador, ele para de add na mensagem completa que ira printar
                complete_message += decoded_message
            else:
                print(complete_message)
                if complete_message != "Você entrou da sala" and complete_message != "Você saiu da sala":
                    print("Digite: ")
                complete_message = "" # a mensagem fica vazia depois que printada

        except:
            pass

thread = Thread(target=receive)
thread.start()

# uma ideia é mandar um print explicando como o cliente faz pahira se conectar antes do loop de digite

while True:
    message = input("Digite: ")

    if message.startswith("hi, meu nome eh ") and not name: # se a mensagem for o comando de entrada e n tiver se conectado 
        name = message[len("hi, meu nome eh "):]
        client_socket.sendto(message.encode(), address)
#fazer um elif pra se mandar o comando de entrada e tiver conectado (and name), printar que ele já esta conectado   
    elif message.startswith(f"hi, meu nome eh {name}") and name: # se a mensagem for o comando de entrada e cliente tiver conectado 
        print("Você já está conectado") # se quiser melhorar... falar, mande um arquivo txt e etc sla
    elif message == "bye" and name != "": #se ele quiser sair faz isso
        client_socket.sendto(message.encode(), address) #mandando que quer sair
        # Aguarda um curto período de tempo para dar tempo ao servidor
        # de processar a mensagem antes de fechar a conexão
        time.sleep(0.1) # tempo pra ele receber mensagem do socket dizendo que saiu antes de se desconectar

        client_socket.close() # fechou a conexão com o socket
        name = "" 
        exit() 

    elif name != "": #se ele estiver conectado, existe um name e as mensagens não são comandos de entrada ou saíde, o loop vem pra cá
        path_to_message = Path(message) # é esperado que se envie arquivos .txt
        # Verifica se o arquivo tem a extensão .txt
        if path_to_message.is_file() and path_to_message.suffix.lower() == '.txt': 
            with open(path_to_message, "rb") as file: #abre o arquvo, le como binario pra dividir em 1024 bytes o arq de texto
                data = file.read(1024) #data vai ser enviado, tem no maximo 1024 bytes
                while data:
                    client_socket.sendto(data, address) #enviando primeira parte da mensagem
                    data = file.read(1024) #lendo mais um pacote de 1024, pra enviar
            # Envie um marcador de fim de arquivo
            client_socket.sendto("\\x00".encode(), address)         # Enviando um marcador de fim de arquivo
# se quiser, pode adicionar um print pra esse cliente que enviou falando que sua mensagem foi enviada
        else:
            print("Erro: Por favor, envie um arquivo existente no formato .txt") #se for cliente, mas n enviar arquivo de texto

    else:
        print("Para se conectar ao servidor, digite hi, meu nome eh (seu nome)") #diz como se conecta, pode ajeitar se quiser
    time.sleep(0.001)
