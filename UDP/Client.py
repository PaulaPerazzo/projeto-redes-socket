from socket import *
from threading import *
import random
from pathlib import Path


host_name = gethostname()
server_name = gethostbyname(host_name)
server_port = 9999

client_port = random.randint(8000, 9000)
client_socket = socket(AF_INET, SOCK_DGRAM)
address = (server_name, server_port)
client_socket.connect(address)


def receive():
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            print(message.decode())
        except:
            pass


thread = Thread(target=receive)
thread.start()

name = ""

while True:
    message = input("Digite: ")

    # if name not defined yet and message starts with name to be defined, o que acontece?
    # mensagem mandada define nome do cliente que entrou no servidor e salva esse nome em name
    if message.startswith("hi, meu nome eh ") and not name:
        name = message[len("hi, meu nome eh "):]
        
        client_socket.sendto(message.encode(), (address))
    
    # nome ja definido e mensagem bye, o que acontece? saída do cliente
    elif message == "bye" and name != "": # 
        client_socket.sendto(message.encode(), (address))
        client_socket.close()
        name = ""
        exit()

    # nome ja definido, mensagem não é de saída, o que aocntece? mensagem enviada aos clientes conectados (servidor)
    elif name != "":
        path_to_message = Path(message)
        with open(path_to_message, 'r') as arquivo:
            conteudo = arquivo.read()   

        conteudo += "\x00"  # Adiciona identificador de fim de mensagem
        client_socket.sendto(conteudo.encode(), (address))

    # caso não conectado ainda
    else:
        print("para se conectar ao servidor digite hi, meu nome eh (seu nome)")
        pass

# no codigo acima as mensagens recebidas como input só são enviadas caso o usuario esteja conectado a sala
# podemos fazer com que o servidor receba mensagens mesmo de usuarios que não estejam conectados a sala