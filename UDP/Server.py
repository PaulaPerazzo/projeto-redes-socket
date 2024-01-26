from socket import *
from threading import *
from queue import *
from datetime import datetime


messages = Queue()
clients = []
file_packets = {}

server_port = 9999
host_name = gethostname()
server_address = gethostbyname(host_name)

server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((server_address, server_port))
print("server is ready to receive")

def receive():
    while True:
        try:
            message, addr = server_socket.recvfrom(1024)
            messages.put((message, addr))
            #server_socket.sendto(f"mensagem recebida".encode(), addr)
            # print(f"{messages} <<<-------- messages = message, addr. é uma queue")
        except:
            pass


def process_message(message, addr):
    decoded_message = message.decode()
    if decoded_message.startswith("hi, meu nome eh "):
        name = decoded_message[len("hi, meu nome eh "):]
        clients.append((addr, name))
        print(f"{name} entrou na sala")
        server_socket.sendto(f"você, entrou na sala com o nome {name}".encode(), addr) # funciona

    else:
        pass

# função para reconstruir a mensagem enviada pelo cliente        
def handle_file(file_content, addr, name):
    if addr not in file_packets:
        file_packets[addr] = []


    file_packets[addr].append(file_content)
    # Concatenar os pacotes para reconstruir o arquivo completo
    message = file_packets[addr]    # message = b''.join(file_packets[addr]) #trocar b por file {addr}
    # Limpar os pacotes após reconstruir o arquivo
    del file_packets[addr] #testar se esta deletando o endereço ou as mensagens
    #deletar in messages 
    
    print_message(message, addr, name)


# printar no formato adequado
def print_message(decoded_message, addr, name):
    current_time = datetime.now().strftime("%H:%M:%S/%d/%m/%Y")
    formatted_message = f"{addr[0]}:{addr[1]}/~{name}: {decoded_message} {current_time}"
    print(formatted_message)
    server_socket.sendto(formatted_message.encode(), addr) #acho qye n funciona

def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            #message.decode()

            if addr not in [client[0] for client in clients]:
                process_message(message, addr)
            else:
                for client in clients: #rod -1, bia -2
                    client_addr, client_name = client
                    if message.decode() != "bye":
                        handle_file(messages, addr, client_name) # message(s)
                    else:
                        clients.remove(client)
                        print(f"{client_name} saiu da sala")
                        server_socket.sendto("Você saiu da sala".encode(), client_addr)

print(f' esses sao os clientes: {clients}')
first_thread = Thread(target=receive)
second_thread = Thread(target=broadcast)

first_thread.start()
second_thread.start()
