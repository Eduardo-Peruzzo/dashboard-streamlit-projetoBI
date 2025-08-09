import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

# CSS para texto grande
st.markdown("""
    <style>
        .big-font { font-size:24px !important; }
        .stMetric { font-size: 22px !important; }
    </style>
""", unsafe_allow_html=True)

# Leitura do Excel
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

df = load_data("vendas.xlsx")
df["Date"] = pd.to_datetime(df["Date"])
df["Produto"] = df["Category"].astype(str) + " - R$ " + df["Price"].astype(str)

# ---------------- Filtros gerais ----------------
st.title("📊 Dashboard de Vendas")
st.markdown("<p class='big-font'>Acompanhe suas vendas de forma simples.</p>", unsafe_allow_html=True)

anos = sorted(df["Date"].dt.year.unique())
meses = sorted(df["Date"].dt.month.unique())
dias = sorted(df["Date"].dt.day.unique())

col1, col2, col3 = st.columns(3)

with col1:
    ano = st.selectbox("Ano", ["Tudo"] + anos)
with col2:
    mes = st.selectbox("Mês", ["Tudo"] + meses)
with col3:
    dia = st.selectbox("Dia", ["Tudo"] + dias)

df_filtrado = df.copy()
if ano != "Tudo":
    df_filtrado = df_filtrado[df_filtrado["Date"].dt.year == ano]
if mes != "Tudo":
    df_filtrado = df_filtrado[df_filtrado["Date"].dt.month == mes]
if dia != "Tudo":
    df_filtrado = df_filtrado[df_filtrado["Date"].dt.day == dia]

# ---------------- KPIs ----------------
total_vendas = df_filtrado["Total Vendas"].sum()
valor_total = df_filtrado["Valor Total"].sum()
metodo_mais_usado = df_filtrado[["Qty PIX/Dinheiro", "Qty Crédito", "Qty Débito"]].sum().idxmax()

col1, col2, col3 = st.columns(3)
col1.metric("🛒 Total Vendas", f"{total_vendas}")
col2.metric("💰 Valor Total", f"R$ {valor_total:,.2f}")
col3.metric("💳 Método mais usado", metodo_mais_usado.replace("Qty ", ""))

# ---------------- Gráfico de métodos de pagamento ----------------
pagamentos = {
    "PIX/Dinheiro": df_filtrado["Qty PIX/Dinheiro"].sum(),
    "Crédito": df_filtrado["Qty Crédito"].sum(),
    "Débito": df_filtrado["Qty Débito"].sum(),
}
pag_df = pd.DataFrame(list(pagamentos.items()), columns=["Método", "Quantidade"])
fig_pizza = px.pie(pag_df, values="Quantidade", names="Método", title="Formas de Pagamento", hole=0.3)
st.plotly_chart(fig_pizza, use_container_width=True)

# ---------------- Ranking por categoria (barras horizontais, sem rótulo do eixo Y) ----------------
ranking_df = df_filtrado.groupby("Category")["Total Vendas"].sum().reset_index()
ranking_df = ranking_df.sort_values("Total Vendas", ascending=True)  # Menor p/ cima

fig_ranking = px.bar(
    ranking_df,
    x="Total Vendas",
    y="Category",
    orientation="h",
    title="Ranking de Vendas por Categoria",
    text_auto=True
)
fig_ranking.update_layout(yaxis_title=None)  # Remove o "Category"
st.plotly_chart(fig_ranking, use_container_width=True, config={"staticPlot": True})

# ---------------- Detalhamento por preço dentro da categoria ----------------
categoria_selecionada = st.selectbox(
    "Selecione uma categoria para ver os preços",
    sorted(df_filtrado["Category"].unique())
)

detalhe_df = df_filtrado[df_filtrado["Category"] == categoria_selecionada]
ranking_precos = detalhe_df.groupby("Price")["Total Vendas"].sum().reset_index()
ranking_precos = ranking_precos.sort_values("Total Vendas", ascending=True)  # Menor p/ cima

# Converter preço para string formatada (para exibir no gráfico)
ranking_precos["Preço Formatado"] = ranking_precos["Price"].apply(lambda x: f"R$ {x:,.2f}")

fig_precos = px.bar(
    ranking_precos,
    x="Total Vendas",
    y="Preço Formatado",
    orientation="h",
    title=f"Ranking de Vendas por Preço - {categoria_selecionada}",
    text="Preço Formatado"  # Exibir o preço ao lado da barra
)
fig_precos.update_layout(yaxis_title=None)  # Remove rótulo do eixo Y
st.plotly_chart(fig_precos, use_container_width=True, config={"staticPlot": True})
