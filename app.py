import streamlit as st
import pandas as pd

# -------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------
st.set_page_config(layout="wide")
st.title("📊 Dashboard de Fundos")

# -------------------------------
# UPLOAD DO ARQUIVO
# -------------------------------
file = st.file_uploader("📂 Envie sua base de dados (.xlsx)")

if file:

    # -------------------------------
    # LEITURA DO EXCEL
    # -------------------------------
    df = pd.read_excel(file)

    # Padroniza nomes das colunas
    df.columns = df.columns.str.strip().str.upper()

    st.write("🔍 Colunas encontradas:")
    st.write(df.columns)

    # -------------------------------
    # TRATAMENTO DE DADOS
    # -------------------------------

    # DATA
    if "DATA" in df.columns:
        df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")

    # NET (corrige formato brasileiro)
    if "NET" in df.columns:
        df["NET"] = (
            df["NET"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df["NET"] = pd.to_numeric(df["NET"], errors="coerce")

    # CLIENTE
    if "CLIENTE" in df.columns:
        df["CLIENTE"] = df["CLIENTE"].astype(str)

    # ATIVO
    if "ATIVO" in df.columns:
        df["ATIVO"] = df["ATIVO"].astype(str)

    # -------------------------------
    # AGRUPAMENTO PRINCIPAL
    # -------------------------------
    fundos = df.groupby("ATIVO").agg(
        NET_TOTAL=("NET", "sum"),
        CLIENTES=("CLIENTE", "nunique"),
        POSICOES=("CLIENTE", "count")
    ).reset_index()

    # Métricas adicionais
    fundos["TICKET_MEDIO"] = fundos["NET_TOTAL"] / fundos["CLIENTES"]
    fundos["NET_MEDIO"] = fundos["NET_TOTAL"] / fundos["POSICOES"]

    # -------------------------------
    # KPIs GERAIS
    # -------------------------------
    total = df["NET"].sum()
    clientes_total = df["CLIENTE"].nunique()
    fundos_total = df["ATIVO"].nunique()

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Patrimônio Total", f"R$ {total:,.0f}")
    col2.metric("👥 Clientes", clientes_total)
    col3.metric("📦 Fundos", fundos_total)

    # -------------------------------
    # FORMATAÇÃO SEGURA
    # -------------------------------
    def formatar_moeda(x):
        try:
            return f"R$ {float(x):,.2f}"
        except:
            return "-"

    fundos_view = fundos.copy()

    fundos_view["NET_TOTAL"] = fundos_view["NET_TOTAL"].apply(formatar_moeda)
    fundos_view["TICKET_MEDIO"] = fundos_view["TICKET_MEDIO"].apply(formatar_moeda)
    fundos_view["NET_MEDIO"] = fundos_view["NET_MEDIO"].apply(formatar_moeda)

    # -------------------------------
    # TABELA FINAL
    # -------------------------------
    st.subheader("📊 Consolidação por Fundo")
    st.dataframe(fundos_view.sort_values(by="CLIENTES", ascending=False), use_container_width=True)

    # -------------------------------
    # TOP 10 FUNDOS
    # -------------------------------
    st.subheader("🏆 Top 10 Fundos por Patrimônio")

    top10 = fundos.sort_values(by="NET_TOTAL", ascending=False).head(10)

    st.bar_chart(top10.set_index("ATIVO")["NET_TOTAL"])

else:
    st.warning("⚠️ Envie um arquivo para começar")
