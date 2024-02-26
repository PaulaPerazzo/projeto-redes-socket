from socket import *
from threading import *
from queue import *
from datetime import datetime
from Checksum import ip_checksum
import time

# cria uma fila para armazenar as mensagens recebidas
messages = Queue()
# lista para armazenar os endereços dos clientes conectados
clients = []

# configurações do servidor
server_port = 9999
host_name = gethostname()
server_address = gethostbyname(host_name)

# cria um socket udp para o servidor e atribui um endereço e uma porta
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((server_address, server_port))

# imprime uma mensagem indicando que o servidor está pronto
print("Servidor conectado!")

# função para receber mensagens dos clientes

timeout_test = True

def receive():
    while True:
        expect_seq = 0
        try:
            # recebe uma mensagem e o endereço do remetente e coloca a mensagem com endereço na fila
            message, addr = server_socket.recvfrom(1024)
            message2 = message.decode("utf-8")
            print(message2)
            checksum = message2[:2]
            seq = message2[2]
            pkt = message2[3:]
            if not message:
                break
            if ip_checksum(pkt) == checksum and seq == str(expect_seq):
                print('recv: Good Data Sending ACK' + str(seq))
                print('recv pkt: ' + str(pkt))
                messages.put((message, addr))
                
                server_socket.sendto(("ACK" + str(seq)).encode(), addr)
                expect_seq = 1 - expect_seq
            else:
        # Check seq and send according ACK
                if seq == str(expect_seq):
                    print('recv: Bad Checksum Not Sending')
                else:
                    print('recv: Bad Seq Sending ACK' + str(1 - expect_seq))
                    server_socket.sendto((str(1 - expect_seq)).encode(), addr)

        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")

# função para processar as mensagens


def process_message(decoded_message, addr):
    # verifica se o endereço do cliente está entre os clientes conectados
    if addr not in [client[0] for client in clients]:
        # verifica se a mensagem é para adicioanr um novo cliente e se sim, retorna o nome
        if decoded_message.startswith("hi, meu nome eh "):
            name = decoded_message[len("hi, meu nome eh "):]
            clients.append((addr, name))
            return name
    return None

# função para manipular os arquivos


def handle_file(message, addr, name):
    # formata o cabeçalho e adiciona-o à lista de envio
    formatted_message = f"{addr[0]}:{addr[1]}/~{name}: "
    lista_envios = []
    lista_envios.append(formatted_message)
    while message != "\\x00":
        # adiciona as partes da mensagem à lista de envio, recebe a próxima parte e a decodifica
        lista_envios.append(message)
        message, _ = messages.get()
        message = message.decode("utf-8")

    # adiciona a hora atual à lista de envio
    current_time = datetime.now().strftime(" %H:%M:%S %d/%m/%Y")
    lista_envios.append(current_time)
    # retorna a lista de envios
    return lista_envios


# função para transmitir mensagens para todos os clientes conectados
def broadcast():
    while True:
        # recebe uma mensagem e endereço de remetente
        message, addr = messages.get()
        # decodifica a mensagem
        decoded_message = message.decode()
        # cria uma lista para armazenar as mensagens a serem enviadas
        envio = []
        # verifica se é um novo cliente
        new_client = process_message(decoded_message, addr)

        if new_client:
            # em caso de novo cliente envia a mensagem para os demais avisando que um novo cliente entrou
            # e retorna para o usuário também informando que a entrada foi bem sucedida.
            envio.append(f"{new_client} entrou na sala")
            server_socket.sendto("Você entrou da sala".encode(), addr)
            server_socket.sendto("\\x00".encode(), addr)

        else:
            dicionario_clientes = dict(clients)
            nome = dicionario_clientes.get(addr)
            
            # verifica se a mensagem (não) é para sair do chat
            if decoded_message != "bye":
                envio = handle_file(decoded_message, addr, nome)
            else:
                # se sim, adiciona mensagens de saída,
                # envia um marcador de fim e remove o cliente da lista de clientes conectados
                envio.append(f"{nome} saiu da sala")
                server_socket.sendto("Você saiu da sala".encode(), addr)
                server_socket.sendto("\\x00".encode(), addr)
                
                clients.remove((addr, nome))

        print(f'Esses são os clientes: {clients}')
        # para cada cliente conectado, obtém o endereço do cliente
        for client in clients:
            client_addr, _ = client
            # verificação para a mensagem enviada por um cliente não ser reenviada para ele mesmo
            if client_addr == addr:
                pass
            else:
                # para cada pacote na lista de envio, envia o pacote ao cliente
                for pacote in envio:
                    server_socket.sendto(pacote.encode(), client_addr)
                # envia um marcador de fim de mensagem
                server_socket.sendto("\\x00".encode(), client_addr)


# cria duas threads para as funções receive e broadcast e as inicia
first_thread = Thread(target=receive)
second_thread = Thread(target=broadcast)

first_thread.start()

