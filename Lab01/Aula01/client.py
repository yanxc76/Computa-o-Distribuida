import socket

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 5000))

    while True:
        # Recebe a mensagem do servidor
        data = s.recv(4096).decode()
        if not data: break
        
        # Se a mensagem terminar com ":" (pergunta), pede o input
        if data.endswith(": "):
            resposta = input(data) # Exibe a pergunta e lê a resposta
            s.sendall(resposta.encode())
        else:
            print(data) # Apenas exibe (Correto/Incorreto/Fim)

    s.close()

if __name__ == "__main__":
    main()