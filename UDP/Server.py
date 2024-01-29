from socket import *
from threading import *
from queue import *
from datetime import datetime

messages = Queue()
clients = []


server_port = 9999
host_name = gethostname()
server_address = gethostbyname(host_name)

server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((server_address, server_port))
print("Server is ready to receive")

def receive():
    while True:
        try:
            message, addr = server_socket.recvfrom(1024)
            messages.put((message, addr))
            #print(f"Mensagem recebida de {addr}")
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")

        
def process_message(decoded_message, addr):
    if addr not in [client[0] for client in clients]:
        if decoded_message.startswith("hi, meu nome eh "):
            name = decoded_message[len("hi, meu nome eh "):]
            clients.append((addr, name))
            return name
    return None


def handle_file(message, addr, name):
    formatted_message = f"{addr[0]}:{addr[1]}/~{name}: "
    lista_envios = []
    lista_envios.append(formatted_message)
    while  message != "\\x00":
        lista_envios.append(message)
        message, _ = messages.get()
        message = message.decode("utf-8")

    current_time = datetime.now().strftime(" %H:%M:%S %d/%m/%Y")
    lista_envios.append(current_time)

    return lista_envios



def broadcast():
    while True:
        message, addr = messages.get()
        decoded_message = message.decode()
        envio = []

        new_client = process_message(decoded_message, addr)

        if new_client:
            envio.append(f"{new_client} entrou na sala")
            server_socket.sendto("Você entrou da sala".encode(), addr)
            server_socket.sendto("\\x00".encode(), addr)

        else:
            dicionario_clientes = dict(clients)
            nome = dicionario_clientes.get(addr)
            print(f'o nome de quem enviou é {nome}')
            print(f'o dicionario esta assim: {dicionario_clientes}')
            if decoded_message != "bye":
                envio = handle_file(decoded_message, addr, nome)
            else:
                envio.append(f"{nome} saiu da sala")
                server_socket.sendto("Você saiu da sala".encode(), addr)
                server_socket.sendto("\\x00".encode(), addr)
                print((addr, nome))
                clients.remove((addr, nome))
                
        print(f'Esses são os clientes: {clients}')
        for client in clients:
            client_addr, _ = client
            if client_addr == addr:
                pass
            else:
                
                for pacote in envio:
                    server_socket.sendto(pacote.encode(), client_addr)
                server_socket.sendto("\\x00".encode(), client_addr)


first_thread = Thread(target=receive)
second_thread = Thread(target=broadcast)

first_thread.start()
second_thread.start()
