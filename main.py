import streamlit as st
import pandas as pd
from datetime import datetime
import io
from fpdf import FPDF
import plotly.express as px
import unicodedata
import os

def limpar_texto(texto):
    if pd.isnull(texto):
        return ""
    texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('latin1', 'ignore').decode('latin1')
    return texto

st.set_page_config(page_title="ESoft - Modular 🚀", layout="wide")
st.title("EthSoft - Modular 🚀")

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists("data/daily-reports"):
    os.makedirs("data/daily-reports")

csv_path = os.path.join("data", "status_history.csv")
if "status_history" not in st.session_state:
    if os.path.exists(csv_path):
        st.session_state.status_history = pd.read_csv(csv_path)
    else:
        st.session_state.status_history = pd.DataFrame(columns=["data", "id", "unidade", "status"])
if "unit_status" not in st.session_state:
    st.session_state.unit_status = {}
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.today().date()
if "page" not in st.session_state:
    st.session_state.page = "Status"
# LISTA DE UNIDADES
lista_unidades = [
    "CRECHE MUNICIPAL ANTONIO FERNANDO DO REIS II (EXTENSÃO)",
    "CRECHE MUNICIPAL JEAN PIERRE DOS SANTOS MOLINA",
    "CRECHE MUNICIPAL JULIA MARIA DE JESUS",
    "EMEF CAIC - AYRTON SENNA DA SILVA",
    "EMEI NOSSA SENHORA DA ESPERANÇA",
    "EMEF LUIZ PINHO DE CARVALHO FILHO",
    "CRECHE COMUNITÁRIA CANTINHO DO ZEZINHO I",
    "CRECHE COMUNITÁRIA LAR CINDERELA",
    "CRECHE COMUNITÁRIA MUNDO DA CRIANÇA",
    "CRECHE COMUNITÁRIA VOVÓ LIBÂNIA",
    "CRECHE ESCOLA PEQUENO APRENDIZ",
    "CRECHE MUNICIPAL JOSEFA MARIA",
    "CRECHE MUNICIPAL CANTINHO DO ZEZINHO II",
    "CRECHE MUNICIPAL CORA CORALINA",
    "EMEIEF SEBASTIÃO RIBEIRO DA SILVA",
    "CRECHE MUNICIPAL EL SHADAY",
    "CRECHE MUNICIPAL GERALDA ERNESTINA",
    "CRECHE MUNICIPAL JULIO PEREIRA DE ANDRADE",
    "CRECHE MUNICIPAL LAR DA CRIANÇA FELIZ",
    "CRECHE MUNICIPAL MARIA JOSEFA",
    "CRECHE MUNICIPAL PAULO DE SOUZA",
    "CRECHE MUNICIPAL QUARENTENÁRIO (EXTENSÃO N SRA DA ESPERANÇA)",
    "CRECHE MUNICIPAL SANDRA ANTONELLI",
    "CRECHE MUNICIPAL SANTA TEREZINHA",
    "CRECHE MUNICIPAL SEITETSU IHA (ENG.)",
    "CRECHE MUNICIPAL VOVÔ JOSÉ CAMPELO",
    "EMEIEF ALBERTO SANTOS DUMONT",
    "EMEF ANTÔNIO PACÍFICO",
    "EMEF AUGUSTO SAINT'HILAIRE",
    "EMEI CARLOS CALDEIRA",
    "EMEI CIDADE DENAHA",
    "EMEI CLEMENTE FERREIRA",
    "EMEI DOM PEDRO I",
    "EMEF DR. MARIO COVAS JUNIOR",
    "EMEIEF DUQUE DE CAXIAS",
    "EMEI EDMUNDO CAPELLARI",
    "EMEIEF ERCÍLIA NOGUEIRA COBRA",
    "EMEF FRANCISCO MARTINS DOS SANTOS",
    "EMEI JOSÉ BORGES FERNANDES",
    "EMEF LIONS CLUBE",
    "EMEIEF MANOEL NASCIMENTO JÚNIOR",
    "EMEIEF MARIA DE LOURDES BATISTA",
    "EMEF MATTEO BEI II",
    "EMEI MONTEIRO LOBATO",
    "EMEIEF NILTON RIBEIRO",
    "EMEI PADRE JOSÉ DE ANCHIETA",
    "EMEI KELMA MARIA TOFFETTI GONÇALVE",
    "EMEIEF JOSÉ MEIRELLES",
    "EMEF LUIZ BENEDITINO FERREIRA",
    "EMEF PROF. LEONOR GUIMARÃES ALVES STOFFEL",
    "EMEF VERA LUCIA MACHADO MASSIS",
    "EMEIEF GILSON KOOL MONTEIRO",
    "EMEF PROFESSOR LÚCIO MARTINS RODRIGUES",
    "EMEF PROFESSOR RENAN ALVES LEITE",
    "EMEI PROFESSORA MARIA ELIZABETH RAMOS DA SILVA",
    "EMEI PROVÍNCIA DE OKINAWA",
    "EMEF RAQUEL DE CASTRO FERREIRA",
    "EMEIEF REGINA CÉLIA DOS SANTOS",
    "CRECHE COMUNITÁRIA PENIEL",
    "EMEF UNIÃO CÍVICA FEMININA",
    "EMEIEF VILA EMA",
    "EMEI VILA JÓQUEI",
    "CRECHE MUNICIPAL PROFª ONDINA MARQUES DE MELO",
    "CRECHE VILA NOVA",
    "CRECHE MUNICIPAL MARGARIDA",
    "CRECHE PROFESSORA ANA CRISTINA SANTOS",
    "EMEIEF MANOEL NASCIMENTO JÚNIOR II",
    "CRECHE MUNICIPAL TIO JOSÉ",
    "DAE DEPOSITO DE ALIMENTOS",
    "DEMAS",
    "CCO - CENTRO DE MONITORAMENTO DA PREFEITURA",
    "CEJACON “CENTRO M. DE EDUCAÇÃO SUPLETIVA – ÁREA CONTINENTAL”",
    "CEJAIN “CENTRO MUNICIPAL DE EDUCAÇÃO SUPLETIVA",
    "AMEI NARIZINHO",
    "AMEI VISCONDE DE SABUGOSA",
    "CRECHE COMUNITÁRIA NAYLA AMOR A VIDA I",
    "CRECHE COMUNITÁRIA NAYLA AMOR A VIDA II",
    "CRECHE MUNICIPAL GRUPO DA PRECE",
    "CRECHE NOSSA SENHORA DA ESPERANÇA",
    "EMEI ADILZA DE O. ROSA SOBRAL",
    "EMEIEF MAURO APARECIDO GODOY",
    "EMEF NUMAA - ANA LUCIA ALMEIDA DE OLIVEIRA",
    "EMEF PASTOR JOAQUIM RODRIGUES DA SILVA",
    "EMEF CAROLINA DANTAS",
    "EMEI ANUAR FRAHYA",
    "CRECHE MUNICIPAL PROFº CELSO EDUARDO",
    "AMEI EMILIA",
    "CRECHE MUNICIPAL EDUARDO FURKINI",
    "EMEF RAUL ROCHA DO AMARAL",
    "EMEIEF EULINA TRINDADE",
    "EMEF LAURA FILGUEIRAS",
    "AMEI NARIZINHO II",
    "CRECHE MUNICIPAL CATIAPOÃ",
    "EMEF OCTÁVIO DE CÉSARE",
    "AMEI REI PELÉ",
    "EMEF ARMINDO RAMOS",
    "EMEF PROFESSOR JACOB ANDRADE CÂMARA",
    "PROJETO ESPECIAL 2 - 11/12",
    "EMEI MATTEO BEI - 24/01",
    "EMEF JORGE BIERRENBACH SENRA - 27/02",
    "EMEF NUMAA II - ANA LUCIA ALMEIDA DE OLIVEIRA - 23/02",
    "CRECHE ESCOLA PEQUENO APRENDIZ  - 16/03",
    "CRECHE MUNICIPAL CANTINHO DO CÉU",
    "CRECHE MUNICIPAL CRIANÇA ESPERANÇA - 17/03",
    "EMEF ANTÔNIO FERNANDO DOS REIS - 15/01",
    "EMEIEF JONAS RODRIGUES - 15/03",
    "EMEF PROFESSOR CONSTANTE LUCIANO C. HOULMOUT - 24/03",
    "EMEF REPÚBLICA DE PORTUGAL - 21/03",
    "BIBLIOTECA MUNICIPAL SÃO VICENTE - 16/02",
    "CRECHE MUNICIPAL VOVÔ RAIMUNDO - 05/03"
]
unidades = [{"id": i + 1, "unidade": nome} for i, nome in enumerate(lista_unidades)]

def exibir_status():
    st.header("Status das Unidades 📊")
    st.session_state.selected_date = st.date_input("Selecione a data do relatório", value=st.session_state.selected_date)
    col1, col2, col3 = st.columns([1, 6, 3])
    col1.markdown("**ID**")
    col2.markdown("**Unidade**")
    col3.markdown("**Status**")
    online_count, offline_count = 0, 0
    for unidade in unidades:
        c1, c2, c3 = st.columns([1, 6, 3])
        c1.write(unidade["id"])
        c2.write(unidade["unidade"])
        status_key = f"status_{unidade['id']}"
        status = c3.toggle("", key=status_key, value=st.session_state.unit_status.get(unidade["id"], True))
        st.session_state.unit_status[unidade["id"]] = status
        if status:
            online_count += 1
        else:
            offline_count += 1
    st.markdown("---")
    st.subheader("Resumo Atual")
    st.write(f"**Total de Unidades:** {len(unidades)}")
    st.write(f"**Online ✅:** {online_count}")
    st.write(f"**Offline ❌:** {offline_count}")
    if st.button("Gerar Relatório 📄"):
        data_selecionada = st.session_state.selected_date
        registros = [
            {
                "data": pd.Timestamp(data_selecionada),
                "id": unidade["id"],
                "unidade": unidade["unidade"],
                "status": "ON" if st.session_state.unit_status[unidade["id"]] else "OFF"
            }
            for unidade in unidades
        ]
        df_registros = pd.DataFrame(registros)
        st.session_state.status_history = pd.concat(
            [st.session_state.status_history, df_registros], ignore_index=True)
        st.session_state.status_history.to_csv(csv_path, index=False, encoding="utf-8")
        nome_arquivo = f"relatorio_{data_selecionada.strftime('%Y-%m-%d')}.pdf"
        caminho_arquivo = os.path.join("data/daily-reports", nome_arquivo)
        pdf = gerar_pdf(df_registros, f"Relatório do dia {data_selecionada.strftime('%d/%m/%Y')}")
        pdf.output(caminho_arquivo)
        st.success(f"Relatório salvo: {caminho_arquivo}")
        st.session_state.page = "Dashboard"
        st.rerun()

def gerar_pdf(df_hist, report_title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=9)
    pdf.cell(200, 10, txt=limpar_texto(report_title), ln=True, align='C')
    pdf.ln(10)
    total_reg = len(df_hist)
    soma_on = (df_hist["status"] == "ON").sum()
    soma_off = (df_hist["status"] == "OFF").sum()
    pct_on = (soma_on / total_reg) * 100 if total_reg > 0 else 0
    pct_off = (soma_off / total_reg) * 100 if total_reg > 0 else 0
    pdf.cell(200, 10, txt=f"Total Registros: {total_reg}", ln=True)
    pdf.cell(200, 10, txt=f"ON: {soma_on} ({pct_on:.2f}%)", ln=True)
    pdf.cell(200, 10, txt=f"OFF: {soma_off} ({pct_off:.2f}%)", ln=True)
    pdf.ln(5)
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(40, 10, "Data", border=1, fill=True)
    pdf.cell(110, 10, "Unidade", border=1, fill=True)
    pdf.cell(30, 10, "Status", border=1, fill=True)
    pdf.ln()
    pdf.set_font("Arial", '', 8)
    for _, row in df_hist.iterrows():
        data = limpar_texto(str(row["data"].date()))
        unidade = limpar_texto(row["unidade"])
        status = limpar_texto(row["status"])
        pdf.cell(40, 10, data, border=1)
        pdf.cell(110, 10, unidade[:60], border=1)
        pdf.cell(30, 10, status, border=1)
        pdf.ln()
    return pdf

def exibir_dashboard():
    st.header("Dashboard de Relatórios 📈")
    df_hist = st.session_state.status_history.copy()
    if df_hist.empty:
        st.warning("Nenhum relatório gerado ainda.")
        return
    df_hist["data"] = pd.to_datetime(df_hist["data"])
    data_inicio, data_fim = st.date_input("Filtrar por período:", value=[df_hist["data"].min().date(), df_hist["data"].max().date()])
    df_filtrado = df_hist[(df_hist["data"] >= pd.Timestamp(data_inicio)) & (df_hist["data"] <= pd.Timestamp(data_fim))]

    filtro_tipo = st.radio("Agrupar por:", ["Diário", "Semanal", "Mensal"])
    if filtro_tipo == "Diário":
        df_agrupado = df_filtrado.groupby(df_filtrado["data"].dt.date)["status"].value_counts().unstack().fillna(0)
    elif filtro_tipo == "Semanal":
        df_agrupado = df_filtrado.groupby(df_filtrado["data"].dt.to_period("W").apply(lambda r: r.start_time))["status"].value_counts().unstack().fillna(0)
    else:
        df_agrupado = df_filtrado.groupby(df_filtrado["data"].dt.to_period("M").dt.to_timestamp())["status"].value_counts().unstack().fillna(0)

    df_agrupado["ON"] = df_agrupado.get("ON", 0)
    df_agrupado["OFF"] = df_agrupado.get("OFF", 0)
    df_agrupado["Total"] = df_agrupado["ON"] + df_agrupado["OFF"]
    df_agrupado["% ON"] = (df_agrupado["ON"] / df_agrupado["Total"]) * 100

    st.dataframe(df_agrupado[["ON", "OFF", "% ON"]].style.format({"% ON": "{:.2f}%"}))

    total_reg = len(df_filtrado)
    soma_on = (df_filtrado["status"] == "ON").sum()
    soma_off = (df_filtrado["status"] == "OFF").sum()
    pct_on = (soma_on / total_reg) * 100 if total_reg > 0 else 0
    pct_off = (soma_off / total_reg) * 100 if total_reg > 0 else 0
    st.markdown("---")
    st.subheader("Resumo Geral")
    st.write(f"**Total de Registros:** {total_reg}")
    st.write(f"**ON ✅:** {soma_on} ({pct_on:.2f}%)")
    st.write(f"**OFF ❌:** {soma_off} ({pct_off:.2f}%)")

    dados_graf = {"Status": ["ON ✅", "OFF ❌"], "Total": [soma_on, soma_off]}
    fig = px.pie(pd.DataFrame(dados_graf), names="Status", values="Total", title="Status das Unidades",
                 color="Status", color_discrete_map={"ON ✅": "green", "OFF ❌": "red"})
    st.plotly_chart(fig, use_container_width=True)

    if st.button("Exportar para PDF 🖨️"):
        pdf = gerar_pdf(df_filtrado, "Relatório de Status")
        pdf_output = pdf.output(dest='S').encode('latin1')
        output = io.BytesIO(pdf_output)
        st.download_button("Download PDF", data=output, file_name="relatorio_ethsoft.pdf", mime="application/pdf")

    if st.button("Voltar ↩️"):
        st.session_state.page = "Status"
        st.rerun()

if st.session_state.page == "Status":
    exibir_status()
elif st.session_state.page == "Dashboard":
    exibir_dashboard()
