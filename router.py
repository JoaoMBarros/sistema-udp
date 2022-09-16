import socket

router_ip_adress = socket.gethostbyname(socket.gethostname())

router = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
router.bind(('127.0.1.1', 8200))

router_2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
router_2.bind(('127.0.1.1', 8100))

tabela_de_enderecamento = {100:8300, 101:8000}

def opcoes():

	print ("\n----------------------------------------------")
	print ("\nOpções:")
	print ("\n1 - Enviar próximo pacote")
	print ("2 - Corromper envio do próximo pacote")
	print ("3 - Duplicar envio do próximo pacote")
	print ("4 - Descartar pacote")
	escolha = 0

	while (escolha<1 or escolha>4):
		escolha = int(input("Opção escolhida: "))
	return escolha

def send_data(received_bytes):
    portaorigem = int(received_bytes[0:16], 2)
    portadestino = int(received_bytes[16:32], 2)
    comprimento = int(received_bytes[32:48],2)
    checksum = int(received_bytes[48:64], 2)
    numseq_or_ack = int(received_bytes[64:65],2)
    dados = int(received_bytes[65:97], 2)


    print('---------------------- Pacote recebido ----------------------')
    print('Endereço de origem: {}\nEndereço de destino: {}'.format(portaorigem, portadestino))

    escolha = opcoes()

    if (escolha==2):
        dados = 100

    if (escolha==3):
        if numseq_or_ack == '0':
            numseq_or_ack = 1
        else:
            numseq_or_ack = 0
            
    if (escolha == 4):
        return

    pacote = bin(portaorigem)[2:].zfill(16) + bin(portadestino)[2:].zfill(16) + bin(comprimento)[2:].zfill(16)+bin(checksum)[2:].zfill(16)+bin(numseq_or_ack)[2:].zfill(1)+bin(dados)[2:].zfill(32)
        
    router_2.sendto(pacote.encode(), (router_ip_adress, tabela_de_enderecamento[portadestino]))


while True:
    while True:
        print('Aguardando pacote')
        received_bytes = router.recv(1024)
        received_bytes = received_bytes.decode('utf-8')
        send_data(received_bytes)