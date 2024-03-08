# Projeto de Redes - Socket UDP com rdt3
Projeto de Redes de Computadores CIn - UFPE.

## Client.py
O arquivo Client.py é responsável pela implementação do cliente no chat. Aqui está sua funcionalidade:

 - O cliente inicia uma conexão com o servidor usando um socket UDP.
 - Utiliza threads para lidar com a recepção contínua de mensagens do servidor.
 - Permite que o usuário envie mensagens em formato .txt para o servidor.
 - Antes do envio, um pacote é montado fazendo uma verificação pelo RDT3.
 - O nome do cliente é registrado no servidor quando ele se conecta pela primeira vez.
 - O cliente se conecta a partir da mensagem: "hi, meu nome eh [nome]".
 - O cliente pode se desconectar do servidor enviando a mensagem "bye".

 ### Execução
 Para executar o cliente, basta rodar o script Client.py. O cliente deve inserir o caminho para arquivos .txt. A mensagem deve ser iniciada com "hi, meu nome eh " seguido pelo seu nome para se registrar no servidor.

```bash
python Client.py
```

## Server.py
O arquivo Server.py é responsável pela implementação do servidor. Aqui estão algumas características principais do código:

 - O servidor recebe mensagens de vários clientes usando um socket UDP.
 - Utiliza threads para processar continuamente as mensagens recebidas e enviar respostas aos clientes.
 - Mantém uma lista de clientes conectados, associando cada cliente a um nome único.
 - Suporta o envio de arquivos no formato .txt entre os clientes.
 - Verifica o checksum dos pacotes para saber se ele foi corrompido
 - Atualiza todos os clientes quando um novo cliente se junta ou quando um cliente se desconecta.

 ### Execução
 Para executar o servidor, basta rodar o script Server.py. O servidor começará a receber mensagens e distribuí-las para os clientes conectados. Ele deve estar em exução antes da inicialização dos clientes.
 
 ``` bash
 python Server.py
 ```

## Requisitos
Certifique-se de ter Python 3 e as bibliotecas necessarias instaladas.

## Equipe
- [Cauê Marinho](https://github.com/Cawezinn)
- [Maria Beatriz Martins](https://github.com/mbmartns)
- [Maria Bezerra](https://github.com/mariabdma)
- [Maria Paula Perazzo](https://github.com/PaulaPerazzo)
