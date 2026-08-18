# Acidentes por animais peçonhentos no Brasil, 2007–2023

Material de apoio à avaliação do manuscrito:

> **Tendência temporal e perfil epidemiológico dos acidentes por animais peçonhentos no Brasil, 2007 a 2023: estudo ecológico de série temporal com 3,3 milhões de notificações do Sinan**

Submetido à **Revista Epidemiologia e Serviços de Saúde (RESS)**.

Este repositório reúne exclusivamente os arquivos necessários à avaliação do artigo
pelos revisores: manuscrito, tabelas, figuras, documentos de submissão e o código
utilizado na análise. A base de dados bruta **não** está incluída — ver
[dados/LEIAME.md](dados/LEIAME.md) para o registro de sua existência e instruções de
download reproduzível.

## Conteúdo

| Pasta | Arquivos |
|---|---|
| `manuscrito/` | Artigo completo (`.docx`), tabelas editáveis, carta de apresentação, declaração de responsabilidade, formulário de conformidade com a ciência aberta |
| `figuras/` | Figuras 1–7 e suplementar S1 (PNG, 300 dpi) |
| `codigo/` | `download_sinan.py` (obtenção da base via PySUS), `LimpezaDados.ipynb` (limpeza e análise), `gerar_figuras.py` (reprodução das figuras), `references.bib` |
| `dados/` | Registro da base de dados (fonte, método de download, tamanho, variáveis) |

## Dados

- **Fonte:** Sistema de Informação de Agravos de Notificação (Sinan), agravo
  "Acidente por animais peçonhentos" (ANIMALS), disponibilizado publicamente pelo
  DATASUS.
- **Período:** 2007–2023 (download original 2000–2023).
- **Registros:** 3.354.030 notificações.
- **Disponibilidade:** a base bruta (~1,7 GB em CSV) não foi incluída neste
  repositório por limitação de tamanho. O procedimento completo de obtenção está
  documentado em [dados/LEIAME.md](dados/LEIAME.md), com script reproduzível em
  `codigo/download_sinan.py`.

## Reprodução

```bash
# 1. Baixar a base (gera sinan_animais/*.parquet por ano)
pip install pysus pandas pyarrow fastparquet
python codigo/download_sinan.py

# 2. Limpeza e análise (gera a base consolidada utilizada no artigo)
#    Abrir e executar codigo/LimpezaDados.ipynb

# 3. Reproduzir as figuras
python codigo/gerar_figuras.py
```

## Licença

Os dados são de domínio público (Sinan/DATASUS). O conteúdo produzido pelos
autores (manuscrito, figuras e código) é disponibilizado para fins de avaliação
do manuscrito.
