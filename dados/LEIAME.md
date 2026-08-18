# Registro da base de dados

## Identificação

| Campo | Valor |
|---|---|
| Sistema | Sistema de Informação de Agravos de Notificação (Sinan) |
| Agravo | Acidente por animais peçonhentos (código Sinan: ANIMALS) |
| Fonte pública | DATASUS (downloads do Sinan) |
| Período baixado | 2000–2023 (arquivos anuais) |
| Período analisado no artigo | 2007–2023 |
| Notificações incluídas | 3.354.030 (após filtro de notificação individual — `TP_NOT == 2`) |

## Como a base foi obtida (data: out/2025)

Os arquivos anuais do agravo ANIMALS foram baixados diretamente do DATASUS com a
biblioteca **PySUS** (interface Python para os dados públicos do SUS), em script
Jupyter/R com concorrência por ano de notificação, e salvos em formato Parquet
(`sinan_animais/anim_<ano>.parquet`). O script reproduzível está em
`../codigo/download_sinan.py`.

Em seguida, os arquivos anuais foram concatenados em um CSV consolidado
(`sinan_animais_2000_2023.csv`, ~430 MB) e a base analítica final
(`animais_peconhentos_2000_2023.csv`, ~1,7 GB) foi gerada pela rotina de limpeza
em `../codigo/LimpezaDados.ipynb` (seleção do agravo, filtro `TP_NOT == 2`,
variáveis de interesse, período de análise).

## Tamanho e formato

| Arquivo (local) | Tamanho | Formato |
|---|---|---|
| `sinan_animais/anim_<ano>.parquet` (2000–2023) | ~7–9 MB/ano | Parquet |
| `sinan_animais_2000_2023.csv` | ~430 MB | CSV |
| `animais_peconhentos_2000_2023.csv` | ~1,7 GB | CSV |

> A base final em CSV (~1,7 GB) excede o limite de tamanho para inclusão neste
> repositório; por isso fica apenas o presente registro e o procedimento de
> obtenção. A base pode ser reproduzida integralmente com `download_sinan.py` +
> `LimpezaDados.ipynb`.

## Variáveis principais

- **Notificação:** `TP_NOT`, `ID_AGRAVO`, `DT_NOTIFIC`, `SEM_NOT`, `NU_ANO`
- **Localização:** `SG_UF_NOT`, `ID_MUNICIP`, `SG_UF`, `ID_MN_RESI`, `ID_REGIONA`
- **Acidente:** `TP_ACIDENT` (serpente, aranha, escorpião, lagarta, abelha, outros),
  `ANT_TEMPO_`, `ANT_LOCA_1`
- **Clínica:** `TRA_CLASSI` (leve/moderado/grave), `CON_SOROTE`, `CLI_*`
- **Demográfico:** `NU_IDADE_N`, `CS_SEXO`, `CS_RACA`, `CS_ESCOL_N`
- **Evolução:** `EVOLUCAO` (inclui óbito)

## Nota ética

Dados secundários agregados, de domínio público, sem identificação dos indivíduos
(dispensa de apreciação por comitê de ética conforme Resolução CNS nº 510/2016 —
declaração também presente no manuscrito).

## Reprodução

```bash
pip install pysus pandas pyarrow fastparquet
python codigo/download_sinan.py   # baixa e gera sinan_animais/*.parquet
# depois: executar codigo/LimpezaDados.ipynb para consolidar a base analítica
```
