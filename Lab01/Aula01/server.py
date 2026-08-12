import socket

HOST = "0.0.0.0"
PORT = 5000

FUNDOS = {
   "HGLG11": {"Preco": 145.55, "Provento": 1.10},
    "KNRI11": {"Preco": 158.20, "Provento": 0.95},
    "MXRF11": {"Preco": 10.32, "Provento": 0.10},
    "PVBI11": {"Preco": 78.45, "Provento": 0.75},
    "KNCR11": {"Preco": 102.80, "Provento": 1.05},
    "ISNT11": {"Preco": 42.15, "Provento": 0.40},
    "BTLG11": {"Preco": 101.50, "Provento": 0.82},
    "KNIP11": {"Preco": 91.30, "Provento": 0.70},
    "CACR11": {"Preco": 98.75, "Provento": 1.00},
    "HRES11": {"Preco": 95.60, "Provento": 0.85}

}

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

servidor.bind((HOST, PORT))
servidor.listen(5)

print("Servidor aguardando conexoes...")

def jogar(conn):
    conn.sendall("\n--- BEM-VINDO AO QUIZ (MODO SEQUENCIAL) ---\n\n".encode())
    
    
    
       

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
        
        jogar(conn) # O código "trava" aqui até a função terminar
        
        conn.close()
        print(f"Cliente {addr} finalizado. Pronto para o próximo.\n")

if __name__ == "__main__":
    main()