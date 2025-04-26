import streamlit as st
import os
import sys
import requests
import logging
from models import get_conversation_chain, get_available_brands
from dotenv import load_dotenv
import traceback

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da página Streamlit
st.set_page_config(
    page_title="Especialista em Impermeabilização",
    page_icon="💧",
    layout="wide"
)

# Função para verificar a validade da chave da API do Groq
def verify_groq_api_key(api_key):
    """
    Verifica se a chave da API do Groq é válida fazendo uma chamada de teste.
    Retorna (True, None) se for válida, (False, erro) se for inválida.
    """
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return True, None
        else:
            error_message = f"Status: {response.status_code} - {response.text}"
            return False, error_message
    except Exception as e:
        return False, str(e)

# Função para verificar se o diretório vectordb existe
def check_vectordb_directory():
    """
    Verifica se o diretório vectordb existe e tem conteúdo.
    """
    if not os.path.exists("vectordb"):
        logger.error("Diretório vectordb não encontrado")
        return False, "O diretório vectordb não foi encontrado. Execute o script ingest.py primeiro."
    
    if not os.listdir("vectordb"):
        logger.error("Diretório vectordb está vazio")
        return False, "O diretório vectordb está vazio. Execute o script ingest.py para processar os documentos."
    
    logger.info(f"Diretório vectordb encontrado com conteúdo: {os.listdir('vectordb')}")
    return True, None

# Função para inicializar a conversa para uma marca
def initialize_conversation(brand_folder, brand_display_name):
    """
    Inicializa a conversa para a marca selecionada e trata possíveis erros.
    """
    try:
        logger.info(f"Inicializando conversa para a marca: {brand_folder}")
        conversation = get_conversation_chain(brand_folder)
        logger.info(f"Conversa inicializada com sucesso para {brand_folder}")
        
        # Limpa o histórico
        st.session_state.chat_history = []
        st.session_state.messages = []
        
        # Atualiza o estado da conversa
        st.session_state.selected_brand = brand_folder
        st.session_state.conversation = conversation
        
        return True, None
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Erro ao inicializar conversa para {brand_folder}: {str(e)}\n{error_details}")
        return False, f"Erro ao carregar a conversa para a marca {brand_display_name}: {str(e)}"

# Título da aplicação
st.title("💧 Especialista em Impermeabilização")
st.markdown("""
### Seu assistente virtual para produtos de impermeabilização

Este sistema utiliza inteligência artificial para responder suas dúvidas sobre produtos de impermeabilização 
de diversas marcas, com base nas fichas técnicas oficiais dos produtos.
""")

# Verifica se o diretório vectordb existe e tem conteúdo
vectordb_exists, vectordb_error = check_vectordb_directory()
if not vectordb_exists:
    st.error(f"""
    ⚠️ **Problema com o banco de dados vetorial**
    
    {vectordb_error}
    
    No Streamlit Cloud, isso pode ocorrer porque o diretório não foi incluído no repositório Git.
    Verifique o arquivo README_DEPLOY.md para instruções sobre como resolver este problema.
    """)
    
    # Mostra informações para debug
    st.expander("Informações para debug").info(f"""
    Diretório atual: {os.getcwd()}
    Conteúdo do diretório atual: {os.listdir('.')}
    """)
    
    # Oferece a opção de criar o banco de dados
    if st.button("Iniciar Processamento de Documentos", type="primary"):
        try:
            import ingest
            ingest.main()
            st.success("Processamento concluído com sucesso! Recarregando a aplicação...")
            st.rerun()
        except Exception as e:
            st.error(f"Erro durante o processamento: {str(e)}")
    
    st.stop()

# Inicializa o estado da sessão se não existir
if "conversation" not in st.session_state:
    st.session_state.conversation = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_brand" not in st.session_state:
    st.session_state.selected_brand = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_error" not in st.session_state:
    st.session_state.conversation_error = None

# Tenta obter a chave da API do Groq de múltiplas fontes
groq_api_key = os.environ.get("GROQ_API_KEY")

# Limpa a chave se existir (remove espaços e caracteres invisíveis)
if groq_api_key:
    groq_api_key = groq_api_key.strip()

# Tenta obter a chave dos segredos do Streamlit se não encontrada no ambiente
if not groq_api_key and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets["GROQ_API_KEY"].strip()
    # Adiciona a chave ao ambiente para que o módulo models.py possa acessá-la
    os.environ["GROQ_API_KEY"] = groq_api_key
    logger.info("Chave da API obtida dos segredos do Streamlit")

# Verifica se a chave existe
if not groq_api_key:
    st.error("""
    ⚠️ **Chave da API do Groq não encontrada!**
    
    Para usar este aplicativo, você precisa definir sua chave da API do Groq:
    
    1. No Streamlit Cloud: Adicione a variável `GROQ_API_KEY` nas configurações de segredos do app.
    2. Localmente: Crie um arquivo `.env` na raiz do projeto com `GROQ_API_KEY=sua_chave_aqui`
       ou um arquivo `.streamlit/secrets.toml` com `GROQ_API_KEY = "sua_chave_aqui"`
    """)
    
    # Interface para inserir a chave manualmente
    with st.expander("Inserir chave manualmente"):
        manual_key = st.text_input("Chave da API do Groq", type="password")
        if st.button("Salvar e Usar Chave") and manual_key:
            # Verifica se a chave inserida é válida
            is_valid, error = verify_groq_api_key(manual_key.strip())
            if is_valid:
                groq_api_key = manual_key.strip()
                os.environ["GROQ_API_KEY"] = groq_api_key
                st.success("✅ Chave válida! A aplicação está pronta para uso.")
                st.rerun()
            else:
                st.error(f"❌ Chave inválida! Erro: {error}")
    
    if not groq_api_key:
        st.stop()
else:
    # Verifica se a chave existente é válida
    is_valid, error = verify_groq_api_key(groq_api_key)
    if not is_valid:
        st.error(f"""
        ⚠️ **Chave da API do Groq inválida!**
        
        A chave da API encontrada não é válida. Erro: {error}
        
        Possíveis causas:
        1. A chave está incorreta ou expirou
        2. Há um problema de rede ou firewall
        3. A chave tem caracteres invisíveis ou formatação incorreta
        """)
        
        # Interface para inserir a chave manualmente
        with st.expander("Inserir chave manualmente"):
            manual_key = st.text_input("Chave da API do Groq", type="password")
            if st.button("Salvar e Usar Chave") and manual_key:
                # Verifica se a chave inserida é válida
                is_valid, error = verify_groq_api_key(manual_key.strip())
                if is_valid:
                    groq_api_key = manual_key.strip()
                    os.environ["GROQ_API_KEY"] = groq_api_key
                    st.success("✅ Chave válida! A aplicação está pronta para uso.")
                    st.rerun()
                else:
                    st.error(f"❌ Chave inválida! Erro: {error}")
        
        if not is_valid:
            st.stop()

# Verifica se existem bancos de dados vetoriais
try:
    brands = get_available_brands()
    if not brands:
        st.warning("""
        ⚠️ **Nenhum banco de dados vetorial encontrado!**
        
        Para usar este aplicativo, você precisa primeiro processar os documentos e criar os bancos de dados vetoriais:
        
        1. Execute o script `ingest.py` para processar os documentos PDF e criar os bancos de dados.
        """)
        if st.button("Processar Documentos", type="primary"):
            try:
                import ingest
                ingest.main()
                st.success("Processamento concluído com sucesso! Recarregando a aplicação...")
                st.rerun()
            except Exception as e:
                st.error(f"Erro durante o processamento: {str(e)}")
        st.stop()
except Exception as e:
    st.error(f"""
    ⚠️ **Erro ao carregar bancos de dados vetoriais**
    
    Ocorreu um erro ao tentar carregar os bancos de dados vetoriais: {str(e)}
    
    Consulte os logs para mais detalhes.
    """)
    logger.error(f"Erro ao carregar bancos de dados vetoriais: {str(e)}")
    st.stop()

# Sidebar com seleção de marca
with st.sidebar:
    st.header("Selecione a Marca")
    
    # Transformar a lista de dicionários em uma lista de nomes para exibição
    brand_options = [brand["display"] for brand in brands]
    
    # Dropdown para seleção de marca
    selected_brand_display = st.selectbox(
        "Marca:",
        options=brand_options,
        index=0 if brand_options else None,
        key="brand_selector"
    )
    
    # Encontrar o objeto completo da marca selecionada
    selected_brand_obj = next((brand for brand in brands if brand["display"] == selected_brand_display), None)
    
    # Botão explícito para selecionar a marca
    if st.button("Confirmar Seleção", type="primary"):
        if selected_brand_obj:
            # Reinicializa a conversa para a marca selecionada
            success, error_msg = initialize_conversation(selected_brand_obj["folder"], selected_brand_display)
            if success:
                st.success(f"✅ Marca {selected_brand_display} selecionada com sucesso!")
                st.session_state.conversation_error = None
            else:
                st.error(error_msg)
                st.session_state.conversation_error = error_msg
        else:
            st.error("Por favor, selecione uma marca válida.")
    
    # Exibe o status atual da seleção
    if st.session_state.selected_brand:
        st.success(f"Marca atual: {selected_brand_display}")
    
    # Exibe mensagem de erro se houver
    if st.session_state.conversation_error:
        st.error(f"Erro: {st.session_state.conversation_error}")
        
    # Botão para forçar a reinicialização da conversa (para quando ocorrerem erros)
    if st.button("Reinicializar Conversa"):
        if selected_brand_obj:
            success, error_msg = initialize_conversation(selected_brand_obj["folder"], selected_brand_display)
            if success:
                st.success("✅ Conversa reinicializada com sucesso!")
                st.session_state.conversation_error = None
                st.rerun()
            else:
                st.error(error_msg)
                st.session_state.conversation_error = error_msg
        
    st.markdown("---")
    st.markdown("### Sobre este app")
    st.markdown("""
    Este aplicativo utiliza o modelo Llama 3 da Groq para responder perguntas sobre produtos de impermeabilização.
    
    As respostas são baseadas nas fichas técnicas oficiais dos produtos, fornecidas pelas respectivas fabricantes.
    
    Desenvolvido com Streamlit, LangChain e Groq AI.
    """)

# Interface principal de chat
st.header(f"Chat com Especialista - {selected_brand_display}")

# Adiciona informações de estado para diagnóstico
debug_expander = st.expander("Informações de Diagnóstico")
with debug_expander:
    st.write(f"Marca selecionada: {st.session_state.selected_brand}")
    st.write(f"Conversa inicializada: {'Sim' if st.session_state.conversation else 'Não'}")
    st.write(f"Total de mensagens no histórico: {len(st.session_state.messages)}")
    if not st.session_state.conversation:
        st.warning("A conversa não está inicializada. Selecione uma marca e clique em 'Confirmar Seleção'.")

# Exibe mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Campo de entrada de mensagem
if prompt := st.chat_input("Digite sua pergunta sobre produtos de impermeabilização..."):
    # Adiciona mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Exibe mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Verifica se a conversa foi inicializada
    if not st.session_state.conversation:
        st.error("Por favor, selecione uma marca e clique em 'Confirmar Seleção' antes de fazer perguntas.")
        st.stop()
    
    # Exibe indicador de carregamento durante a geração da resposta
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Pensando...")
        
        try:
            # Gera resposta
            response = st.session_state.conversation({"question": prompt})
            answer = response["answer"]
            
            # Atualiza histórico da conversação
            st.session_state.chat_history = response["chat_history"]
            
            # Exibe resposta
            message_placeholder.markdown(answer)
            
            # Adiciona resposta do assistente ao histórico
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            error_message = str(e)
            error_details = traceback.format_exc()
            logger.error(f"Erro ao gerar resposta: {error_message}\n{error_details}")
            message_placeholder.error(f"Erro ao gerar resposta: {error_message}")
            if "401" in error_message and "Invalid API Key" in error_message:
                st.error("""
                ⚠️ **Erro de autenticação com a API do Groq**
                
                A chave da API parece ser inválida. Por favor, verifique sua chave e reinicie a aplicação.
                """)

# Botão para limpar histórico de chat
if st.button("Limpar Chat"):
    st.session_state.chat_history = []
    st.session_state.messages = []
    st.rerun() 