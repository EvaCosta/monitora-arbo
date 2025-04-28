import streamlit as st
import streamlit.components.v1 as components
from process_data import processar_arquivos
import pyrebase
import pandas as pd
import base64
import os
import plotly.express as px

# Configuração do Firebase
firebaseConfig = {
    "apiKey": "AIzaSyDjeRvV8yHAUmzDbiv2laM5tVM5iFXBByw",
    "authDomain": "monitora-arbo.firebaseapp.com",
    "projectId": "monitora-arbo",
    "storageBucket": "monitora-arbo.appspot.com",
    "messagingSenderId": "401575058454",
    "appId": "1:401575058454:web:52475e9a1be4acfe4fa937",
    "measurementId": "G-2CBGBT9JHG",
    "databaseURL": "https://monitora-arbo.firebaseio.com"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Inicializar session state para login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Função para download estilizado
def download_dataframe(df, filename, label):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'''
    <a href="data:file/csv;base64,{b64}" download="{filename}">
        <button style="
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            border-radius: 12px;
            cursor: pointer;">
            ⬇️ {label}
        </button>
    </a>
    '''
    st.markdown(href, unsafe_allow_html=True)

# Função para login
def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        except Exception as e:
            st.error(f"Falha no login. Erro: {e}")

# Função para tela de processamento
def processamento(user_email):
    st.title("Painel de Dados")


    pasta_dados = "dados_salvos"
    os.makedirs(pasta_dados, exist_ok=True)


    if user_email in ["vigilanciaambientalds7@gmail.com"]:
        #Usuário VA: apenar visualiza dados já processados
        try:
            df_va = pd.read_excel(os.path.join(pasta_dados, "chico_filtrado_va.xlsx"))
        except Exception as e:
            st.error(f"Arquivo de dados não foi gerado pelo administrador.")
            return

    else:
        uploaded_files = st.file_uploader("Envie um ou mais arquivos .xls", type=["xls"], accept_multiple_files=True)

        if uploaded_files:
            pasta_temp = "temp_upload"
            os.makedirs(pasta_temp, exist_ok=True)

            # Salvar todos os arquivos enviados
            for uploaded_file in uploaded_files:
                caminho = os.path.join(pasta_temp, uploaded_file.name)
                with open(caminho, "wb") as f:
                    f.write(uploaded_file.getbuffer())
        
        
            try:
                df_ve, df_va = processar_arquivos(pasta_temp)
              
                df_ve.to_excel(os.path.join(pasta_dados, "chico_filtrado_ve.xlsx"), index=False, engine='openpyxl')
                df_va.to_excel(os.path.join(pasta_dados, "chico_filtrado_va.xlsx"), index=False, engine='openpyxl')

                st.success("Arquivos processados e salvos com sucesso!")

            except Exception as e:
                st.error(f"Erro ao processar os arquivos: {e}")
                return

        else:
            st.warning("Por favor, envie os arquivos para processar os dados.")
            return
        
        
        if user_email == "vigilanciaepidemiologicadsvii@gmail.com":
            st.subheader("🦠 Casos dos últimos 60 dias (VE)")
            st.dataframe(df_ve)
            download_dataframe(df_va, "chico_filtrado_ve.csv", "Download VE")
            if 'OPORTUNIDADE_SINAN' in df_va.columns:
                st.subheader("📈 Oportunidades SINAN - VE")
                fig = px.bar(df_va, x=df_va.columns[0], y='OPORTUNIDADE_SINAN', title="Gráfico de Oportunidades SINAN - VE")
                st.plotly_chart(fig, use_container_width=True)
        elif user_email == "vigilanciaambientalds7@gmail.com":
            st.subheader("🦠 Casos dos Últimos 30 Dias (VA)")
            st.dataframe(df_va)
            download_dataframe(df_va, "chico_filtrado_va.csv", "Download VA")
            if 'OPORTUNIDADE_SINAN' in df_va.columns:
                fig = px.bar(df_va, x=df_va.columns[0], y='OPORTUNIDADE_SINAN', title="Oportunidades SINAN - VA")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.subheader("🦠 Casos dos Últimos 60 Dias")
            st.dataframe(df_ve)
            download_dataframe(df_ve, "chico_filtrado_ve.csv", "Download VE")
            st.subheader("🦠 Casos dos Últimos 30 Dias")
            st.dataframe(df_va)
            download_dataframe(df_va, "chico_filtrado_va.csv", "Download VA")

        # st.subheader("🗺️ Mapa de Oportunidades")
        # components.html(
        #     """
        #     <iframe 
        #         src="https://www.google.com/maps/d/embed?mid=1Gaigj7AB0cBk6ousCK2V6Qa3-pgMQ0U&ehbc=2E312F" 
        #         width="100%" 
        #         height="480"
        #         style="border:0;"
        #         allowfullscreen=""
        #         loading="lazy">
        #     </iframe>
        #     """,
        #     height=500,
            # )

       

# Função de painel admin
def admin_panel():
    if st.button("Cadastrar Novo Usuário ➕"):
        st.session_state.show_register = True

    if st.session_state.show_register:
        st.subheader("👤 Cadastro de Novo Usuário")
        new_email = st.text_input("Novo email")
        new_password = st.text_input("Nova senha", type="password")

        if st.button("Cadastrar novo usuário"):
            try:
                auth.create_user_with_email_and_password(new_email, new_password)
                st.success(f"Usuário {new_email} criado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao criar usuário: {e}")

# Roteamento com base no login
if not st.session_state.logged_in:
    login()
else:
    user_email = st.session_state.user['email']
    processamento(user_email)

    if user_email == "raquelmlacioli@gmail.com":
        st.markdown("---")
        admin_panel()
