#!/usr/bin/env python3
"""
Download da base de acidentes por animais peçonhentos (Sinan/DATASUS), 2000-2023.

Reproduz o procedimento utilizado em out/2025 para obter os arquivos anuais do
agravo ANIMALS (acidente por animais peçonhentos) via PySUS, salvando cada ano
como Parquet em ./sinan_animais/.

Uso:
    pip install pysus pandas pyarrow fastparquet
    python download_sinan.py

Depois de gerar os Parquet anuais, consolidar e limpar a base com
LimpezaDados.ipynb (gera a base analítica final utilizada no artigo:
3.354.030 notificações, 2007-2023).
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from pysus import SINAN

OUT_DIR = "sinan_animais"
ANOS = list(range(2000, 2024))  # 2000-2023
MAX_WORKERS = 4


def baixar_ano(ano: int) -> str:
    """Baixa os arquivos do agravo ANIMALS de um ano para OUT_DIR."""
    arquivos = sinan.get_files("ANIMALS", ano)
    if not arquivos:
        return f"{ano}: nenhum arquivo encontrado"
    sinan.download(arquivos, OUT_DIR)
    return f"{ano}: {len(arquivos)} arquivo(s)"


os.makedirs(OUT_DIR, exist_ok=True)

# Carrega o catálogo de arquivos disponíveis no DATASUS
sinan = SINAN().load()

resultados = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
    futures = {ex.submit(baixar_ano, ano): ano for ano in ANOS}
    for fut in as_completed(futures):
        ano = futures[fut]
        try:
            resultados.append(fut.result())
            print(f"[OK] {fut.result()}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"[ERRO] {ano}: {exc}", flush=True)

print(f"\nConcluído. Arquivos Parquet em ./{OUT_DIR}/")
print("Próximo passo: LimpezaDados.ipynb (consolidação e limpeza).")
