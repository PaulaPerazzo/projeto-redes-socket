from socket import *
from threading import *
import random
from pathlib import Path
import os
import time
from Checksum import ip_checksum

# obtem o nome do host local e seu endereço IP e define a porta do servidor
host_name = gethostname()
server_name = gethostbyname(host_name)
server_port = 9999

# gera uma porta aleatória e cria um socket UDP para o cliente
client_port = random.randint(8000, 9000)
client_socket = socket(AF_INET, SOCK_DGRAM)
# define o endereço do servidor e o conecta ao cliente
address = (server_name, server_port)
client_socket.connect(address)
name = ""

client_socket.settimeout(3)

# função que recebe as mensagens do servidor


def receive():
    # variável para armazenar a mensagem completa
    complete_message = ""
    while True:
        try:
            # recebe e decodifica a mensagem recebida do servidor
            message, _ = client_socket.recvfrom(1024)
            decoded_message = message.decode()
            # verifica se a mensagem é um marcador de fim
            if decoded_message != "\\x00":
                # adiciona a mensagem decodificada à mensagem completa
                complete_message += decoded_message
            else:
                # imprime a mensagem completa e reinicia a variável para a próxima mensagem
                print(complete_message)
                if complete_message != "Você entrou da sala" and complete_message != "Você saiu da sala":
                    # Após receber uma mensagem, aparece uma mensagem de digite, caso não tenha sido uma mensagem advinda de um comando do cliente
                    print("Digite sua mensagem: ")
                complete_message = ""  # a mensagem fica vazia depois que printada
        except:
            pass


# cria uma thread para a função de receber e a inicia
thread = Thread(target=receive)
thread.start()

# mensagem de boas-vindas e instruções para conectar ao servidor
print("---------------------")

print("BEM VINDO AO CHAT UDP")

print("---------------------")

print("Para se conectar ao servidor, digite: hi, meu nome eh (seu nome)")

verification = False
seq = 0

checksum_test = True

while verification == False:

    # solicitação de input mensagem
    message = input("\nDigite: ")
    ack_received = False
    # verifica se a mensagem é para extrair o nome do usuário, e se o nome não está vazio
    if message.startswith("hi, meu nome eh ") and not name:
        name = message[len("hi, meu nome eh "):]
        if name != "":
            while not ack_received:
            # envia a mensagem para o servidor e altera a variável de verificaçãoq que indica conexão bem sucedida
                print('SENDING PACKAGE...')
                client_socket.sendto((ip_checksum(message) + str(seq) + message).encode(), address)
                
                try:
                    print('send: GETTING ACK')
                    reply, addr = client_socket.recvfrom(1024)
                    reply.decode("utf-8")
                    ack = reply[3]
                except timeout:
                    print('send: TIMEOUT')
                else:
                    print('Checking for ACK ' + str(seq))
                    if ack == str(seq):
                        ack_received = True
                        
            print('ACK FOUND, CHANGING SEQ')
            seq = 1 - seq
            verification = True
        else:
            # mensagem de erro para nome inválido
            print("Nome inválido, digite novamente o comando.")
            pass
    else:
        # mensagem de erro para comando inválido
        print("Comando inválido, digite novamente!")

# loop para enviar mensagens para o servidor
while True:
    # aguarda um segundo e imprime as instruções para envio de arquivo e saída do chat
    time.sleep(0.1)

    print("\n(Para envio de um arquivo txt, \ndigite o caminho do mesmo em sua máquina)")
    print("\n(Para sair do chat, digite: bye)")

    # recebe o input da mensagem
    message = input("\nDigite sua mensagem: ")

    # verifica se a mensagem é para sair do chat
    if message == "bye" and name != "":
        while not ack_received:
        # envia mensagem ao servidor
            client_socket.sendto(message.encode(), address)
            try:
                print('send: GETTING ACK')
                reply, addr = client_socket.recvfrom(1024)
                ack = reply[0]
            except timeout:
                print('send: TIMEOUT')
            else:
                print('Checking for ACK ' + str(seq))
                if ack == str(seq):
                    ack_received = True
        print('ACK FOUND, CHANGING SEQ')
        seq = 1 - seq
            # Aguarda um curto período de tempo para dar tempo ao servidor
            # de processar a mensagem antes de fechar a conexão
            
        time.sleep(0.1)

        # fecha o socket do cliente, reinicia o nome do usuário e sai do programa
        client_socket.close()
        name = ""
        exit()

    # verifica se o nome de usuário foi definido
    elif name != "":
        # cria um objeto path com o caminho do arquivo
        path_to_message = Path(message)
        # Verifica se o arquivo tem a extensão .txt
        if path_to_message.suffix.lower() != '.txt':
            print("Erro: Por favor, envie um arquivo no formato .txt")
        else:
            # abre o arquivo em modo de leitura e lê os primeiros 1024 bytes
            with open(path_to_message, "rb") as file:
                data = file.read(1024)
                # loop enquanto houver dados no arquivo para repetir a última operação
                while data:
                    while not ack_received:
                        client_socket.sendto(data, address)
                        try:
                            print('send: GETTING ACK')
                            reply, addr = client_socket.recvfrom(1024)
                            ack = reply[0]
                        except timeout:
                            print('send: TIMEOUT')
                        else:
                            print('Checking for ACK ' + str(seq))
                            if ack == str(seq):
                                ack_received = True
                    print('ACK FOUND, CHANGING SEQ')
                    seq = 1 - seq
                    data = file.read(1024)
            # Enviando um marcador de fim de arquivo
            client_socket.sendto("\\x00".encode(), address)

    time.sleep(0.001)
