import streamlit as st
import pandas as pd
import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Controlo de Stock & Caixa", page_icon="📱", layout="centered")

if 'entradas' not in st.session_state:
    st.session_state.entradas = pd.DataFrame(columns=['ID', 'Data', 'Gerente', 'Vendedor', 'Produto', 'Qtd Entregue'])
if 'fechos' not in st.session_state:
    st.session_state.fechos = pd.DataFrame(columns=['ID', 'Data', 'Gerente', 'Vendedor', 'Produto', 'Preço', 'St Inicial', 'Entradas', 'Quebras', 'Saldo Físico', 'Qtd Vendida', 'Valor Devido', 'Dinheiro Entregue', 'Falta_Sobra'])

UTILIZADORES = {"abdul": {"nome": "Abdul Aziz (Admin)", "senha": "123", "funcao": "Admin"}, "Rishad": {"nome": "Gerente Rishad", "senha": "456", "funcao": "Gerente"}}
PRODUTOS = {"Pão Grande": 12.00, "Pão Redondo": 10.00, "Pãozinho": 5.00, "Refresco Garrafa": 25.00, "Plástico": 3.00, "Doce 1": 1.00, "Doce da Índia": 5.00, "Pastilha": 2.00, "Chupa": 2.00, "Yogueta": 5.00, "Pipoca": 5.00, "Shamussa": 6.00, "Gulabo": 5.00, "Badjia": 2.00, "Argola": 5.00, "Refresco Txoti": 30.00, "Santal 500ml": 75.00, "Ceres 500ml": 80.00, "Frozzy": 15.00, "Frozzy Energético": 25.00, "Dragon": 50.00, "Água Pequena": 20.00, "Água Grande": 50.00, "Arrofada": 5.00}
VENDEDORES = ["Vendedor Ali"]

def gerar_pdf_entrada(data_row):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = [Paragraph("NOTA DE ENTRADA DE MERCADORIA", ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0284c7'))), Spacer(1, 10)]
    meta_text = f"<b>Data:</b> {data_row['Data']}<br/><b>Gerente:</b> {data_row['Gerente']}<br/><b>Vendedor:</b> {data_row['Vendedor']}"
    story.append(Paragraph(meta_text, styles['Normal']))
    story.append(Spacer(1, 15))
    t = Table([["Produto", "Qtd Entregue"], [data_row['Produto'], str(data_row['Qtd Entregue'])]], colWidths=[200, 100])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1'))]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

def gerar_pdf_fecho(data_row):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = [Paragraph("RELATÓRIO DE FECHO DE CAIXA", ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0f172a'))), Spacer(1, 10)]
    meta_text = f"<b>Data:</b> {data_row['Data']}<br/><b>Auditado Por:</b> {data_row['Gerente']}<br/><b>Vendedor:</b> {data_row['Vendedor']}"
    story.append(Paragraph(meta_text, styles['Normal']))
    story.append(Spacer(1, 15))
    data = [["Campo", "Valor"], ["Produto", str(data_row['Produto'])], ["Preço Unitário", f"{data_row['Preço']} MT"], ["Stock Inicial", str(data_row['St Inicial'])], ["Entradas", str(data_row['Entradas'])], ["Quebras", str(data_row['Quebras'])], ["Saldo Físico (Sobra)", str(data_row['Saldo Físico'])], ["Quantidade Vendida", str(data_row['Qtd Vendida'])], ["Valor Devido (Sistema)", f"{data_row['Valor Devido']} MT"], ["Dinheiro Entregue", f"{data_row['Dinheiro Entregue']} MT"], ["FALTA / SOBRA", f"{data_row['Falta_Sobra']} MT"]]
    t = Table(data, colWidths=[200, 150])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')), ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#fee2e2') if float(data_row['Falta_Sobra']) < 0 else colors.HexColor('#dcfce7'))]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔑 Login no Sistema")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in UTILIZADORES and UTILIZADORES[usuario]["senha"] == senha:
            st.session_state.autenticado = True
            st.session_state.usuario_logado = usuario
            st.session_state.nome_completo = UTILIZADORES[usuario]["nome"]
            st.session_state.funcao = UTILIZADORES[usuario]["funcao"]
            st.rerun()
        else: st.error("Usuário ou senha incorretos!")
else:
    st.sidebar.write(f"👤 Conectado como: **{st.session_state.nome_completo}**")
    if st.sidebar.button("Sair / Logout"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("📱 Gestão de Stock e Vendas")
    aba1, aba2, aba3 = st.tabs(["📥 Injetar Mercadoria", "💰 Fazer Fecho de Vendas", "📊 Painel Geral (Admin)"])
    
    with aba1:
        st.header("Entrada de Mercadoria")
        vendedor_e = st.selectbox("Escolha o Vendedor", VENDEDORES, key="v_e")
        produto_e = st.selectbox("Escolha o Produto", list(PRODUTOS.keys()), key="p_e")
        qtd_e = st.number_input("Quantidade Entregue ao Vendedor", min_value=1, step=1, value=50)
        if st.button("Gravar Entrada e Gerar Recibo"):
            nova_linha = {'ID': f"ENT-{len(st.session_state.entradas)+1:03d}", 'Data': datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), 'Gerente': st.session_state.nome_completo, 'Vendedor': vendedor_e, 'Produto': produto_e, 'Qtd Entregue': qtd_e}
            st.session_state.entradas = pd.concat([st.session_state.entradas, pd.DataFrame([nova_linha])], ignore_index=True)
            st.success("Entrada registada com sucesso!")
            st.download_button(label="📄 Descarregar PDF para Impressão", data=gerar_pdf_entrada(nova_linha), file_name=f"Entrada_{nova_linha['ID']}.pdf", mime="application/pdf")

    with aba2:
        st.header("Fecho de Vendas e Caixa")
        vendedor_f = st.selectbox("Escolha o Vendedor", VENDEDORES, key="v_f")
        produto_f = st.selectbox("Escolha o Produto", list(PRODUTOS.keys()), key="p_f")
        preco = PRODUTOS[produto_f]
        st.write(f"Preço Unitário: **{preco:.2f} MT**")
        st_inicial = st.number_input("Stock Inicial na Banca", min_value=0, step=1, value=20)
        entradas_f = st.number_input("Entradas do Turno", min_value=0, step=1, value=100)
        quebras = st.number_input("Quebras / Produtos Estragados", min_value=0, step=1, value=2)
        saldo_f = st.number_input("Sobra Física no Fim do Dia", min_value=0, step=1, value=18)
        
        qtd_vendida = (st_inicial + entradas_f) - quebras - saldo_f
        valor_devido = qtd_vendida * preco
        st.info(f"📊 Qtd Vendida: **{qtd_vendida}** | Valor Total por Receber: **{valor_devido:.2f} MT**")
        
        dinheiro_entregue = st.number_input("Dinheiro Físico Entregue (MT)", min_value=0.0, value=float(valor_devido))
        falta_sobra = dinheiro_entregue - valor_devido
        if falta_sobra < 0: st.error(f"⚠️ FALTOU DINHEIRO! Falta: **{falta_sobra:.2f} MT**")
        else: st.success("✅ Caixa sem faltas.")

        if st.button("Gravar Fecho e Gerar Relatório"):
            novo_fecho = {'ID': f"FCH-{len(st.session_state.fechos)+1:03d}", 'Data': datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), 'Gerente': st.session_state.nome_completo, 'Vendedor': vendedor_f, 'Produto': produto_f, 'Preço': preco, 'St Inicial': st_inicial, 'Entradas': entradas_f, 'Quebras': quebras, 'Saldo Físico': saldo_f, 'Qtd Vendida': qtd_vendida, 'Valor Devido': valor_devido, 'Dinheiro Entregue': dinheiro_entregue, 'Falta_Sobra': falta_sobra}
            st.session_state.fechos = pd.concat([st.session_state.fechos, pd.DataFrame([novo_fecho])], ignore_index=True)
            st.success("Fecho guardado com sucesso!")
            st.download_button(label="📄 Descarregar PDF do Fecho", data=gerar_pdf_fecho(novo_fecho), file_name=f"Fecho_{novo_fecho['ID']}.pdf", mime="application/pdf")

    with aba3:
        st.header("Painel Geral de Auditoria")
        st.subheader("Histórico Recente de Entradas")
        st.dataframe(st.session_state.entradas)
        st.subheader("Histórico Recente de Fechos")
        st.dataframe(st.session_state.fechos)
