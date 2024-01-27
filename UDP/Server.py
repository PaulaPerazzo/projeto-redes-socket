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
            print(f"Mensagem recebida de {addr}")
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")

def process_message(decoded_message, addr):
    print("Entrou no process")
    if addr not in [client[0] for client in clients]:
        if decoded_message.startswith("hi, meu nome eh "):
            name = decoded_message[len("hi, meu nome eh "):]
            clients.append((addr, name))
            print(f"{name} entrou na sala")
            server_socket.sendto(f"Você entrou na sala com o nome {name}".encode(), addr)
    else:
        print(f"Cliente já conectado: {decoded_message}")

def handle_file(message, addr, name):
    print("Entrou no handle_file")
    mensagem_completa = message.decode()
    while "\x00" not in mensagem_completa:
        message, _ = messages.get()
        mensagem_completa += message.decode()
    print_message(mensagem_completa[:-3], addr, name)

def print_message(decoded_message, addr, name):
    print("Entrou no print_message")
    current_time = datetime.now().strftime("%H:%M:%S/%d/%m/%Y")
    formatted_message = f"{addr[0]}:{addr[1]}/~{name}: {decoded_message} {current_time}"
    print(formatted_message)
    server_socket.sendto(formatted_message.encode(), addr)

def broadcast():
    while True:
        print("Entrou no broadcasting")
        message, addr = messages.get()
        decoded_message = message.decode()

        process_message(decoded_message, addr)
        
        for client in clients:
            client_addr, client_name = client
            if decoded_message != "bye":
                handle_file(message, client_addr, client_name)
            else:
                clients.remove(client)
                print(f"{client_name} saiu da sala")
                server_socket.sendto("Você saiu da sala".encode(), client_addr)

print(f'Esses são os clientes: {clients}')
first_thread = Thread(target=receive)
second_thread = Thread(target=broadcast)

first_thread.start()
second_thread.start()
