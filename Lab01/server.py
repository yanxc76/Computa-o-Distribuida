import socket

HOST = "0.0.0.0"
PORT = 5000

FIIS = {
    "HGLG11": {"preco": 165.50, "provento": 1.10},
    "KNRI11": {"preco": 148.30, "provento": 0.75},
    "MXRF11": {"preco": 10.25, "provento": 0.09},
    "XPML11": {"preco": 112.80, "provento": 0.85},
    "VISC11": {"preco": 115.50, "provento": 0.70},
    "BCFF11": {"preco": 68.40, "provento": 0.45},
    "HGRE11": {"preco": 130.20, "provento": 0.95},
    "RECT11": {"preco": 88.60, "provento": 0.60},
    "GGRC11": {"preco": 9.80, "provento": 0.08},
    "IRDM11": {"preco": 95.30, "provento": 1.00},
}


def processsar_informacao(msg:str) -> str:
    partes = msg.strip().split(";")

    if len(partes) != 2:
        return "Coamndo Inválido"
    
    comando, ticker = partes
    comando = comando.strip().upper()
    ticker = ticker.strip().upper()

    if comando not in ("PRECO", "PROVENTO", "STATUS"):
        return "Comando Inválido! Insira outro"
    
    if ticker not in FIIS:
        return "FIIS nao encontrados"
    
    dados = FIIS[ticker]

    if comando == "PRECO":
        return f"{dados['preco']}"
    
    elif comando == "PROVENTO":
        return f"{dados['provento']}"
    
    else:
        return f"PRECO = {dados['preco']} PROVENTO = {dados['provento']}"
    

def atende(conn, addr):

    print(f"Clinte conectou: {addr}")

    while True:
        dados = conn.recv(1024)
        if not dados:
            break
        
        msg = dados.decode("utf-8")
        print(f"Recebido msg de {addr}: {msg} ")

        resposta = processsar_informacao(msg)
        conn.sendall(resposta.encode("utf-8"))

    
    print(f"Cliente {addr} desconectado\n")




def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1) # Fila pequena para demonstrar o limite
    
    print(f"Servidor Quiz (Sem Threads) ouvindo em {PORT}...")
    print("Aviso: Apenas um cliente por vez será atendido.")

    while True:
        conn, addr = s.accept()
        print(f"Atendendo agora: {addr}")
        
        atende(conn,addr) # O código "trava" aqui até a função terminar
        
        conn.close()
        print(f"Cliente {addr} finalizado. Pronto para o próximo.\n")

if __name__ == "__main__":
    main()