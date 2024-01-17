from socket import *
from threading import *
from queue import *

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
print("server is ready to receive")

# função para receber mensagens dos clientes
def receive():
    while True:
        try:
            # recebe uma mensagem e o endereço do remetente e coloca a mensagem com endereço na fila
            message, addr = server_socket.recvfrom(2048)
            messages.put((message, addr))
        except:
            pass

# função para transmitir mensagens para todos os clientes conectados
def broadcast():
    while True:
        # verifica se há mensagens na fila
        while not messages.empty():
            # obtém a mensagem e o endereço do remetente, decodifica a mensagem e a exibe no servidor
            message, addr = messages.get()
            print(message.decode())

           
            if addr not in clients:
                clients.append(addr)
            
            
            for client in clients:
                try:
                    if message.decode().startswith("NICKNAME:"):
                        name = message.decode()[message.decode().index(":") + 1 :]
                        print(f"{name} entrou!")
                        server_socket.sendto(f"{name} entrou!".encode(), client)
                    else:
                        server_socket.sendto(message, client)
                
                except:
                    clients.remove(client)

# cria duas threads para as funções receive e broadcast e as inicia
first_thread = Thread(target=receive)
first_thread = Thread(target=receive)
second_thread = Thread(target=broadcast)

first_thread.start()
second_thread.start()
