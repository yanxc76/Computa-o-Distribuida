import socket
import threading
import sys

def receber_mensagens(s):
    # Essa função fica em loop infinito só ouvindo o servidor
    while True:
        try:
            resposta = s.recv(1024).decode("utf-8")
            if not resposta:
                break
            
            #para não ficar feio no terminal
            print(f"\n{resposta.strip()}")
            print(">> ", end="", flush=True)
        except:
            break
            
    print("\nConexão com o servidor encerrada.")
    s.close()
    sys.exit() # Fecha o programa

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect(("127.0.0.1", 5000))
    except:
        print("Erro ao conectar. O servidor está ligado?")
        return

    print("Conectado ao servidor de Leilão.")
    print("Digite um valor numérico para dar seu lance (ex: 500.00) ou /sair")

    # Inicia a thread que fica escutando os alertas do servidor
    t = threading.Thread(target=receber_mensagens, args=(s,))
    t.daemon = True # Morre junto com o programa principal
    t.start()

    while True:
        try:
            msg = input(">> ")
            if not msg:
                continue
                
            if msg.lower() == '/sair': 
                break

            s.sendall(msg.encode("utf-8"))
        except KeyboardInterrupt: # Ctrl+C
            break

    s.close()

if __name__ == "__main__":
    main()