import socket
import threading

HOST = "0.0.0.0"
PORT = 5000

# Variáveis globais 
clientes_conectados = []
maior_lance = 0.0

# O lock para evitar a Race Condition
lock = threading.Lock()

def atende(conn, addr):
    global maior_lance
    
    print(f"Clinte conectou: {addr}")
    clientes_conectados.append(conn)

    # Manda uma mensagem 
    conn.sendall(f"Bem vindo ao Leilao! Maior lance atual: R$ {maior_lance:.2f}\n".encode("utf-8"))

    while True:
        try:
            dados = conn.recv(1024)
            if not dados:
                break
            
            msg = dados.decode("utf-8").strip()
            print(f"Recebido lance de {addr}: {msg} ")

            # Tenta converter a mensagem pra número
            try:
                valor = float(msg)
            except ValueError:
                conn.sendall("Comando Inválido! Insira apenas numeros (ex: 500.00)\n".encode("utf-8"))
                continue

            # Trava a variável para evitar inconsistência de lances ao mesmo tempo
            with lock:
                if valor > maior_lance:
                    maior_lance = valor
                    
                    # Formata a mensagem de broadcast pedida
                    msg_broadcast = f"Novo lance, R$ {maior_lance:.2f} por {addr}\n"
                    print(msg_broadcast.strip())
                    
                    # Envia o broadcast para tds os clientes na lista
                    for c in clientes_conectados:
                        try:
                            c.sendall(msg_broadcast.encode("utf-8"))
                        except:
                            pass # Ignora se der erro de envio pra algum cliente que caiu
                else:
                    # Envia só pro remetente se o lance for baixo
                    conn.sendall("LANCE RECUSADO: Valor baixo\n".encode("utf-8"))

        except Exception as e:
            # Se deu algum erro na conexão, quebra o loop
            break
            
    print(f"Cliente {addr} desconectado\n")
    if conn in clientes_conectados:
        clientes_conectados.remove(conn)
    conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5) 
    
    print(f"Servidor Leilao (Com Threads) ouvindo em {PORT}...")

    while True:
        conn, addr = s.accept()
        print(f"Atendendo agora: {addr}")
        
        #atende(conn, addr) numa Thread separada
        t = threading.Thread(target=atende, args=(conn, addr))
        t.start()

if __name__ == "__main__":
    main()