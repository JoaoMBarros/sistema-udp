import socket

COMPRIMENTO_PACOTE = 97 #16 bits dos campos de ip origem, ip destino, checksum e comprimento + 1 bit do ack/checksum + 32 bits de dados
CHECKSUM_DIVISAO = 4
BUFFER_JANELA_DESLIZANTE = 485

server = socket.gethostbyname(socket.gethostname())
router = socket.gethostbyname(socket.gethostname())
router_2 = (router, 8200)
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Tipo de protocolo utilizado (AF_INET = ipv4) e tipo de conexao (SOCK_DGRAM = udp)
server.bind((server, 8000)) #Deixando meu socket "online"

ultimo_ack = 1
mensagens_recebidas = []

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

def cria_pacote(portaorigem, portadestino, comprimento, checksum, ack, dados):
    pacote = bin(portaorigem)[2:].zfill(16) + bin(portadestino)[2:].zfill(16) + bin(comprimento)[2:].zfill(16)+ bin(checksum)[2:].zfill(16) + bin(ack)[2:].zfill(1) + bin(dados)[2:].zfill(32)
    return pacote

while True:
    received_bytes = (server.recv(1024))
    received_bytes = received_bytes.decode('utf-8')
    
    portaorigem = int(received_bytes[0:16], 2)
    portadestino = int(received_bytes[16:32], 2)
    comprimento = int(received_bytes[32:48],2)
    checksum = int(received_bytes[48:64], 2)
    numseq = int(received_bytes[64:65],2)
    dado = int(received_bytes[65:97],2)

    if numseq == ultimo_ack:
        print('Pacote duplicado! Descartando e solicitando novamente')
        checksum = find_check_sum(dado)
        pacote = cria_pacote(101, 100, comprimento, checksum, ultimo_ack, int(mensagens_recebidas[-1], 2))
        server.sendto(pacote.encode(), (router_2))

    else:
        #Calculando o checksum do pacote que chegou do cliente
        checksum_recebido = find_check_sum(dado)

        #Verificando se o checksum que acabou de ser calculado bate com o checksum que foi calculado e enviado pelo cliente
        if checksum_recebido != checksum:
            print('Pacote corrompido! Descartando e solicitando novamente')
            checksum = find_check_sum(dado)
            pacote = cria_pacote(101, 100, comprimento, checksum, ultimo_ack, int(mensagens_recebidas[-1], 2))
            server.sendto(pacote.encode(), (router_2))

        else:
            print('Pacote recebido com sucesso!.')
            print('---------------- Dados do pacote ----------------')
            print(f'Endereço de origem: {portaorigem}\nEndereço de destino: {portadestino}\nMensagem: {bin(dado)[2:]}')
            checksum = find_check_sum(dado)
            mensagens_recebidas.append(bin(dado)[2:])

            if numseq == 1:
                ack = 1
            else:
                ack = 0

            pacote = cria_pacote(101, 100, COMPRIMENTO_PACOTE, checksum, ack, int(mensagens_recebidas[-1], 2))
            server.sendto(pacote.encode(), (router_2))
            ultimo_ack = numseq

    print('Mensagens recebidas até o momento: {}'.format(mensagens_recebidas))
    continue