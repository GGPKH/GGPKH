import streamlit as st
import pandas as pd

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(layout="wide")
st.title("📊 Dashboard de Fundos")

# -------------------------------
# UPLOAD
# -------------------------------
file = st.file_uploader("📂 Envie sua base (.xlsx)")

if file:

    # -------------------------------
    # LEITURA (corrige cabeçalho)
    # -------------------------------
    df = pd.read_excel(file, header=1)

    # -------------------------------
    # LIMPEZA NOMES COLUNAS
    # -------------------------------
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
    )

    st.write("📌 Colunas detectadas:")
    st.write(df.columns)

    # -------------------------------
    # IDENTIFICA COLUNAS AUTOMÁTICO
    # -------------------------------
    col_cliente = [c for c in df.columns if "CLIENTE" in c][0]
    col_ativo = [c for c in df.columns if "ATIVO" in c][0]
    col_net = [c for c in df.columns if "NET" in c][0]

    # -------------------------------
    # TRATAMENTO DE DADOS
    # -------------------------------

    # Cliente
    df[col_cliente] = df[col_cliente].astype(str)

    # NET (corrige padrão brasileiro)
    df[col_net] = (
        df[col_net]
        .astype(str)
        .str.replace(r"\.", "", regex=True)   # remove milhar
        .str.replace(",", ".", regex=False)   # decimal
    )
    df[col_net] = pd.to_numeric(df[col_net], errors="coerce")

    # Remove linhas inválidas
    df = df.dropna(subset=[col_net])

    # DEBUG (pode apagar depois)
    st.write("🔍 NET corrigido (amostra):")
    st.write(df[col_net].head())

    # -------------------------------
    # AGRUPAMENTO
    # -------------------------------
    fundos = df.groupby(col_ativo).agg(
        NET_TOTAL=(col_net, "sum"),
        CLIENTES=(col_cliente, "nunique"),
        POSICOES=(col_cliente, "count")
    ).reset_index()

    # Métricas
    fundos["TICKET_MEDIO"] = fundos["NET_TOTAL"] / fundos["CLIENTES"]
    fundos["NET_MEDIO"] = fundos["NET_TOTAL"] / fundos["POSICOES"]

    # -------------------------------
    # KPIs GERAIS
    # -------------------------------
    total = df[col_net].sum()
    clientes_total = df[col_cliente].nunique()
    fundos_total = df[col_ativo].nunique()

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Patrimônio Total", f"R$ {total:,.0f}")
    col2.metric("👥 Clientes", clientes_total)
    col3.metric("📦 Fundos", fundos_total)

    # -------------------------------
    # FORMATADOR
    # -------------------------------
    def moeda(x):
        try:
            return f"R$ {float(x):,.2f}"
        except:
            return "-"

    view = fundos.copy()

    view["NET_TOTAL"] = view["NET_TOTAL"].apply(moeda)
    view["TICKET_MEDIO"] = view["TICKET_MEDIO"].apply(moeda)
    view["NET_MEDIO"] = view["NET_MEDIO"].apply(moeda)

    # -------------------------------
    # TABELA
    # -------------------------------
    st.subheader("📊 Consolidação por Fundo")
    st.dataframe(
        view.sort_values(by="CLIENTES", ascending=False),
        use_container_width=True
    )

    # -------------------------------
    # TOP 10
    # -------------------------------
    st.subheader("🏆 Top 10 Fundos por Patrimônio")

    top10 = fundos.sort_values(by="NET_TOTAL", ascending=False).head(10)

    st.bar_chart(top10.set_index(col_ativo)["NET_TOTAL"])

else:
    st.warning("⚠️ Envie um arquivo para começar")
