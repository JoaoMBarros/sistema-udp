import socket

client_ip = socket.gethostbyname(socket.gethostname())
router_ip = socket.gethostbyname(socket.gethostname())

router = (router_ip, 8200)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind((client_ip, 8300))

messages_para_envio = ['11110111000111101100011110111010', '11110000000111101100000010111010', '11110111111111101111111110111010',
'11111111100111111100111110111111', '00000111000111101100000110111010']
mensagens_enviadas = []

COMPRIMENTO_PACOTE = 97 #16 bits de cada campo do endereço de origem, destino, comprimento, checksum + 1 bit do numero de sequencia + 32 bits de dados
CHECKSUM_DIVISAO = 4
controle = 1

def find_check_sum(dados):
    soma = 0
    dados = bin(dados)[2:].zfill(32)

    index_divisao = int(len(dados)/CHECKSUM_DIVISAO)
    for i in range(0, CHECKSUM_DIVISAO):
        soma += int(dados[:index_divisao], 2)
        dados = dados[index_divisao:]

    soma = bin(soma)[2:]

    if len(soma) > 16:
        overflow_bits = len(soma) - 16
        soma = bin(int(soma[0:overflow_bits], 2) + int(soma[overflow_bits:], 2))[2:].zfill(16)

    #Calcula o complemento de 2 da soma
    checksum = ''
    for i in soma:
        if i == '1':
            checksum += '0'
        else:
            checksum += '1'

    return int(checksum, 2)

def cria_pacote(portaorigem, portadestino, COMPRIMENTO_PACOTE, checksum, numseq, dado):
    pacote = portaorigem[2:].zfill(16) + portadestino[2:].zfill(16) + bin(COMPRIMENTO_PACOTE)[2:].zfill(16)+bin(checksum)[2:].zfill(16)+bin(numseq)[2:].zfill(1)+bin(int(dado, 2))[2:].zfill(32)
    return pacote

while True:

        #Usando 100 e 101 como números fictícios pra conseguir redirecionar, já que o ip utilizando a funcao gethost vai ser o mesmo
        portaorigem = bin(100)
        portadestino = bin(101)
        
        try:
            checksum = find_check_sum(int(messages_para_envio[0], 2))

            if controle == 1:
                numseq = 0
            else:
                numseq = 1

            pacote = cria_pacote(portaorigem, portadestino, COMPRIMENTO_PACOTE, checksum, numseq, messages_para_envio[0])
            print('---------------- Pacote criado ----------------')
            print(f'Endereço de origem: {int(portaorigem[2:], 2)}\nEndereço de destino: {int(portadestino[2:], 2)}\nMensagem: {messages_para_envio[0]}')
            print('------------------------------------------------')
            client.sendto(pacote.encode('utf-8'), (router))

            print('Pacote enviado. Temporizador iniciado.')
            client.settimeout(10)

            received_bytes = client.recv(1024)
            received_message = received_bytes.decode('utf-8')

            portaorigem = int(received_bytes[0:16], 2)
            portadestino = int(received_bytes[16:32], 2)
            comprimento = int(received_bytes[32:48],2)
            checksum = int(received_bytes[48:64], 2)
            ack = int(received_bytes[64:65],2)
            dados = int(received_bytes[65:97], 2)

            checksum_recebido = find_check_sum(dados)

            if checksum_recebido != checksum or ack == controle:
                print('Ack indicando erro no pacote enviado. Reenviando')

            else:
                print('Ack confirmando recebimento do pacote. Enviando próximo pacote')
                mensagens_enviadas.append(messages_para_envio.pop(0))
                controle = ack

            continue

        except socket.timeout:
            print('Estouro do temporizador. Reenviando pacote')
            continue