import os
import glob
import io
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import shutil

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
        
        return documents
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {e}")
        return []

def process_documents(brand_folder):
    """
    Processa todos os documentos PDF em uma pasta de marca específica
    e cria um banco de dados vetorial para essa marca.
    """
    brand_name = os.path.basename(brand_folder)
    print(f"Processando documentos da marca: {brand_name}")
    
    # Cria o diretório de saída para o banco de dados vetorial
    output_dir = os.path.join("vectordb", brand_name)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    # Carrega todos os PDFs na pasta
    pdf_files = glob.glob(os.path.join(brand_folder, "*.pdf"))
    if not pdf_files:
        print(f"Nenhum documento PDF encontrado em {brand_folder}")
        return
    
    print(f"Encontrados {len(pdf_files)} documentos para processar")
    documents = []
    
    for pdf_file in pdf_files:
        try:
            # Usa nossa função personalizada em vez de PyPDFLoader
            docs = pdf_to_documents(pdf_file)
            
            # Adiciona metadados sobre a marca
            for doc in docs:
                doc.metadata["brand"] = brand_name
                
            documents.extend(docs)
            print(f"Processado: {pdf_file} - {len(docs)} páginas")
        except Exception as e:
            print(f"Erro ao processar {pdf_file}: {e}")
    
    if not documents:
        print(f"Nenhum documento foi carregado com sucesso para {brand_name}")
        return 0
    
    # Divide os documentos em chunks menores
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    
    splits = text_splitter.split_documents(documents)
    print(f"Criados {len(splits)} chunks de texto")
    
    # Carrega os embeddings e cria o banco de dados vetorial
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    try:
        # Cria o banco de dados vetorial e o persiste
        vectordb = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=output_dir
        )
        
        vectordb.persist()
        print(f"Banco de dados vetorial criado para {brand_name} em {output_dir}")
        return len(splits)
    except Exception as e:
        print(f"Erro ao criar banco de dados vetorial para {brand_name}: {e}")
        return 0

def main():
    """
    Função principal que processa todas as marcas
    """
    print("Iniciando processamento de documentos...")
    
    # Cria a pasta vectordb se não existir
    os.makedirs("vectordb", exist_ok=True)
    
    total_chunks = 0
    
    for brand in BRANDS:
        chunks = process_documents(brand)
        if chunks:
            total_chunks += chunks
    
    print(f"Processamento concluído! Total de chunks criados: {total_chunks}")

if __name__ == "__main__":
    main() 