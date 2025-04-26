import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

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
        raise ValueError("A chave da API do Groq não foi encontrada nas variáveis de ambiente")
    
    # Remove espaços em branco e caracteres invisíveis
    api_key = api_key.strip()
    
    # Verifica se a chave está no formato esperado
    if not api_key.startswith("gsk_"):
        print("Aviso: A chave da API do Groq não começa com 'gsk_', verifique se ela está correta")
    
    return api_key

def get_vectordb(brand):
    """
    Carrega o banco de dados vetorial para uma marca específica.
    """
    # Normaliza o nome da marca para corresponder à estrutura de pastas
    brand_folder = brand
    if not brand.startswith("FT"):
        brand_folder = f"FT - {brand}"
    
    # Caminho para o banco de dados vetorial
    persist_directory = os.path.join("vectordb", brand_folder)
    
    # Verifica se o banco de dados existe
    if not os.path.exists(persist_directory):
        raise ValueError(f"Banco de dados vetorial não encontrado para a marca {brand}")
    
    # Carrega os embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Carrega o banco de dados vetorial
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    return vectordb

def get_llm():
    """
    Configura e retorna o modelo LLM da Groq.
    """
    # Obtém a chave da API com tratamento adequado
    api_key = get_api_key()
    
    # Cria o cliente com a chave limpa
    llm = ChatGroq(
        api_key=api_key,
        model_name="llama3-70b-8192",
        temperature=0.2,
        max_tokens=4096,
    )
    
    return llm

def get_conversation_chain(brand):
    """
    Configura e retorna a cadeia de conversação com o modelo e o banco de dados vetorial.
    """
    llm = get_llm()
    vectordb = get_vectordb(brand)
    
    # Configura a memória da conversação
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Configura a cadeia de conversação
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectordb.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        verbose=True
    )
    
    return conversation_chain

def get_available_brands():
    """
    Retorna a lista de marcas disponíveis com bases de dados vetoriais.
    """
    brands = []
    
    # Verifica se o diretório vectordb existe
    if os.path.exists("vectordb"):
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
    
    return brands 