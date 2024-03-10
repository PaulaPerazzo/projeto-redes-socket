from socket import *
from threading import *
import threading
from queue import *
from datetime import datetime
from Checksum import ip_checksum
import time

messages = Queue() # criação de fila para armazenar as mensagens
clients = [] # lista para armazenar os endereços dos clientes conectados

### configurações do servidor ###
server_port = 9999
host_name = gethostname()
server_address = gethostbyname(host_name)
server_socket = socket(AF_INET, SOCK_DGRAM) # criação de socket udp para o servidor
server_socket.bind((server_address, server_port)) # atribuição de endereço e porta

print("Servidor conectado!")

ack_recebido = threading.Event() # função para receber mensagens dos clientes
n_sequencia = None
seq = 0

### função three way handshake ###
def ThreeWayHandshake(client_message = "", client_address = ""):
    global seq

    while True:
        if client_message == "":
            syn_msg, client_address = server_socket.recvfrom(1024) # recebe SYN do primeiro cliente
            client_message = syn_msg.decode()

        if client_message == "SYN":
            print("SYN recebido do cliente, enviando SYN-ACK...")

            syn_ack_msg = "SYN-ACK"
            server_socket.sendto(syn_ack_msg.encode(), client_address) # envia SYN-ACK para o cliente

            time.sleep(0.01)

            ack_msg, _ = server_socket.recvfrom(1024) # verifica recebimento do ACK

            if ack_msg.decode() == "ACK":
                print("ACK recebido e conexão estabelecida pelo handshake") # ACK recebido e conexão ok

                seq = 1 # definição do proximo numero de sequencia
                break
        else:
            print("syn nao recebido")


### função para o recebimento de mensagem dos clientes ###
def receive():
    global n_sequencia
    while True:
        try:
            message, addr = server_socket.recvfrom(1024) # recebe mensagem e endereço do cliente
            decoded_message = message.decode() # mensagem decodificada
            
            if decoded_message == "SYN":
                n_seq = 0
                
                # no caso de não ser o primeiro cliente verificar o 3 way novamente
                ThreeWayHandshake(client_message=decoded_message, client_address=addr)
                process_message(decoded_message, addr)  # processa a mensagem para realizar o handshake

            if decoded_message == "ACK 0" or decoded_message == "ACK 1":
                n_sequencia = int(decoded_message[-1:]) # verificar qual foi o número do ACK recebido
                ack_recebido.set()

            else:
                if decoded_message != "SYN":
                    checksum = decoded_message[:2] # guardar valor de checksum
                    n_seq = decoded_message[2] # guardar num de sequencia
                    pkt = decoded_message[3:] # guardar o resto do pacote

                    # fazer checagem entre checksum recebido e esperado
                    if checksum == ip_checksum(pkt):
                        print(f'Checksum válido, enviando ACK {n_seq}')
                        messages.put((pkt, addr))
                        server_socket.sendto(("ACK " + str(n_seq)).encode(), addr)

                    else:
                        server_socket.sendto(("ACK " + str(1 - int(n_seq))).encode(), addr)
                        if decoded_message != "SYN":
                            print("Erro: checksum inválido")
            
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")


### função para processar a mensagem de um novo usuário ###
def process_message(decoded_message, addr):
    # verifica se o endereço do cliente está entre os clientes conectados
    if addr not in [client[0] for client in clients]:
        # verifica se a mensagem é para adicioanr um novo cliente e se sim, retorna o nome
        if decoded_message.startswith("hi, meu nome eh ") and decoded_message != "SYN":
            name = decoded_message[len("hi, meu nome eh "):]
            clients.append((addr, name)) # adição de novo cliente à lista
            return name
    return None

### função para manipular os arquivos e colocar a mensagem na formatação adequada ###
def handle_file(message, addr, name):
    # formata o cabeçalho e adiciona-o à lista de envio
    formatted_message = f"{addr[0]}:{addr[1]}/~{name}: "
    lista_envios = []
    lista_envios.append(formatted_message)
    while message != "\\x00":
        # adiciona as partes da mensagem à lista de envio, recebe a próxima parte e a decodifica
        lista_envios.append(message)
        message, _ = messages.get()
        #message = message.decode("utf-8")

    # adiciona a hora atual à lista de envio
    current_time = datetime.now().strftime(" %H:%M:%S %d/%m/%Y")
    lista_envios.append(current_time)
    # retorna a lista de envios
    return lista_envios


### função de transmissão de mensagens ###
def broadcast():
    global seq
    while True:
        # recebe uma mensagem e endereço de remetente
        message, addr = messages.get()
        # decodifica a mensagem
       # decoded_message = message.decode()
        # cria uma lista para armazenar as mensagens a serem enviadas
        envio = []
        # verifica se é um novo cliente
        new_client = process_message(message, addr)

        if new_client:
            # em caso de novo cliente envia a mensagem para os demais avisando que um novo cliente entrou
            # e retorna para o usuário também informando que a entrada foi bem sucedida.
            envio.append(f"{new_client} entrou na sala")
            envio_com_rdt(seq, "Você entrou da sala", addr, new_client)
            seq = 1-seq
            envio_com_rdt(seq, "\\x00", addr, new_client)
            seq = 1-seq

        #não é um cliente novo, vai enviar o conteúdo da mensagem para todos os clientes
        else:
            dicionario_clientes = dict(clients)
            nome = dicionario_clientes.get(addr)
            print(f'o nome de quem enviou é {nome}')
            print(f'o dicionario está assim: {dicionario_clientes}')
            # verifica se a mensagem (não) é para sair do chat
           # if decoded_message != "bye":
            if message != "bye":
                envio = handle_file(message, addr, nome)

            #    envio = handle_file(decoded_message, addr, nome)
            else:
                # se sim, adiciona mensagens de saída,
                # envia um marcador de fim e remove o cliente da lista de clientes conectados
                envio.append(f"{nome} saiu da sala")
                envio_com_rdt(seq, "Você saiu da sala", addr, nome)
                seq = 1 - seq
                envio_com_rdt(seq, "\\x00", addr, nome)
                seq = 1 - seq

                #print((addr, nome))
                clients.remove((addr, nome))

        print(f'Esses são os clientes: {clients}')
        # para cada cliente conectado, obtém o endereço do cliente
        for client in clients:
            client_addr, nome = client
            # verificação para a mensagem enviada por um cliente não ser reenviada para ele mesmo
            if client_addr == addr:
                pass
            else:
                # para cada pacote na lista de envio, envia o pacote ao cliente
                for pacote in envio:
                    envio_com_rdt(seq, pacote, client_addr, nome)
                    seq = 1 - seq
                # envia um marcador de fim de mensagem
                envio_com_rdt(seq, "\\x00", client_addr, nome)
                seq = 1 - seq

### função de envio com rdt ###
def envio_com_rdt(seq, mensagem, address, nome):
    global n_sequencia

    ack = False
    while ack == False:
        #server_socket.sendto((check + n_seq + message.encode()), address)
        check = ip_checksum(mensagem).encode()
        n_seq = str(seq).encode()
        pacote = (check + n_seq + mensagem.encode())
        server_socket.sendto(pacote, address)
        #print(f'esperado: {seq} e chegado: {n_sequencia}' )

        if ack_recebido.wait(3): #acho que n basta usar o timer, pq ele pega o tempo do proximo?
            #n_sequencia = n_sequencia 
            time.sleep(0.1) #porque? nao precisa, porem faz com que a linha debaixo da igual
            #print(f'{n_sequencia} é o numero de sequencia recebido, {seq} é o esperado')
            # print(type(n_sequencia), "TYPE DE N_SEQUENCIA")
            # print(type(seq), "TYPE SEQ")
            # print(seq == n_sequencia)
            if n_sequencia == seq:
                ack = True
                print(f'ACK {seq} recebido => Mensagem recebida por {nome}')
            else:
                print(f'ACK {n_sequencia} recebido => Arquivo perdido, reenviando pacote para {nome}...')
        else:
            print('TIMEOUT Error, reenviando pacote...')
            pass


### iniciar o three way handshake antes de outras funções ###
handshake_thread = Thread(target=ThreeWayHandshake)
handshake_thread.start()
handshake_thread.join() # aguardar o handshake acabar antes de prosseguir
            
# cria duas threads para as funções receive e broadcast e as inicia
first_thread = Thread(target=receive)
second_thread = Thread(target=broadcast)

first_thread.start()
second_thread.start()
