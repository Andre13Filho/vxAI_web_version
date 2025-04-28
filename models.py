import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from typing import Any, List, Dict, Optional
from pydantic import Field
from langchain.schema.retriever import BaseRetriever
from langchain_core.retrievers import BaseRetriever as CoreBaseRetriever
from langchain_core.documents import Document
import logging
import sys
import importlib.util
import traceback

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

def check_sqlite_version():
    """
    Verifica a versão do SQLite e retorna se está acima do mínimo necessário.
    """
    try:
        import sqlite3
        sqlite_version = sqlite3.sqlite_version_info
        min_version = (3, 35, 0)
        
        logger.info(f"Versão do SQLite: {sqlite_version}")
        
        if sqlite_version < min_version:
            logger.warning(f"SQLite versão {sqlite_version} é mais antiga que a versão mínima recomendada {min_version}")
            return False
        return True
    except Exception as e:
        logger.error(f"Erro ao verificar versão do SQLite: {e}")
        return False

def is_pysqlite_available():
    """
    Verifica se pysqlite está disponível como alternativa.
    """
    try:
        spec = importlib.util.find_spec('pysqlite3')
        return spec is not None
    except ImportError:
        return False

def setup_pysqlite():
    """
    Configura pysqlite3 como solução alternativa para versões antigas do SQLite.
    """
    try:
        # Verifica se pysqlite3 está disponível
        if not is_pysqlite_available():
            logger.warning("pysqlite3 não está disponível. Tentando usá-lo mesmo assim.")
        
        # Realizando a substituição do driver sqlite
        __import__('pysqlite3')
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
        
        # Verificando se a substituição funcionou
        import sqlite3
        logger.info(f"SQLite (após substituição) versão: {sqlite3.sqlite_version}")
        return True
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Falha ao configurar pysqlite3: {e}\n{error_details}")
        return False

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
        
        # Verifica versão do SQLite
        if not check_sqlite_version():
            logger.warning("SQLite está em uma versão antiga. Tentando usar pysqlite3 como alternativa.")
            setup_success = setup_pysqlite()
            if not setup_success:
                logger.warning("Não foi possível configurar pysqlite3. Tentando continuar com SQLite nativo.")
        
        # Carrega os embeddings
        logger.info("Iniciando carregamento dos embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Embeddings carregados com sucesso")
        
        # Carrega o banco de dados vetorial com configurações compatíveis
        logger.info(f"Carregando banco de dados vetorial de {persist_directory}...")
        
        # Tentativa de carregamento sem configurações extras primeiro
        try:
            logger.info("Tentando carregar ChromaDB sem configurações especiais...")
            vectordb = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
            logger.info("Banco de dados vetorial carregado com sucesso (modo padrão)")
            return vectordb
        except Exception as first_error:
            logger.warning(f"Erro no primeiro método de carregamento: {str(first_error)}")
            logger.info("Tentando método alternativo de carregamento...")
            
            try:
                # Se falhar, tenta importar usando o módulo chromadb diretamente
                # para configurações mais específicas
                from chromadb.config import Settings
                import chromadb
                
                # Inicializa o cliente com configurações compatíveis
                logger.info("Inicializando cliente ChromaDB diretamente...")
                chroma_client = chromadb.PersistentClient(
                    path=persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=True
                    )
                )
                
                # Get the default collection
                logger.info("Obtendo coleção padrão...")
                collection_name = "langchain"  # Nome padrão usado pelo LangChain
                try:
                    collection = chroma_client.get_collection(collection_name)
                    logger.info(f"Coleção '{collection_name}' encontrada")
                except Exception:
                    logger.warning(f"Coleção '{collection_name}' não encontrada, listando coleções disponíveis...")
                    collections = chroma_client.list_collections()
                    if collections:
                        collection_name = collections[0].name
                        collection = chroma_client.get_collection(collection_name)
                        logger.info(f"Usando coleção alternativa: {collection_name}")
                    else:
                        raise ValueError("Nenhuma coleção encontrada no banco de dados vetorial")
                
                # Criar uma instância do Chroma usando o cliente e coleção
                logger.info("Criando instância Chroma a partir do cliente personalizado...")
                vectordb = Chroma(
                    client=chroma_client,
                    collection_name=collection_name,
                    embedding_function=embeddings
                )
                logger.info("Banco de dados vetorial carregado com sucesso (modo alternativo)")
                return vectordb
            except Exception as second_error:
                error_details = traceback.format_exc()
                logger.error(f"Erro no segundo método de carregamento: {str(second_error)}\n{error_details}")
                
                # Se ambos falharem, tenta um terceiro método mais básico
                try:
                    logger.info("Tentando método de último recurso...")
                    # Use um diretório temporário novo para reconstruir o banco
                    import shutil
                    import tempfile
                    
                    # Cria um diretório temporário
                    temp_dir = tempfile.mkdtemp()
                    logger.info(f"Diretório temporário criado: {temp_dir}")
                    
                    # Copia os arquivos do banco de dados para o diretório temporário
                    for item in os.listdir(persist_directory):
                        src = os.path.join(persist_directory, item)
                        dst = os.path.join(temp_dir, item)
                        if os.path.isdir(src):
                            shutil.copytree(src, dst)
                        else:
                            shutil.copy2(src, dst)
                    
                    # Tenta carregar a partir do diretório temporário
                    vectordb = Chroma(
                        persist_directory=temp_dir,
                        embedding_function=embeddings
                    )
                    logger.info("Banco de dados vetorial carregado com sucesso (modo de recuperação)")
                    return vectordb
                except Exception as third_error:
                    logger.error(f"Todos os métodos de carregamento falharam. Último erro: {str(third_error)}")
                    # Verificando se o erro está relacionado ao SQLite
                    if "sqlite3" in str(third_error).lower():
                        raise ValueError(f"Erro com SQLite: {third_error}. É necessário um SQLite mais recente.")
                    raise ValueError(f"Não foi possível carregar o banco de dados vetorial após várias tentativas: {str(third_error)}")
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
            temperature=0.1,  # Reduzindo a temperatura para respostas mais precisas
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
        
        # Extrai o nome da marca sem prefixos para mostrar no prompt
        brand_display = brand.replace("FT - ", "").replace("FT_", "")
        logger.info(f"Nome da marca para exibição: {brand_display}")
        
        # Configura a memória da conversação com chave de saída específica
        logger.info("Configurando memória da conversação...")
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"  # Especifica qual chave será armazenada na memória
        )
        
        # Abordagem alternativa - usar diretamente o retriever padrão
        logger.info("Usando retriever padrão com componente de busca especializada...")
        
        # Carrega a lista de produtos conhecidos
        product_mapping = {
            # Produtos SIKA - mapeamento de nomes alternativos para nomes oficiais
            "igolasfal": "IgolEcoasfalto",
            "igol asfal": "IgolEcoasfalto",
            "igol eco": "IgolEcoasfalto",
            "ecoasfal": "IgolEcoasfalto",
            "igolecoasfal": "IgolEcoasfalto",
            "igol asfalto eco": "IgolEcoasfalto",
            "igol s": "Igol S",
            "igol 2": "Igol®-2",
            "igolflex": "Igolflex",  # Base para Igolflex Fachada ou Preto
            "fachada": "Igolflex Fachada",
            "preto": "Igolflex Preto",
            "impermur": "Impermur_Sikagard",
            "sikagard": "Impermur_Sikagard",
            "impersika": "Impersika",
            "pk premium": "PK Premium Superflex",
            "pk superflex": "PK Premium Superflex",
            "premium superflex": "PK Premium Superflex",
            "sika 1": "Sika 1",
            "sika1": "Sika 1",
            "sika 2": "Sika 2",
            "sika2": "Sika 2",
            "sika 3": "Sika 3 Plus",
            "sika3": "Sika 3 Plus",
            "sika plus": "Sika 3 Plus",
            "chapisco": "Sika Chapisco Plus",
            "concreto forte": "Sika Concreto Forte",
            "eco primer": "Sika Eco Primer",
            "intraplast": "Sika Intraplast N",
            "monotop": "Sika Monotop 123 Rodapé",
            "rodapé": "Sika Monotop 123 Rodapé",
            "multiseal": "Sika Multiseal Primer",
            "separol": "Sika Separol Top",
            "silicone": "Sika Silicone",
            "sikabond 134": "SikaBond 134",
            "sikabond at": "SikaBond AT Universal",
            "sikacryl": "SikaCryl 203",
            "sikadur 31": "Sikadur 31",
            "sikadur 32 gel": "Sikadur 32 Gel",
            "sikadur 32": "Sikadur 32",
            "sikadur 512": "Sikadur 512",
            "sikadur epoxi": "Sikadur Epoxi",
            "sikafill rápido power": "Sikafill Rápido Power",
            "sikafill rápido": "Sikafill Rápido",
            "sikaflex 1a": "Sikaflex 1A Plus",
            "sikaflex construction": "Sikaflex Construction",
            "sikaflex universal": "Sikaflex Universal",
            "sikagrout 250": "Sikagrout 250",
            "sikagrout tix": "Sikagrout Tix",
            "sikanol": "Sikanol Alvenaria",
            "alvenaria": "Sikanol Alvenaria",
            "sikashield alu": "SikaShield P34 ALU Tipo II 4 mm",
            "sikashield 3mm": "SikaShield P34 PE Tipo II 3 mm",
            "sikashield 4mm": "SikaShield P34 PE Tipo II 4 mm",
            "sikatop 100": "Sikatop 100",
            "sikatop 107": "Sikatop 107",
            "sikatop flex": "Sikatop Flex",
        }
        
        # Função de busca personalizada
        def custom_search(query, vectordb=vectordb, product_mapping=product_mapping):
            # Identifica o produto na consulta
            question_lower = query.lower()
            identified_product = None
            
            # Verifica se algum produto específico é mencionado na pergunta
            for keyword, product_name in product_mapping.items():
                if keyword.lower() in question_lower:
                    identified_product = product_name
                    logger.info(f"Produto identificado na pergunta: {product_name}")
                    break
            
            # Se identificou um produto, tenta filtrar os resultados
            if identified_product:
                logger.info(f"Buscando informações específicas para o produto: {identified_product}")
                
                # Recupera mais documentos e filtra manualmente para maior precisão
                try:
                    # Primeiro tenta buscar com filtro exato
                    filter_dict = {"product": identified_product}
                    docs_with_filter = vectordb.similarity_search(
                        query, k=3, filter=filter_dict
                    )
                    
                    if docs_with_filter:
                        logger.info(f"Encontrados {len(docs_with_filter)} documentos com filtro exato")
                        return docs_with_filter
                    
                    # Se não encontrar com filtro exato, busca sem filtro e filtra manualmente
                    all_docs = vectordb.similarity_search(query, k=10)
                    
                    # Filtra manualmente por produto específico
                    filtered_docs = []
                    for doc in all_docs:
                        product_in_metadata = doc.metadata.get("product", "").lower()
                        if identified_product.lower() in product_in_metadata:
                            filtered_docs.append(doc)
                    
                    if filtered_docs:
                        logger.info(f"Encontrados {len(filtered_docs)} documentos após filtragem manual")
                        return filtered_docs
                
                except Exception as e:
                    logger.warning(f"Erro ao filtrar por produto: {str(e)}")
            
            # Fallback - busca padrão
            docs = vectordb.similarity_search(query, k=3)
            logger.info(f"Usando resultados sem filtro: {len(docs)} documentos")
            return docs
        
        # Configuração do retriever padrão usando uma função de search personalizada
        retriever = vectordb.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3},
            search_function=custom_search  # Passamos nossa função de busca personalizada
        )
        
        # Mensagem do sistema para controlar o comportamento do modelo
        system_template = """Você é um especialista em produtos de impermeabilização da marca """ + brand_display + """.
        
Sua função é responder perguntas sobre os produtos com base EXCLUSIVAMENTE nas informações das fichas técnicas oficiais.

REGRAS IMPORTANTES:
1. Use APENAS as informações fornecidas na ficha técnica do produto específico mencionado na pergunta.
2. Se a informação solicitada não estiver na ficha técnica do produto, informe claramente que não possui essa informação.
3. NÃO INVENTE ou DEDUZA informações que não estejam explicitamente na ficha técnica.
4. Foque apenas no produto específico mencionado na pergunta do usuário.
5. Não compare produtos a menos que seja explicitamente solicitado, e somente se tiver informações de ambos.
6. Seu conhecimento vem exclusivamente da ficha técnica, não de outras fontes ou experiência prévia.
7. Se o usuário não mencionar um produto específico, pergunte qual produto ele deseja saber informações antes de fornecer detalhes.
8. Sempre responda as respostas em português.
9. ATENÇÃO ESPECIAL para informações técnicas como: consumo, rendimento, temperatura de aplicação, tempo de secagem, validade, embalagens disponíveis, etc. Verifique com muito cuidado estas informações nos documentos fornecidos.
10. Quando responder sobre CONSUMO do produto, cite exatamente como está na ficha técnica, incluindo a unidade de medida.
11. A ficha técnica geralmente inclui seções como "Dados do Produto" ou "Dados Técnicos" onde informações como consumo são especificadas. Examine cuidadosamente estas seções.

Contexto técnico recuperado: 
{context}

Histórico da conversa:
{chat_history}

Responda a pergunta do usuário com base APENAS no contexto técnico fornecido acima e APENAS sobre o produto específico perguntado.
"""
        
        # Mensagem do usuário
        human_template = "{question}"
        
        # Constrói o prompt completo
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        
        # Junta as mensagens para formar o prompt completo
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        
        # Configura a cadeia de conversação com o prompt personalizado
        logger.info("Criando cadeia de conversação com prompt personalizado...")
        
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            verbose=True,
            combine_docs_chain_kwargs={"prompt": chat_prompt},
            chain_type="stuff",  # Usando o tipo "stuff" para melhor contexto
            return_source_documents=True,  # Retorna os documentos fonte para debugging
            output_key="answer"  # Define a chave de saída para a resposta
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