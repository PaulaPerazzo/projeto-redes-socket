from socket import *
from threading import *
import threading
import random
from pathlib import Path
import os
import time
from Checksum import ip_checksum

host_name = gethostname() # obtem o nome do host local
server_name = gethostbyname(host_name) # define nome do server
server_port = 9999 # define porta do server

client_port = random.randint(8000, 9000) # define porta aleatoria para o cliente
client_socket = socket(AF_INET, SOCK_DGRAM) # cria um socket para o cliente
address = (server_name, server_port) # define endereço do server
client_socket.connect(address) # estabelece uma conexão
name = ""

### Criando um objeto de evento ###
ack_recebido = threading.Event()

### funcao do 3way handshake ###
def ThreeWayHandshake():
    time.sleep(0.01)
    syn_msg = "SYN"
    client_socket.sendto(syn_msg.encode(), address) # enviar o syn para o server
    print("SYN enviado...")

    time.sleep(0.01)
    syn_ack_msg, _ = client_socket.recvfrom(1024) # aguarda o syn-ack do servidor

    if syn_ack_msg.decode() == "SYN-ACK":
        print("SYN-ACK recebido, enviando ACK...")

        time.sleep(0.01)
        ack_msg = "ACK"
        client_socket.sendto(ack_msg.encode(), address) # envia ACK para o servidor
        time.sleep(0.01)
        print("conexão extabelecida pelo three way handshake")

### three way handshake antes de começar a receber e enviar mensagens ###
handshake_thread = Thread(target=ThreeWayHandshake)
handshake_thread.start()
handshake_thread.join() # aguarda o handshake ser estabelecido antes de continuar


#### função que recebe as mensagens do servidor ###
n_sequencia = None

def receive():
    global n_sequencia

    complete_message = "" # variável para armazenar a mensagem completa
    while True:
        try:
            message, _ = client_socket.recvfrom(1024) # recebe mensagens do server
            decoded_message = message.decode() # decodifica as mensagens do server

            if decoded_message == "ACK 0" or decoded_message == "ACK 1":
                n_sequencia = int(decoded_message[-1:]) # verifica o ACK recebido
                ack_recebido.set()

            else:
                checksum = decoded_message[:2]   
                n_seq = decoded_message[2]
                pkt = decoded_message[3:]

                if checksum == ip_checksum(pkt): 
                    if pkt != "\\x00": # verifica se a mensagem é um marcador de fim
                        complete_message += pkt # adiciona a mensagem decodificada à mensagem completa
                        print(f'Checksum válido, enviando ACK {n_seq}')
                        client_socket.sendto(("ACK " + str(n_seq)).encode(), address)

                    else:
                        print(complete_message) # imprime a mensagem completa e reinicia a variável para a próxima mensagem
                        if complete_message != "Você entrou da sala" and complete_message != "Você saiu da sala":
                        # Após receber uma mensagem, aparece uma mensagem de digite, caso não tenha sido uma mensagem advinda de um comando do cliente
                            print("Digite sua mensagem: ")
                        complete_message = ""  # a mensagem fica vazia depois que printada
                        #print(f'Checksum válido, enviando ACK {n_seq}')
                        client_socket.sendto(("ACK " + str(n_seq)).encode(), address)

                else:
                    client_socket.sendto(("ACK " + str(1 - int(n_seq))).encode(), address)
                    if (decoded_message != "SYN-ACK"):
                        print("Erro: checksum inválido")
        
        except:
            pass


### função de envio com RDT ###
def envio_com_rdt(seq, mensagem, address):
    global n_sequencia

    ack = False

    while ack == False:
        check = ip_checksum(mensagem).encode() # estabelece o checksum
        n_seq = str(seq).encode() # estabelece o num de sequencia
        pacote = (check + n_seq + mensagem.encode()) # monta o pacote
        client_socket.sendto(pacote, address) # envia o pacote para o servidor

        if ack_recebido.wait(3):
            time.sleep(0.1) 

            if n_sequencia == seq:
                ack = True
                print('Mensagem recebida')

            else:
                print('Arquivo perdido, reenviando pacote...')

        else:
            print('TIMEOUT Error, reenviando pacote...')
            pass


seq = 0

thread = Thread(target=receive) # cria uma thread para a função de recebimento
thread.start() # inicia a thread

# mensagem de boas-vindas e instruções para conectar ao servidor
print("---------------------")

print("BEM VINDO AO CHAT UDP")

print("---------------------")

verification = False

print("Para se conectar ao servidor, digite: hi, meu nome eh (seu nome)")

while verification == False:
    # solicitação de input mensagem
    message = input("\nDigite: ")

    # verifica se a mensagem é para extrair o nome do usuário, e se o nome não está vazio
    if message.startswith("hi, meu nome eh ") and not name:
        name = message[len("hi, meu nome eh "):]

        if name != "":
            # envia a mensagem com rdt para o servidor e altera a variável de verificaçãoq que indica conexão bem sucedida
            envio_com_rdt(seq, message, address)
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
        # envia mensagem ao servidor
        envio_com_rdt(seq, message, address)
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
                    envio_com_rdt(seq, data.decode(), address)
                    seq = 1 - seq
                    #client_socket.sendto(data, address)
                    data = file.read(1024)
                    
            # Enviando um marcador de fim de arquivo
            envio_com_rdt(seq,"\\x00", address)
            seq = 1 - seq

    time.sleep(1)
