import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title("📊 Dashboard Carteira de Fundos")

file = st.file_uploader("Upload da base", type=["xlsx"])

if file:
    # 🔥 Lê pulando a primeira linha errada
    df = pd.read_excel(file, header=1)

    # 🔥 Limpa nomes das colunas
    df.columns = df.columns.str.strip().str.upper()
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df["NET"] = pd.to_numeric(df["NET"], errors="coerce")

    # 🔥 Garante que NET é número
    df["NET"] = pd.to_numeric(df["NET"], errors="coerce")

    # 🔥 Remove linhas vazias
    df = df.dropna(subset=["ATIVO", "NET"])

    # 🔥 Consolidação por fundo
    fundos = df.groupby("ATIVO").agg(
        NET_TOTAL=("NET", "sum"),
        CLIENTES=("CLIENTE", "nunique")
    ).reset_index()

    # 🔥 Ticket médio
    fundos["TICKET_MEDIO"] = fundos["NET_TOTAL"] / fundos["CLIENTES"]
    fundos["NET_MEDIO"] = fundos["NET_TOTAL"] / fundos["CLIENTES"]
    fundos["NET_TOTAL"] = fundos["NET_TOTAL"].map("R$ {:,.2f}".format)
    fundos["TICKET_MEDIO"] = fundos["TICKET_MEDIO"].map("R$ {:,.2f}".format)
    fundos["NET_MEDIO"] = fundos["NET_MEDIO"].map("R$ {:,.2f}".format)

    # 🔥 Ordena
    fundos = fundos.sort_values(by="NET_TOTAL", ascending=False)

    # 🔥 TOTAL GERAL
    total = fundos["NET_TOTAL"].sum()
    total_clientes = df["CLIENTE"].nunique()

    # =========================
    # 📊 DASHBOARD
    # =========================

    col1, col2 = st.columns(2)

    col1.metric("💰 Patrimônio Total", f"R$ {total:,.0f}")
    col2.metric("👥 Total de Clientes", total_clientes)

    st.subheader("🏆 Ranking por Fundo")
    st.dataframe(fundos, use_container_width=True)

    # 🔥 Top 10 fundos
    st.subheader("📈 Top 10 Fundos")
    st.bar_chart(fundos.set_index("ATIVO")["NET_TOTAL"].head(10))
    st.subheader("📈 Evolução do Patrimônio")

    mensal = df.groupby(pd.Grouper(key="DATA", freq="M"))["NET"].sum()

    st.line_chart(mensal)
    import datetime

    hoje = datetime.datetime.today()
    
    # 🔹 12 meses
    df_12m = df[df["DATA"] >= hoje - pd.DateOffset(months=12)]
    mensal_12 = df_12m.groupby(pd.Grouper(key="DATA", freq="M"))["NET"].sum()
    
    st.subheader("📈 Últimos 12 meses")
    st.line_chart(mensal_12)
    
    # 🔹 24 meses
    df_24m = df[df["DATA"] >= hoje - pd.DateOffset(months=24)]
    mensal_24 = df_24m.groupby(pd.Grouper(key="DATA", freq="M"))["NET"].sum()
    
    st.subheader("📈 Últimos 24 meses")
    st.line_chart(mensal_24)
