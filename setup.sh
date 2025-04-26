#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}====================================${NC}"
echo -e "${YELLOW}=== Configuração do Especialista ===${NC}"
echo -e "${YELLOW}=== em Impermeabilização         ===${NC}"
echo -e "${YELLOW}====================================${NC}"
echo ""

# Verifica se Python está instalado
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo -e "${RED}Erro: Python não está instalado.${NC}"
    exit 1
fi

echo -e "${GREEN}Criando ambiente virtual...${NC}"
$PYTHON -m venv venv

# Ativa o ambiente virtual de acordo com o sistema operacional
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo -e "${GREEN}Instalando dependências...${NC}"
pip install --upgrade pip

# Usar o script de instalação sequencial para evitar conflitos
if [ -f "install_deps.sh" ]; then
    echo -e "${GREEN}Utilizando instalação sequencial para evitar conflitos...${NC}"
    chmod +x install_deps.sh
    ./install_deps.sh
else
    echo -e "${GREEN}Instalando dependências do requirements.txt...${NC}"
    pip install -r requirements.txt
    
    # Verifica se foi bem-sucedido
    if [ $? -ne 0 ]; then
        echo -e "${RED}Erro: Falha na instalação das dependências.${NC}"
        echo -e "${YELLOW}Tente instalar manualmente com: pip install -r requirements.txt${NC}"
        exit 1
    fi
fi

# Verifica se existe arquivo .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}Arquivo .env não encontrado. Vamos criar um.${NC}"
    echo -e "${YELLOW}Por favor, digite sua chave da API do Groq:${NC}"
    read -p "GROQ_API_KEY=" groq_key
    echo "GROQ_API_KEY=$groq_key" > .env
    echo -e "${GREEN}Arquivo .env criado com sucesso!${NC}"
fi

# Verifica se existe pasta .streamlit
if [ ! -d .streamlit ]; then
    mkdir -p .streamlit
    echo "# Configurações e segredos do Streamlit" > .streamlit/config.toml
    echo -e "${GREEN}Diretório .streamlit criado.${NC}"
    
    # Cria arquivo de segredos
    if [ ! -f .streamlit/secrets.toml ]; then
        # Obtém a chave do arquivo .env
        groq_key=$(grep GROQ_API_KEY .env | cut -d '=' -f2)
        echo "# Arquivo de segredos - NÃO compartilhe!" > .streamlit/secrets.toml
        echo "GROQ_API_KEY = \"$groq_key\"" >> .streamlit/secrets.toml
        echo -e "${GREEN}Arquivo de segredos do Streamlit criado.${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Configuração concluída!${NC}"
echo ""
echo -e "${YELLOW}Para processar os documentos, execute:${NC}"
echo -e "  ${GREEN}python ingest.py${NC}"
echo ""
echo -e "${YELLOW}Para iniciar a aplicação, execute:${NC}"
echo -e "  ${GREEN}streamlit run app.py${NC}"
echo "" 