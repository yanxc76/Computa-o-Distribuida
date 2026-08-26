import socket

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 5000))

    print("Conectado ao servidor de FIIs.")
    print("Formato: COMANDO;TICKER  (ex: PRECO;HGLG11)")

    while True:
        # Recebe a mensagem do servidor
       msg = input(">> ")
       if not msg:
            continue

       s.sendall(msg.encode("utf-8"))

       resposta = s.recv(1024).decode("utf-8")
       print(resposta)

    s.close()

if __name__ == "__main__":
    main()