[← Voltar ao perfil](https://github.com/yanxc76)

# Computação distribuída · Sockets, MPI e Docker

**Python · Sockets TCP · MPI · Open MPI · Docker Compose**

Laboratórios sobre comunicação cliente-servidor, distribuição de trabalho entre processos e infraestrutura para experimentos com MPI.

## Organização

| Caminho | Conteúdo |
| --- | --- |
| [Lab01/](Lab01/) | Exemplos de cliente e servidor TCP |
| [Lab04/](Lab04/) | Experimentos com MPI, matrizes e comparação de abordagens |
| [Lab05/exercicio_scatter.py](Lab05/exercicio_scatter.py) | Distribuição de logs sintéticos com `scatter` |
| [radiografia_mpi.py](radiografia_mpi.py) | Script adicional de exploração de MPI |
| [docker-compose.yml](docker-compose.yml) | Infraestrutura com um nó master e três workers |

## Cliente e servidor TCP

O primeiro exercício funciona com Python 3 e a biblioteca padrão. Em dois terminais, a partir da raiz do repositório:

```bash
# Terminal 1
python3 Lab01/Exc1/server.py
```

```bash
# Terminal 2
python3 Lab01/Exc1/client.py
```

O cliente conecta a `127.0.0.1:5000`. Um exemplo de mensagem é `PRECO;HGLG11`. As informações dos fundos são dados fixos de demonstração no servidor.

## Experimentos com MPI

Use Python 3, uma implementação MPI disponível no sistema e `mpi4py` no ambiente Python.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install mpi4py
mpiexec -n 4 python Lab04/exercicio1.py 100
```

Nesse experimento, o argumento `100` define a dimensão das matrizes. O processo de rank zero reúne os resultados e apresenta o tempo medido.

## Infraestrutura Docker

```bash
docker compose up --build -d
docker compose ps
```

O Compose cria os serviços `master`, `worker1`, `worker2` e `worker3`. A imagem prepara Open MPI e SSH; ela ainda não instala Python/`mpi4py` nem copia os scripts dos laboratórios. A execução dos exemplos Python dentro dos containers exige essa preparação adicional. As credenciais de demonstração da imagem são destinadas apenas ao laboratório local.

Material acadêmico para estudo de sistemas distribuídos.
