import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title("📊 Dashboard Carteira de Fundos")

file = st.file_uploader("Upload da base", type=["xlsx"])

if file:
    df = pd.read_excel(file)

st.write(df.columns)    

df.columns = df.columns.str.strip().str.upper()    

fundos = df.groupby("ATIVO").agg(
    NET_total=("NET", "sum"),
    Clientes=("CLIENTE", "nunique")
).reset_index()

fundos["Ticket Medio"] = fundos["NET_total"] / fundos["Clientes"]
fundos = fundos.sort_values(by="NET_total", ascending=False)

total = fundos["NET_total"].sum()
fundos["%"] = fundos["NET_total"] / total

clientes = df.groupby("Cliente")["NET"].sum().reset_index()
clientes = clientes.sort_values(by="NET", ascending=False)

produtos = df.groupby("Produto")["NET"].sum().reset_index()

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Carteira", f"R$ {total:,.0f}")
col2.metric("📊 Nº Fundos", len(fundos))
col3.metric("👤 Nº Clientes", df["Cliente"].nunique())

st.divider()

st.subheader("🏆 Top Fundos")
st.dataframe(fundos.head(15))

st.subheader("👥 Top Clientes")
st.dataframe(clientes.head(15))

st.subheader("📈 Top 10 Fundos")
st.bar_chart(fundos.head(10).set_index("Ativo")["NET_total"])

st.subheader("📊 Distribuição por Produto")
st.bar_chart(produtos.set_index("Produto")["NET"])
  
