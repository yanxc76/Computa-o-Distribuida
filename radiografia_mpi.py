from mpi4py import MPI
import numpy as np
import random
import time
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# ============================================================
# PARÂMETROS DE CONFIGURAÇÃO
# (podem ser passados via linha de comando: python3 script.py LINHAS COLUNAS)
# ============================================================
LINHAS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
COLUNAS = int(sys.argv[2]) if len(sys.argv) > 2 else 2000

LIMIAR_SUSPEITA_LEVE = 200      # pixel > 200 -> suspeito
LIMIAR_SUSPEITA_ALTA = 230      # pixel > 230 -> altamente suspeito
PERCENTUAL_CRITICO = 5.0        # % de pixels suspeitos para considerar a faixa/exame crítico


# ============================================================
# ETAPA 2 - Geração da radiografia simulada (somente rank 0)
# ============================================================
def gerar_radiografia(linhas, colunas):
    """
    Gera uma radiografia simulada com uma estrutura coerente:
    - fundo externo do corpo (mais escuro)
    - região central do tórax (intensidade intermediária)
    - pulmão esquerdo e direito (mais escuros que o tórax)
    - manchas claras artificiais simulando áreas suspeitas
    """
    img = np.random.randint(15, 35, size=(linhas, colunas), dtype=np.int32)

    # Região central do tórax
    margem_v = max(1, int(linhas * 0.08))
    margem_h = max(1, int(colunas * 0.12))
    img[margem_v:linhas - margem_v, margem_h:colunas - margem_h] = np.random.randint(
        60, 95, size=(linhas - 2 * margem_v, colunas - 2 * margem_h)
    )

    # Pulmões (esquerdo e direito) - mais escuros que o tórax ao redor
    pulmao_topo = margem_v + int(linhas * 0.05)
    pulmao_base = linhas - margem_v - int(linhas * 0.05)
    pulmao_esq_ini = margem_h + int(colunas * 0.05)
    pulmao_esq_fim = colunas // 2 - int(colunas * 0.03)
    pulmao_dir_ini = colunas // 2 + int(colunas * 0.03)
    pulmao_dir_fim = colunas - margem_h - int(colunas * 0.05)

    img[pulmao_topo:pulmao_base, pulmao_esq_ini:pulmao_esq_fim] = np.random.randint(
        35, 60, size=(pulmao_base - pulmao_topo, pulmao_esq_fim - pulmao_esq_ini)
    )
    img[pulmao_topo:pulmao_base, pulmao_dir_ini:pulmao_dir_fim] = np.random.randint(
        35, 60, size=(pulmao_base - pulmao_topo, pulmao_dir_fim - pulmao_dir_ini)
    )

    # Manchas claras artificiais (áreas suspeitas) espalhadas pelos pulmões
    n_manchas = max(3, (linhas * colunas) // 400000)
    for _ in range(n_manchas):
        lado = random.choice(["esq", "dir"])
        if lado == "esq":
            cy = random.randint(pulmao_topo, pulmao_base - 1)
            cx = random.randint(pulmao_esq_ini, pulmao_esq_fim - 1)
        else:
            cy = random.randint(pulmao_topo, pulmao_base - 1)
            cx = random.randint(pulmao_dir_ini, pulmao_dir_fim - 1)

        raio = random.randint(3, max(4, min(linhas, colunas) // 60))
        intensidade = random.randint(205, 255)

        y0, y1 = max(0, cy - raio), min(linhas, cy + raio)
        x0, x1 = max(0, cx - raio), min(colunas, cx + raio)
        img[y0:y1, x0:x1] = intensidade

    return img


# ============================================================
# ETAPA 1 - Inicialização (todos já sabem rank e size acima)
# ============================================================
tempo_inicio = None
imagem = None

if rank == 0:
    tempo_inicio = time.time()
    print(f"\n[ROOT] Gerando radiografia simulada {LINHAS}x{COLUNAS} pixels...\n")
    imagem = gerar_radiografia(LINHAS, COLUNAS)

# ============================================================
# ETAPA 3 - BROADCAST dos parâmetros de análise
# ============================================================
if rank == 0:
    parametros = {
        "linhas": LINHAS,
        "colunas": COLUNAS,
        "limiar_leve": LIMIAR_SUSPEITA_LEVE,
        "limiar_alta": LIMIAR_SUSPEITA_ALTA,
        "percentual_critico": PERCENTUAL_CRITICO,
    }
else:
    parametros = None

parametros = comm.bcast(parametros, root=0)

LINHAS = parametros["linhas"]
COLUNAS = parametros["colunas"]
LIMIAR_SUSPEITA_LEVE = parametros["limiar_leve"]
LIMIAR_SUSPEITA_ALTA = parametros["limiar_alta"]
PERCENTUAL_CRITICO = parametros["percentual_critico"]

# ============================================================
# ETAPA 4 - BARRIER: garante que todos já têm os parâmetros
# antes de iniciar a etapa de análise
# ============================================================
comm.Barrier()

# ============================================================
# ETAPA 5 - Divisão da radiografia por faixas de linhas + SCATTER
# (trata o caso em que LINHAS não é divisível por size,
#  distribuindo o resto entre os primeiros processos)
# ============================================================
if rank == 0:
    linhas_por_processo = LINHAS // size
    resto = LINHAS % size

    partes_imagem = []
    faixas_indices = []
    inicio = 0
    for i in range(size):
        qtd = linhas_por_processo + (1 if i < resto else 0)
        fim = inicio + qtd
        faixas_indices.append((inicio, fim))
        partes_imagem.append(imagem[inicio:fim, :])
        inicio = fim
else:
    partes_imagem = None
    faixas_indices = None

minha_faixa = comm.scatter(partes_imagem, root=0)
linha_ini, linha_fim = comm.scatter(faixas_indices, root=0)

# ============================================================
# ETAPA 6 - Análise local de cada processo
# ============================================================
total_pixels_local = minha_faixa.size
soma_local = int(minha_faixa.sum())
media_local = soma_local / total_pixels_local
maior_local = int(minha_faixa.max())

suspeitos_local = int(np.sum(minha_faixa > LIMIAR_SUSPEITA_LEVE))
altos_local = int(np.sum(minha_faixa > LIMIAR_SUSPEITA_ALTA))

metade = COLUNAS // 2
pulmao_esquerdo_local = minha_faixa[:, :metade]
pulmao_direito_local = minha_faixa[:, metade:]

suspeitos_esquerdo_local = int(np.sum(pulmao_esquerdo_local > LIMIAR_SUSPEITA_LEVE))
suspeitos_direito_local = int(np.sum(pulmao_direito_local > LIMIAR_SUSPEITA_LEVE))

# ============================================================
# ETAPA 7 - Classificação local da faixa
# Regra (objetiva e documentada):
#   - se % de pixels ALTAMENTE suspeitos >= PERCENTUAL_CRITICO       -> "crítica"
#   - senão, se % de pixels suspeitos >= PERCENTUAL_CRITICO / 2      -> "atenção"
#   - caso contrário                                                 -> "normal"
# ============================================================
pct_altos_local = (altos_local / total_pixels_local) * 100
pct_suspeitos_local = (suspeitos_local / total_pixels_local) * 100

if pct_altos_local >= PERCENTUAL_CRITICO:
    classificacao_local = "crítica"
elif pct_suspeitos_local >= (PERCENTUAL_CRITICO / 2):
    classificacao_local = "atenção"
else:
    classificacao_local = "normal"

# ============================================================
# ETAPA 8 - Simulação de cluster heterogêneo
# Processos de rank ímpar simulam uma máquina mais lenta.
# Feito DEPOIS do processamento local e ANTES da consolidação.
# ============================================================
if rank % 2 == 1:
    atraso = random.uniform(0.5, 2.0)
    time.sleep(atraso)

# ============================================================
# ETAPA 9 - BARRIER antes da consolidação
# Garante que todos terminaram a análise local (incluindo o atraso
# artificial) antes de qualquer processo seguir para o Reduce/Gather.
# ============================================================
comm.Barrier()

# ============================================================
# ETAPA 10 - Consolidação numérica com REDUCE
# ============================================================
total_pixels_global = comm.reduce(total_pixels_local, op=MPI.SUM, root=0)
soma_global = comm.reduce(soma_local, op=MPI.SUM, root=0)
total_suspeitos_global = comm.reduce(suspeitos_local, op=MPI.SUM, root=0)
total_altos_global = comm.reduce(altos_local, op=MPI.SUM, root=0)
total_suspeitos_esquerdo = comm.reduce(suspeitos_esquerdo_local, op=MPI.SUM, root=0)
total_suspeitos_direito = comm.reduce(suspeitos_direito_local, op=MPI.SUM, root=0)
maior_intensidade_global = comm.reduce(maior_local, op=MPI.MAX, root=0)

# ============================================================
# ETAPA 11 - Coleta de estatísticas detalhadas com GATHER
# ============================================================
relatorio_local = {
    "rank": rank,
    "linha_inicio": linha_ini,
    "linha_fim": linha_fim,
    "pixels_analisados": total_pixels_local,
    "suspeitos": suspeitos_local,
    "altamente_suspeitos": altos_local,
    "maior_intensidade": maior_local,
    "classificacao": classificacao_local,
}

relatorios = comm.gather(relatorio_local, root=0)

# ============================================================
# ETAPA 12 - Relatório final (somente root)
# ============================================================
if rank == 0:
    tempo_fim = time.time()

    media_global = soma_global / total_pixels_global
    pct_suspeitos_global = (total_suspeitos_global / total_pixels_global) * 100
    pct_altos_global = (total_altos_global / total_pixels_global) * 100

    if total_suspeitos_esquerdo > total_suspeitos_direito:
        lado_mais_afetado = "ESQUERDO"
    elif total_suspeitos_direito > total_suspeitos_esquerdo:
        lado_mais_afetado = "DIREITO"
    else:
        lado_mais_afetado = "EMPATE"

    # Classificação geral do exame (mesma lógica da classificação local,
    # aplicada aos totais globais)
    if pct_altos_global >= PERCENTUAL_CRITICO:
        classificacao_geral = "exame com alta concentração de áreas suspeitas"
    elif pct_suspeitos_global >= (PERCENTUAL_CRITICO / 2):
        classificacao_geral = "atenção clínica"
    else:
        classificacao_geral = "sem indícios relevantes"

    print("=" * 78)
    print("RELATÓRIO FINAL - ANÁLISE DISTRIBUÍDA DE RADIOGRAFIA (SIMULAÇÃO)")
    print("=" * 78)
    print(f"Tamanho da imagem............: {LINHAS} x {COLUNAS} pixels")
    print(f"Quantidade de processos MPI..: {size}")
    print(f"Limiar de suspeita leve......: {LIMIAR_SUSPEITA_LEVE}")
    print(f"Limiar de suspeita alta......: {LIMIAR_SUSPEITA_ALTA}")
    print(f"Percentual crítico definido..: {PERCENTUAL_CRITICO}%")
    print(f"Tempo total de execução......: {(tempo_fim - tempo_inicio) * 1000:.2f} ms")
    print("-" * 78)
    print("ESTATÍSTICAS GLOBAIS")
    print(f"  Total de pixels analisados..........: {total_pixels_global}")
    print(f"  Intensidade média global.............: {media_global:.2f}")
    print(f"  Maior intensidade global.............: {maior_intensidade_global}")
    print(f"  Total de pixels suspeitos............: {total_suspeitos_global} ({pct_suspeitos_global:.3f}%)")
    print(f"  Total de pixels altamente suspeitos..: {total_altos_global} ({pct_altos_global:.3f}%)")
    print("-" * 78)
    print("COMPARAÇÃO ENTRE OS LADOS DO PULMÃO")
    print(f"  Suspeitos pulmão ESQUERDO............: {total_suspeitos_esquerdo}")
    print(f"  Suspeitos pulmão DIREITO.............: {total_suspeitos_direito}")
    print(f"  Lado com maior concentração..........: {lado_mais_afetado}")
    print("-" * 78)
    print("ESTATÍSTICAS POR PROCESSO")
    for r in relatorios:
        print(
            f"  Processo {r['rank']:>2} | linhas {r['linha_inicio']:>6}-{r['linha_fim']:<6} | "
            f"pixels: {r['pixels_analisados']:>9} | suspeitos: {r['suspeitos']:>6} | "
            f"altos: {r['altamente_suspeitos']:>5} | max: {r['maior_intensidade']:>3} | "
            f"classificação: {r['classificacao']}"
        )
    print("-" * 78)
    print(f"CLASSIFICAÇÃO GERAL DO EXAME (SIMULADO): {classificacao_geral.upper()}")
    print("=" * 78)
