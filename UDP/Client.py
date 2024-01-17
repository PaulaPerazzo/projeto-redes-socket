from socket import *
from threading import *
import random

# obtem o nome do host local e seu endereço IP e define a porta do servidor 
host_name = gethostname()
server_name = gethostbyname(host_name)
server_port = 9999

# cria um socket UDP
client_socket = socket(AF_INET, SOCK_DGRAM)
# atribui um endereço IP e porta local aleatória para o socket do cliente
client_socket.bind((server_name, random.randint(8000, 9000)))

# solicita ao usuário um apelido (nickname)
name = input("NICKNAME: ")

# função que recebe as mensagens do servidor 
def receive():
    while True:
        try:
            # recebe uma mensagem de no máximo 2048 bytes
            message, _ = client_socket.recvfrom(2048)
            # exibe a mensagem decodificada
            print(message.decode())
        except:
            pass

# cria uma thread para a função de receber e a inicia
thread = Thread(target=receive)
thread.start()

# envia uma mensgame de boas-vindas ao servidor com o apelido fornecido pelo cliente
client_socket.sendto(f"bem vindo: {name}".encode(), (server_name, server_port))

# loop para enviar mensagens para o servidor
while True:
    # solicitação de mensagem ao cliente/usuário
    message = input("digite: ")

    # verificação para, caso o usuário digitar !q, informar que ele saiu, fechar o socket e encerrar o programa
    if message == "!q":
        client_socket.sendto(f"{name}: saiu da sala".encode(), (server_name, server_port))
        client_socket.close()
        exit()
    else:
        # envia a mensagem ao servidor no formato "apelido: mensagem"
        client_socket.sendto(f"{name}: {message}".encode(), (server_name, server_port))
