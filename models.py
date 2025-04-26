import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

def get_api_key():
    """
    Obtém a chave da API do Groq e faz uma limpeza básica para evitar problemas comuns.
    """
    # Obtém a chave da API do Groq do ambiente
    api_key = os.environ.get("GROQ_API_KEY")
    
    # Verifica se a chave está vazia
    if not api_key:
        # Tenta obter do secrets do Streamlit
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
                logger.info("API key obtained from Streamlit secrets")
        except Exception as e:
            logger.error(f"Error accessing Streamlit secrets: {e}")
    
    # Ainda está vazia?
    if not api_key:
        raise ValueError("A chave da API do Groq não foi encontrada nas variáveis de ambiente ou nos secrets do Streamlit")
    
    # Remove espaços em branco e caracteres invisíveis
    api_key = api_key.strip()
    
    # Verifica se a chave está no formato esperado
    if not api_key.startswith("gsk_"):
        logger.warning("A chave da API do Groq não começa com 'gsk_', verifique se ela está correta")
    
    return api_key

def get_vectordb(brand):
    """
    Carrega o banco de dados vetorial para uma marca específica.
    """
    try:
        # Normaliza o nome da marca para corresponder à estrutura de pastas
        brand_folder = brand
        if not brand.startswith("FT"):
            brand_folder = f"FT - {brand}"
        
        # Caminho para o banco de dados vetorial
        persist_directory = os.path.join("vectordb", brand_folder)
        
        # Verifica se o banco de dados existe
        if not os.path.exists(persist_directory):
            logger.error(f"Diretório não encontrado: {persist_directory}")
            raise ValueError(f"Banco de dados vetorial não encontrado para a marca {brand}")
        
        # Lista o conteúdo do diretório para debug
        logger.info(f"Conteúdo do diretório {persist_directory}: {os.listdir(persist_directory)}")
        
        # Carrega os embeddings
        logger.info("Iniciando carregamento dos embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Embeddings carregados com sucesso")
        
        # Carrega o banco de dados vetorial
        logger.info(f"Carregando banco de dados vetorial de {persist_directory}...")
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        logger.info("Banco de dados vetorial carregado com sucesso")
        
        return vectordb
    except Exception as e:
        logger.error(f"Erro ao carregar o banco de dados vetorial: {str(e)}")
        raise

def get_llm():
    """
    Configura e retorna o modelo LLM da Groq.
    """
    try:
        # Obtém a chave da API com tratamento adequado
        api_key = get_api_key()
        
        # Cria o cliente com a chave limpa
        logger.info("Inicializando modelo LLM da Groq...")
        llm = ChatGroq(
            api_key=api_key,
            model_name="llama3-70b-8192",
            temperature=0.2,
            max_tokens=4096,
        )
        logger.info("Modelo LLM inicializado com sucesso")
        
        return llm
    except Exception as e:
        logger.error(f"Erro ao inicializar o modelo LLM: {str(e)}")
        raise

def get_conversation_chain(brand):
    """
    Configura e retorna a cadeia de conversação com o modelo e o banco de dados vetorial.
    """
    try:
        llm = get_llm()
        vectordb = get_vectordb(brand)
        
        # Configura a memória da conversação
        logger.info("Configurando memória da conversação...")
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Configura a cadeia de conversação
        logger.info("Criando cadeia de conversação...")
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectordb.as_retriever(search_kwargs={"k": 5}),
            memory=memory,
            verbose=True
        )
        logger.info("Cadeia de conversação criada com sucesso")
        
        return conversation_chain
    except Exception as e:
        logger.error(f"Erro ao criar a cadeia de conversação: {str(e)}")
        raise

def get_available_brands():
    """
    Retorna a lista de marcas disponíveis com bases de dados vetoriais.
    """
    brands = []
    
    try:
        # Verifica se o diretório vectordb existe
        if os.path.exists("vectordb"):
            logger.info(f"Conteúdo do diretório vectordb: {os.listdir('vectordb')}")
            
            # Lista todas as pastas dentro do diretório vectordb
            for brand_folder in os.listdir("vectordb"):
                brand_path = os.path.join("vectordb", brand_folder)
                if os.path.isdir(brand_path):
                    # Limpa o prefixo "FT - " ou "FT_" para exibição
                    display_name = brand_folder
                    if brand_folder.startswith("FT - "):
                        display_name = brand_folder[5:]
                    elif brand_folder.startswith("FT_"):
                        display_name = brand_folder[3:]
                    
                    brands.append({"folder": brand_folder, "display": display_name})
        else:
            logger.warning("Diretório vectordb não encontrado")
    except Exception as e:
        logger.error(f"Erro ao listar marcas disponíveis: {str(e)}")
    
    return brands 