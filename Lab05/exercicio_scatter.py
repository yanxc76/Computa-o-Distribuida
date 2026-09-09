from mpi4py import MPI
import random

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def gerar_logs(qtd):
    ips = [f"192.168.1.{i}" for i in range(1, 255)]
    endpoints = ["/", "/login", "/products", "/cart", "/checkout", "/api/users", "/api/orders"]
    metodos = ["GET", "POST"]
    status = ["200", "200", "200", "404", "500"]

    logs = []
    for _ in range(qtd):
        ip = random.choice(ips)
        metodo = random.choice(metodos)
        endpoint = random.choice(endpoints)
        cod_status = random.choice(status)
        linha = f"{ip} {metodo} {endpoint} {cod_status}"
        logs.append(linha)
    return logs

logs_divididos = None
TOTAL_LOGS = 1000000

if rank == 0:
    print("\nGerando dataset de logs...\n")
    logs = gerar_logs(TOTAL_LOGS)
    tamanho_parte = len(logs) // size
    logs_divididos = [
        logs[i * tamanho_parte : (i + 1) * tamanho_parte]
        for i in range(size)
    ]

logs_locais = comm.scatter(logs_divididos, root=0)

erros = 0
for linha in logs_locais:
    campos = linha.split()
    cod_status = campos[3]
    if cod_status == "404" or cod_status == "500":
        erros += 1

print(
    f"Processo {rank} analisou {len(logs_locais)} linhas "
    f"e encontrou {erros} erros."
)