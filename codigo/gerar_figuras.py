"""
Geração de figuras publication-grade para o artigo:
"Tendência temporal e perfil epidemiológico dos acidentes por animais
peçonhentos no Brasil, 2007-2023"

Figuras produzidas:
  fig1_serie_temporal.png        — Série temporal total + regressão
  fig2_serie_por_animal.png      — Casos por tipo de animal (2007-2023)
  fig3_letalidade_animal.png     — Letalidade e proporção de casos graves por animal
  fig4_distribuicao_regional.png — Casos e letalidade por macrorregião
  fig5_sazonalidade.png          — Distribuição mensal por tipo de animal
  fig6_perfil_demografico.png    — Perfil de faixa etária e sexo
  fig7_covid_impacto.png         — Impacto da pandemia COVID-19 por região
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
from pathlib import Path

# ──────────────────────────────────────────────
# 0. Estilo global publication-grade
# ──────────────────────────────────────────────
mpl.rcParams.update({
    "font.family":       "DejaVu Sans",
    "font.size":         10,
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "legend.fontsize":   9,
    "legend.frameon":    False,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.linewidth":    0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "grid.linewidth":    0.5,
    "grid.alpha":        0.4,
    "figure.dpi":        150,
    "savefig.dpi":       300,
    "savefig.bbox":      "tight",
    "savefig.facecolor": "white",
})

# Paleta acessível (Color Universal Design)
CUD = {
    "Escorpião": "#E69F00",
    "Serpente":  "#56B4E9",
    "Aranha":    "#009E73",
    "Abelha":    "#F0E442",
    "Lagarta":   "#0072B2",
    "Outros":    "#D55E00",
    "Ignorado":  "#CC79A7",
    "total":     "#333333",
    "regress":   "#CC3311",
}
REGIAO_COLORS = {
    "Sudeste":      "#1B7837",
    "Nordeste":     "#E08214",
    "Sul":          "#4575B4",
    "Norte":        "#D73027",
    "Centro-Oeste": "#762A83",
}

OUT = Path("/home/marc/Documentos/ANIM_PEC/figuras")
OUT.mkdir(exist_ok=True)

# ──────────────────────────────────────────────
# 1. Carregar e preparar dados
# ──────────────────────────────────────────────
print("Carregando dados …")
df = pd.read_csv(
    "/home/marc/Documentos/ANIM_PEC/animais_peconhentos_2000_2023.csv",
    low_memory=False, encoding="latin-1",
)

M_ANIMAL  = {1:"Serpente",2:"Aranha",3:"Escorpião",4:"Lagarta",5:"Abelha",6:"Outros",9:"Ignorado"}
M_CLASSI  = {1:"Leve",2:"Moderado",3:"Grave",9:"Ignorado"}
M_EVOLUCAO= {1:"Cura",2:"Obito_Peconhento",3:"Obito_Outras",9:"Ignorado"}
M_UF      = {12:"AC",27:"AL",16:"AP",13:"AM",29:"BA",23:"CE",53:"DF",32:"ES",52:"GO",
             21:"MA",51:"MT",50:"MS",31:"MG",15:"PA",25:"PB",41:"PR",26:"PE",22:"PI",
             33:"RJ",24:"RN",43:"RS",11:"RO",14:"RR",42:"SC",35:"SP",28:"SE",17:"TO"}
M_REGIAO  = {"AC":"Norte","AM":"Norte","AP":"Norte","PA":"Norte","RO":"Norte",
             "RR":"Norte","TO":"Norte","AL":"Nordeste","BA":"Nordeste","CE":"Nordeste",
             "MA":"Nordeste","PB":"Nordeste","PE":"Nordeste","PI":"Nordeste",
             "RN":"Nordeste","SE":"Nordeste","DF":"Centro-Oeste","GO":"Centro-Oeste",
             "MS":"Centro-Oeste","MT":"Centro-Oeste","ES":"Sudeste","MG":"Sudeste",
             "RJ":"Sudeste","SP":"Sudeste","PR":"Sul","RS":"Sul","SC":"Sul"}

df["TP_ACIDENT"] = pd.to_numeric(df["TP_ACIDENT"], errors="coerce").astype("Int64").map(M_ANIMAL)
df["TRA_CLASSI"] = pd.to_numeric(df["TRA_CLASSI"], errors="coerce").astype("Int64").map(M_CLASSI)
df["EVOLUCAO"]   = pd.to_numeric(df["EVOLUCAO"],   errors="coerce").astype("Int64").map(M_EVOLUCAO)
df["SG_UF_NOT"]  = pd.to_numeric(df["SG_UF_NOT"],  errors="coerce").astype("Int64").map(M_UF)
df["REGIAO"]     = df["SG_UF_NOT"].map(M_REGIAO)
df["CS_SEXO"]    = df["CS_SEXO"].str.strip().str.upper()
df["DT_NOTIFIC"] = pd.to_datetime(df["DT_NOTIFIC"], errors="coerce")
df["MES"]        = df["DT_NOTIFIC"].dt.month

# Idade
df["IDADE_ANOS"] = pd.to_numeric(df["NU_IDADE_N"], errors="coerce").astype("float64")
m_anos  = df["IDADE_ANOS"] >= 4000
m_meses = (df["IDADE_ANOS"] >= 3000) & (df["IDADE_ANOS"] < 4000)
m_dias  = (df["IDADE_ANOS"] >= 2000) & (df["IDADE_ANOS"] < 3000)
df.loc[m_anos,  "IDADE_ANOS"] = df.loc[m_anos,  "IDADE_ANOS"] - 4000
df.loc[m_meses, "IDADE_ANOS"] = (df.loc[m_meses, "IDADE_ANOS"] - 3000) / 12
df.loc[m_dias,  "IDADE_ANOS"] = (df.loc[m_dias,  "IDADE_ANOS"] - 2000) / 365
df.loc[df["IDADE_ANOS"] > 120, "IDADE_ANOS"] = np.nan

bins   = [0,4,9,14,19,29,39,49,59,69,79,200]
labels = ["0–4","5–9","10–14","15–19","20–29","30–39","40–49","50–59","60–69","70–79","80+"]
df["FAIXA_ETARIA"] = pd.cut(df["IDADE_ANOS"], bins=bins, labels=labels, right=True)

print("Dados carregados:", df.shape)

# ══════════════════════════════════════════════
# FIG 1 — Série temporal total + regressão
# ══════════════════════════════════════════════
print("Gerando Fig 1 …")
serie = df.groupby("NU_ANO").agg(
    n_casos    = ("NU_ANO", "count"),
    n_obitos   = ("EVOLUCAO", lambda x: (x == "Obito_Peconhento").sum()),
).reset_index()
serie["letalidade"] = serie["n_obitos"] / serie["n_casos"] * 100

x = serie["NU_ANO"].values
y = serie["n_casos"].values
sl, ic, r, pv, _ = stats.linregress(x, y)
y_hat = sl * x + ic

fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True,
                         gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08})

ax = axes[0]
ax.plot(x, y / 1000, "o-", color=CUD["total"], lw=1.8, ms=5, zorder=3, label="Casos notificados")
ax.plot(x, y_hat / 1000, "--", color=CUD["regress"], lw=1.5,
        label=f"Tendência linear (slope = +{sl/1000:.1f}k/ano; R² = {r**2:.2f}; p < 0,001)")
ax.fill_between(x, y / 1000, y_hat / 1000, alpha=0.07, color=CUD["regress"])
ax.axvspan(2020, 2021.5, color="steelblue", alpha=0.12, label="Pandemia COVID-19")
ax.set_ylabel("Notificações (× 1.000)", labelpad=6)
ax.set_ylim(0, 400)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}"))
ax.legend(loc="upper left", fontsize=8.5)
ax.set_title("A   Tendência temporal das notificações de acidentes por animais peçonhentos,\n"
             "Brasil, 2007–2023 (N = 3.354.030)", loc="left", fontsize=10, fontweight="bold")
ax.grid(axis="y", ls="--")

ax2 = axes[1]
ax2.bar(x, serie["n_obitos"], color=CUD["regress"], alpha=0.75, width=0.7, label="Óbitos anuais")
ax2_r = ax2.twinx()
ax2_r.plot(x, serie["letalidade"], "D--", color="#444", ms=4, lw=1.2, label="Letalidade (%)")
ax2_r.set_ylabel("Letalidade (%)", fontsize=8)
ax2_r.set_ylim(0, 0.35)
ax2_r.spines["top"].set_visible(False)
ax2.set_ylabel("Óbitos", labelpad=6)
ax2.set_ylim(0, 600)
ax2.set_xlabel("Ano")
ax2.set_xticks(x)
ax2.set_xticklabels([str(int(v)) for v in x], rotation=45, ha="right", fontsize=8)

lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_r.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)
ax2.set_title("B   Óbitos anuais e taxa de letalidade", loc="left", fontsize=9, fontweight="bold")
ax2.grid(axis="y", ls="--")

plt.savefig(OUT / "fig1_serie_temporal.png")
plt.close()
print("  → fig1_serie_temporal.png")

# ══════════════════════════════════════════════
# FIG 2 — Casos por tipo de animal (linha)
# ══════════════════════════════════════════════
print("Gerando Fig 2 …")
tipo_ano = df.groupby(["NU_ANO", "TP_ACIDENT"]).size().unstack(fill_value=0)
order_animals = ["Escorpião", "Serpente", "Aranha", "Abelha", "Lagarta", "Outros"]
tipo_ano = tipo_ano[[c for c in order_animals if c in tipo_ano.columns]]

fig, ax = plt.subplots(figsize=(9, 5))
for animal in order_animals:
    if animal in tipo_ano.columns:
        ax.plot(tipo_ano.index, tipo_ano[animal] / 1000,
                "o-", lw=1.8, ms=5, color=CUD[animal], label=animal)

ax.axvspan(2020, 2021.5, color="steelblue", alpha=0.1, label="Pandemia COVID-19")
ax.set_xlabel("Ano")
ax.set_ylabel("Notificações (× 1.000)")
ax.set_title("Evolução anual de acidentes por tipo de animal peçonhento,\n"
             "Brasil, 2007–2023", fontweight="bold")
ax.legend(loc="upper left", ncol=2, fontsize=9)
ax.set_xticks(tipo_ano.index)
ax.set_xticklabels([str(int(v)) for v in tipo_ano.index], rotation=45, ha="right", fontsize=8)
ax.grid(axis="y", ls="--")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}"))

plt.savefig(OUT / "fig2_serie_por_animal.png")
plt.close()
print("  → fig2_serie_por_animal.png")

# ══════════════════════════════════════════════
# FIG 3 — Letalidade e casos graves por animal
# ══════════════════════════════════════════════
print("Gerando Fig 3 …")
let_animal = df.groupby("TP_ACIDENT").agg(
    n_casos   = ("EVOLUCAO", "count"),
    n_obitos  = ("EVOLUCAO", lambda x: (x == "Obito_Peconhento").sum()),
    n_graves  = ("TRA_CLASSI", lambda x: (x == "Grave").sum()),
).reset_index()
let_animal["letalidade"]  = let_animal["n_obitos"] / let_animal["n_casos"] * 100
let_animal["pct_graves"]  = let_animal["n_graves"]  / let_animal["n_casos"] * 100
let_animal = let_animal[let_animal["TP_ACIDENT"] != "Ignorado"].copy()
let_animal = let_animal.sort_values("letalidade", ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

# Painel A — letalidade
ax = axes[0]
colors = [CUD.get(a, "#888") for a in let_animal["TP_ACIDENT"]]
bars = ax.barh(let_animal["TP_ACIDENT"], let_animal["letalidade"],
               color=colors, edgecolor="white", height=0.65)
for bar, val, n_ob in zip(bars, let_animal["letalidade"], let_animal["n_obitos"]):
    ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
            f"{val:.3f}%\n(n={n_ob:,})", va="center", fontsize=8)
ax.set_xlabel("Taxa de letalidade (%)")
ax.set_title("A   Taxa de letalidade por tipo de acidente", loc="left",
             fontweight="bold", fontsize=10)
ax.set_xlim(0, 0.65)
ax.grid(axis="x", ls="--")

# Painel B — % casos graves
ax2 = axes[1]
let_animal2 = let_animal.sort_values("pct_graves", ascending=True)
colors2 = [CUD.get(a, "#888") for a in let_animal2["TP_ACIDENT"]]
bars2 = ax2.barh(let_animal2["TP_ACIDENT"], let_animal2["pct_graves"],
                 color=colors2, edgecolor="white", height=0.65)
for bar, val in zip(bars2, let_animal2["pct_graves"]):
    ax2.text(val + 0.03, bar.get_y() + bar.get_height()/2,
             f"{val:.2f}%", va="center", fontsize=8)
ax2.set_xlabel("Proporção de casos graves (%)")
ax2.set_title("B   Proporção de casos graves por tipo de acidente", loc="left",
              fontweight="bold", fontsize=10)
ax2.set_xlim(0, 12)
ax2.grid(axis="x", ls="--")

plt.tight_layout()
plt.savefig(OUT / "fig3_letalidade_animal.png")
plt.close()
print("  → fig3_letalidade_animal.png")

# ══════════════════════════════════════════════
# FIG 4 — Distribuição regional
# ══════════════════════════════════════════════
print("Gerando Fig 4 …")
reg_data = df.groupby("REGIAO").agg(
    n_casos  = ("EVOLUCAO", "count"),
    n_obitos = ("EVOLUCAO", lambda x: (x == "Obito_Peconhento").sum()),
).reset_index().dropna(subset=["REGIAO"])
reg_data["letalidade"] = reg_data["n_obitos"] / reg_data["n_casos"] * 100
reg_data["pct_casos"]  = reg_data["n_casos"] / reg_data["n_casos"].sum() * 100
reg_data = reg_data.sort_values("n_casos", ascending=False)

# Série temporal por região
reg_ano = df.groupby(["NU_ANO", "REGIAO"]).size().unstack(fill_value=0)
reg_ano = reg_ano[[c for c in ["Sudeste","Nordeste","Sul","Norte","Centro-Oeste"] if c in reg_ano.columns]]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Painel A — barras casos e letalidade
ax = axes[0]
x_pos = np.arange(len(reg_data))
colors_r = [REGIAO_COLORS.get(r, "#888") for r in reg_data["REGIAO"]]
bars = ax.bar(x_pos, reg_data["n_casos"] / 1000, color=colors_r,
              edgecolor="white", width=0.6, label="Casos (× 1.000)")
ax.set_xticks(x_pos)
ax.set_xticklabels(reg_data["REGIAO"], rotation=20, ha="right")
ax.set_ylabel("Notificações (× 1.000)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}"))

ax_r = ax.twinx()
ax_r.plot(x_pos, reg_data["letalidade"], "D--", color="#333", ms=7, lw=1.5,
          label="Letalidade (%)")
ax_r.set_ylabel("Taxa de letalidade (%)", fontsize=9)
ax_r.set_ylim(0, 0.5)
ax_r.spines["top"].set_visible(False)

for i, (row) in enumerate(reg_data.itertuples()):
    ax.text(i, row.n_casos / 1000 + 5, f"{row.pct_casos:.1f}%",
            ha="center", fontsize=8, color="#333")

lines1, labs1 = ax.get_legend_handles_labels()
lines2, labs2 = ax_r.get_legend_handles_labels()
ax.legend(lines1 + lines2, labs1 + labs2, fontsize=8, loc="upper right")
ax.set_title("A   Distribuição de casos e letalidade por macrorregião", loc="left",
             fontweight="bold", fontsize=10)
ax.grid(axis="y", ls="--")

# Painel B — série temporal por região
ax2 = axes[1]
for reg in reg_ano.columns:
    ax2.plot(reg_ano.index, reg_ano[reg] / 1000,
             "o-", lw=1.8, ms=4, color=REGIAO_COLORS.get(reg, "#888"), label=reg)
ax2.axvspan(2020, 2021.5, color="steelblue", alpha=0.1)
ax2.set_xlabel("Ano")
ax2.set_ylabel("Notificações (× 1.000)")
ax2.set_title("B   Evolução temporal por macrorregião", loc="left",
              fontweight="bold", fontsize=10)
ax2.legend(fontsize=8, loc="upper left")
ax2.set_xticks(reg_ano.index[::2])
ax2.set_xticklabels([str(int(v)) for v in reg_ano.index[::2]], rotation=45, ha="right", fontsize=8)
ax2.grid(axis="y", ls="--")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}"))

plt.tight_layout()
plt.savefig(OUT / "fig4_distribuicao_regional.png")
plt.close()
print("  → fig4_distribuicao_regional.png")

# ══════════════════════════════════════════════
# FIG 5 — Sazonalidade por tipo de animal
# ══════════════════════════════════════════════
print("Gerando Fig 5 …")
meses_label = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

# Sazonalidade geral
sazo_total = df.groupby("MES").size().reset_index(name="n")
sazo_total["pct"] = sazo_total["n"] / sazo_total["n"].sum() * 100

# Por animal
sazo_animal = df.groupby(["MES", "TP_ACIDENT"]).size().unstack(fill_value=0)
sazo_animal = sazo_animal[[c for c in ["Escorpião","Serpente","Aranha","Abelha"] if c in sazo_animal.columns]]
# Normalizar por % dentro de cada animal
sazo_pct = sazo_animal.div(sazo_animal.sum(axis=0), axis=1) * 100

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# Painel A — sazonalidade total
ax = axes[0]
idx = np.arange(1, 13)
ax.bar(idx, sazo_total["pct"], color=CUD["total"], alpha=0.7, width=0.7)
ax.plot(idx, sazo_total["pct"], "o-", color=CUD["regress"], lw=1.5, ms=5)
ax.set_xticks(idx)
ax.set_xticklabels(meses_label)
ax.set_xlabel("Mês")
ax.set_ylabel("Proporção do total anual (%)")
ax.axhline(100/12, color="#888", ls="--", lw=1, label=f"Distribuição uniforme ({100/12:.1f}%)")
ax.legend(fontsize=8)
ax.set_title("A   Distribuição mensal — todos os acidentes peçonhentos", loc="left",
             fontweight="bold", fontsize=10)
ax.grid(axis="y", ls="--")
ax.set_ylim(0, 13)

# Painel B — sazonalidade por tipo
ax2 = axes[1]
for animal in sazo_pct.columns:
    ax2.plot(idx, sazo_pct[animal], "o-", lw=1.8, ms=5,
             color=CUD[animal], label=animal)
ax2.set_xticks(idx)
ax2.set_xticklabels(meses_label)
ax2.set_xlabel("Mês")
ax2.set_ylabel("Proporção dentro do tipo (%)")
ax2.axhline(100/12, color="#888", ls="--", lw=1)
ax2.legend(fontsize=8.5, ncol=2)
ax2.set_title("B   Sazonalidade por tipo de animal", loc="left",
              fontweight="bold", fontsize=10)
ax2.grid(axis="y", ls="--")

plt.tight_layout()
plt.savefig(OUT / "fig5_sazonalidade.png")
plt.close()
print("  → fig5_sazonalidade.png")

# ══════════════════════════════════════════════
# FIG 6 — Perfil sociodemográfico
# ══════════════════════════════════════════════
print("Gerando Fig 6 …")
fig, axes = plt.subplots(1, 3, figsize=(13, 5))

# Painel A — Faixa etária geral (horizontal bar)
ax = axes[0]
fe = df["FAIXA_ETARIA"].value_counts(dropna=True).sort_index()
fe_pct = fe / fe.sum() * 100
ax.barh(range(len(fe_pct)), fe_pct.values, color="#2166AC", edgecolor="white", height=0.7)
ax.set_yticks(range(len(fe_pct)))
ax.set_yticklabels(fe_pct.index)
for i, val in enumerate(fe_pct.values):
    ax.text(val + 0.2, i, f"{val:.1f}%", va="center", fontsize=8)
ax.set_xlabel("Proporção (%)")
ax.set_title("A   Distribuição etária", loc="left", fontweight="bold", fontsize=10)
ax.grid(axis="x", ls="--")
ax.set_xlim(0, 23)

# Painel B — Faixa etária por sexo (M vs F)
ax2 = axes[1]
fe_sexo = df[df["CS_SEXO"].isin(["M", "F"])].groupby(["FAIXA_ETARIA", "CS_SEXO"]).size().unstack(fill_value=0)
fe_sexo_pct = fe_sexo.div(fe_sexo.sum(), axis=1) * 100

x_fe = np.arange(len(fe_sexo_pct))
w = 0.35
ax2.barh(x_fe + w/2, fe_sexo_pct["M"], height=w, color="#2166AC", label="Masculino", alpha=0.85)
ax2.barh(x_fe - w/2, fe_sexo_pct["F"], height=w, color="#D6604D", label="Feminino", alpha=0.85)
ax2.set_yticks(x_fe)
ax2.set_yticklabels(fe_sexo_pct.index)
ax2.set_xlabel("Proporção dentro do sexo (%)")
ax2.legend(fontsize=8.5)
ax2.set_title("B   Distribuição etária por sexo", loc="left", fontweight="bold", fontsize=10)
ax2.grid(axis="x", ls="--")

# Painel C — Raça/Cor
ax3 = axes[2]
M_RACA_L = {1:"Branca", 2:"Preta", 3:"Amarela", 4:"Parda", 5:"Indígena", 9:"Ignorado"}
raca_series = pd.to_numeric(df["CS_RACA"], errors="coerce").astype("Int64").map(M_RACA_L)
raca_cnt = raca_series.value_counts().drop("Ignorado", errors="ignore").dropna()
raca_pct = raca_cnt / raca_cnt.sum() * 100
raca_colors = {"Parda":"#E08214", "Branca":"#92C5DE", "Preta":"#4D4D4D",
               "Indígena":"#A6D96A", "Amarela":"#F4E642"}
raca_pct_s = raca_pct.sort_values(ascending=True)
c_list = [raca_colors.get(r, "#888") for r in raca_pct_s.index]
ax3.barh(range(len(raca_pct_s)), raca_pct_s.values, color=c_list, edgecolor="white", height=0.65)
ax3.set_yticks(range(len(raca_pct_s)))
ax3.set_yticklabels(raca_pct_s.index)
for i, val in enumerate(raca_pct_s.values):
    ax3.text(val + 0.3, i, f"{val:.1f}%", va="center", fontsize=8.5)
ax3.set_xlabel("Proporção (%) — excluído 'Ignorado'")
ax3.set_title("C   Distribuição por raça/cor autodeclarada", loc="left",
              fontweight="bold", fontsize=10)
ax3.grid(axis="x", ls="--")
ax3.set_xlim(0, 60)

plt.tight_layout()
plt.savefig(OUT / "fig6_perfil_demografico.png")
plt.close()
print("  → fig6_perfil_demografico.png")

# ══════════════════════════════════════════════
# FIG 7 — Impacto COVID-19
# ══════════════════════════════════════════════
print("Gerando Fig 7 …")
anos_covid = [2017, 2018, 2019, 2020, 2021, 2022, 2023]
total_covid = serie[serie["NU_ANO"].isin(anos_covid)].set_index("NU_ANO")["n_casos"]

reg_covid = df[df["NU_ANO"].isin(anos_covid)].groupby(["NU_ANO","REGIAO"]).size().unstack(fill_value=0)
reg_covid = reg_covid[[c for c in ["Sudeste","Nordeste","Sul","Norte","Centro-Oeste"] if c in reg_covid.columns]]

# Variação pct 2019→2020 por região
delta_pct = {}
for reg in reg_covid.columns:
    n19 = reg_covid.loc[2019, reg] if 2019 in reg_covid.index else 0
    n20 = reg_covid.loc[2020, reg] if 2020 in reg_covid.index else 0
    delta_pct[reg] = (n20 - n19) / n19 * 100 if n19 > 0 else 0

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Painel A — série pré/durante/pós com anotações
ax = axes[0]
ax.plot(total_covid.index, total_covid.values / 1000, "o-",
        color=CUD["total"], lw=2, ms=7, zorder=3)
ax.axvspan(2020, 2021.5, color="steelblue", alpha=0.15, label="Pandemia COVID-19")
ax.axhline(total_covid[2019] / 1000, color="#888", ls=":", lw=1.2, label="Nível pré-pandemia (2019)")
for ano in [2020, 2021, 2022, 2023]:
    if ano in total_covid.index:
        base = total_covid[2019]
        delta = (total_covid[ano] - base) / base * 100
        color = "#D73027" if delta < 0 else "#1A9850"
        ax.annotate(f"{delta:+.1f}%", xy=(ano, total_covid[ano] / 1000),
                    xytext=(ano + 0.1, total_covid[ano] / 1000 + 8),
                    fontsize=8.5, color=color, fontweight="bold")
ax.set_xlabel("Ano")
ax.set_ylabel("Notificações (× 1.000)")
ax.set_xticks(anos_covid)
ax.set_xticklabels([str(v) for v in anos_covid], rotation=45, ha="right")
ax.legend(fontsize=8.5)
ax.set_title("A   Notificações totais — contexto pré e pós-pandemia\n(variação em relação a 2019)", loc="left",
             fontweight="bold", fontsize=10)
ax.grid(axis="y", ls="--")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}"))

# Painel B — variação percentual 2019→2020 por região
ax2 = axes[1]
regioes = list(delta_pct.keys())
deltas  = [delta_pct[r] for r in regioes]
order_idx = np.argsort(deltas)
regioes_ord = [regioes[i] for i in order_idx]
deltas_ord  = [deltas[i] for i in order_idx]
bar_colors  = ["#D73027" if d < 0 else "#1A9850" for d in deltas_ord]

bars = ax2.barh(regioes_ord, deltas_ord, color=bar_colors, edgecolor="white", height=0.6)
ax2.axvline(0, color="#333", lw=1)
for bar, val in zip(bars, deltas_ord):
    xpos = val - 0.5 if val < 0 else val + 0.2
    ha   = "right" if val < 0 else "left"
    ax2.text(xpos, bar.get_y() + bar.get_height()/2,
             f"{val:.1f}%", va="center", ha=ha, fontsize=9, fontweight="bold")
ax2.set_xlabel("Variação percentual (%) em relação a 2019")
ax2.set_title("B   Impacto regional da pandemia COVID-19\n(variação 2019 → 2020)", loc="left",
              fontweight="bold", fontsize=10)
ax2.set_xlim(-30, 5)
ax2.grid(axis="x", ls="--")

plt.tight_layout()
plt.savefig(OUT / "fig7_covid_impacto.png")
plt.close()
print("  → fig7_covid_impacto.png")

# ══════════════════════════════════════════════
# FIG S1 (Supplementary) — Escorpionismo detalhe
# ══════════════════════════════════════════════
print("Gerando Fig S1 …")
esc = df[df["TP_ACIDENT"] == "Escorpião"].groupby("NU_ANO").agg(
    n       = ("EVOLUCAO", "count"),
    obitos  = ("EVOLUCAO", lambda x: (x == "Obito_Peconhento").sum()),
    graves  = ("TRA_CLASSI", lambda x: (x == "Grave").sum()),
).reset_index()
esc["let_pct"]   = esc["obitos"] / esc["n"] * 100
esc["grave_pct"] = esc["graves"] / esc["n"] * 100

x_esc = esc["NU_ANO"].values
sl_e, ic_e, r_e, pv_e, _ = stats.linregress(x_esc, esc["n"].values)
y_hat_e = sl_e * x_esc + ic_e

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(x_esc, esc["n"] / 1000, color=CUD["Escorpião"], alpha=0.85, width=0.7, label="Casos (× 1.000)")
ax.plot(x_esc, y_hat_e / 1000, "--", color="#333", lw=1.5,
        label=f"Tendência (slope = +{sl_e/1000:.1f}k/ano; R² = {r_e**2:.2f})")
ax.axvspan(2020, 2021.5, color="steelblue", alpha=0.12)
ax.set_xlabel("Ano")
ax.set_ylabel("Notificações de escorpionismo (× 1.000)")
ax.set_xticks(x_esc)
ax.set_xticklabels([str(int(v)) for v in x_esc], rotation=45, ha="right", fontsize=8)

ax_r = ax.twinx()
ax_r.plot(x_esc, esc["let_pct"], "D-.", color=CUD["regress"], ms=5, lw=1.3, label="Letalidade (%)")
ax_r.set_ylabel("Taxa de letalidade (%)", fontsize=9)
ax_r.set_ylim(0, 0.3)
ax_r.spines["top"].set_visible(False)

lines1, labs1 = ax.get_legend_handles_labels()
lines2, labs2 = ax_r.get_legend_handles_labels()
ax.legend(lines1 + lines2, labs1 + labs2, fontsize=8.5, loc="upper left")
ax.set_title("Escorpionismo no Brasil, 2007–2023: casos notificados e taxa de letalidade",
             fontweight="bold", fontsize=10)
ax.grid(axis="y", ls="--")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}"))

plt.tight_layout()
plt.savefig(OUT / "figS1_escorpionismo.png")
plt.close()
print("  → figS1_escorpionismo.png")

# ──────────────────────────────────────────────
# Resumo final
# ──────────────────────────────────────────────
pngs = sorted(OUT.glob("*.png"))
print(f"\n✓ {len(pngs)} figuras geradas em {OUT}/")
for p in pngs:
    size_kb = p.stat().st_size / 1024
    print(f"  {p.name:<45} {size_kb:>7.1f} KB")
