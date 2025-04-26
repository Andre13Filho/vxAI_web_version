import os
import glob
import io
import logging
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import shutil

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Lista das marcas disponíveis
BRANDS = [
    "FT - DENVER",
    "FT - DRYKO",
    "FT - MC BAUCHEMIE",
    "FT - VEDACIT",
    "FT - VIAPOL",
    "FT_SIKA"
]

def pdf_to_documents(pdf_path):
    """
    Converte um arquivo PDF em documentos do LangChain diretamente, sem usar PyPDFLoader
    """
    try:
        # Lê o PDF com pypdf
        logger.info(f"Processando arquivo PDF: {pdf_path}")
        reader = PdfReader(pdf_path)
        
        # Extrai o nome do produto do caminho do arquivo
        product_name = os.path.basename(pdf_path).replace('.pdf', '')
        
        # Lista para armazenar os documentos
        documents = []
        
        # Itera sobre as páginas do PDF
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():  # Ignora páginas vazias
                # Cria um documento LangChain
                doc = Document(
                    page_content=text,
                    metadata={
                        "source": pdf_path,
                        "page": i+1,
                        "product": product_name,
                        "total_pages": len(reader.pages)
                    }
                )
                documents.append(doc)
        
        logger.info(f"Extraídas {len(documents)} páginas com texto de {pdf_path}")
        return documents
    except Exception as e:
        logger.error(f"Erro ao processar {pdf_path}: {e}")
        return []

def process_documents(brand_folder):
    """
    Processa todos os documentos PDF em uma pasta de marca específica
    e cria um banco de dados vetorial para essa marca.
    """
    brand_name = os.path.basename(brand_folder)
    logger.info(f"Processando documentos da marca: {brand_name}")
    
    # Verifica se o diretório da marca existe
    if not os.path.exists(brand_folder):
        logger.error(f"Diretório da marca não encontrado: {brand_folder}")
        # Tenta criar o diretório vazio para facilitar o uso futuro
        try:
            os.makedirs(brand_folder)
            logger.info(f"Diretório criado: {brand_folder}")
        except Exception as e:
            logger.error(f"Erro ao criar diretório {brand_folder}: {e}")
        return 0
    
    # Cria o diretório de saída para o banco de dados vetorial
    output_dir = os.path.join("vectordb", brand_name)
    if os.path.exists(output_dir):
        logger.info(f"Removendo diretório existente: {output_dir}")
        shutil.rmtree(output_dir)
    
    # Carrega todos os PDFs na pasta
    pdf_files = glob.glob(os.path.join(brand_folder, "*.pdf"))
    if not pdf_files:
        logger.warning(f"Nenhum documento PDF encontrado em {brand_folder}")
        return 0
    
    logger.info(f"Encontrados {len(pdf_files)} documentos para processar")
    documents = []
    
    for pdf_file in pdf_files:
        try:
            # Usa nossa função personalizada em vez de PyPDFLoader
            docs = pdf_to_documents(pdf_file)
            
            # Adiciona metadados sobre a marca
            for doc in docs:
                doc.metadata["brand"] = brand_name
                
            documents.extend(docs)
            logger.info(f"Processado: {pdf_file} - {len(docs)} páginas")
        except Exception as e:
            logger.error(f"Erro ao processar {pdf_file}: {e}")
    
    if not documents:
        logger.warning(f"Nenhum documento foi carregado com sucesso para {brand_name}")
        return 0
    
    # Divide os documentos em chunks menores
    logger.info("Dividindo documentos em chunks menores...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    
    try:
        splits = text_splitter.split_documents(documents)
        logger.info(f"Criados {len(splits)} chunks de texto")
        
        # Carrega os embeddings e cria o banco de dados vetorial
        logger.info("Carregando modelo de embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Modelo de embeddings carregado com sucesso")
        
        try:
            # Certifica-se de que o diretório de saída exista
            os.makedirs(os.path.dirname(output_dir), exist_ok=True)
            
            # Cria o banco de dados vetorial e o persiste
            logger.info(f"Criando banco de dados vetorial em {output_dir}...")
            vectordb = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_directory=output_dir
            )
            
            vectordb.persist()
            logger.info(f"Banco de dados vetorial criado com sucesso para {brand_name} em {output_dir}")
            return len(splits)
        except Exception as e:
            logger.error(f"Erro ao criar banco de dados vetorial para {brand_name}: {e}")
            return 0
    except Exception as e:
        logger.error(f"Erro ao dividir documentos para {brand_name}: {e}")
        return 0

def main():
    """
    Função principal que processa todas as marcas
    """
    logger.info("Iniciando processamento de documentos...")
    
    # Cria a pasta vectordb se não existir
    try:
        os.makedirs("vectordb", exist_ok=True)
        logger.info("Diretório vectordb criado ou já existente")
    except Exception as e:
        logger.error(f"Erro ao criar diretório vectordb: {e}")
        return
    
    # Verifica se todas as pastas de marca existem, criando-as se necessário
    for brand in BRANDS:
        if not os.path.exists(brand):
            try:
                logger.info(f"Criando diretório para a marca {brand}")
                os.makedirs(brand, exist_ok=True)
            except Exception as e:
                logger.error(f"Erro ao criar diretório para a marca {brand}: {e}")
    
    total_chunks = 0
    
    for brand in BRANDS:
        try:
            chunks = process_documents(brand)
            if chunks:
                total_chunks += chunks
        except Exception as e:
            logger.error(f"Erro ao processar a marca {brand}: {e}")
    
    logger.info(f"Processamento concluído! Total de chunks criados: {total_chunks}")
    
    # Lista o conteúdo do diretório vectordb após o processamento
    if os.path.exists("vectordb"):
        logger.info(f"Conteúdo do diretório vectordb após processamento: {os.listdir('vectordb')}")

if __name__ == "__main__":
    main() 