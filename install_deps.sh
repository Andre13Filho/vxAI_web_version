#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===============================================${NC}"
echo -e "${YELLOW}=== Instalando dependências (modo seguro)  ===${NC}"
echo -e "${YELLOW}===============================================${NC}"
echo ""

# Atualiza o pip para a versão mais recente
pip install --upgrade pip

echo ""
echo -e "${GREEN}1/8: Instalando dependências básicas...${NC}"
pip install python-dotenv pydantic streamlit

echo ""
echo -e "${GREEN}2/8: Instalando pypdf...${NC}"
pip install pypdf

echo ""
echo -e "${GREEN}3/8: Instalando langchain-core...${NC}"
pip install langchain-core

echo ""
echo -e "${GREEN}4/8: Instalando sentence-transformers...${NC}"
pip install sentence-transformers

echo ""
echo -e "${GREEN}5/8: Instalando chromadb...${NC}"
pip install chromadb

echo ""
echo -e "${GREEN}6/8: Instalando langchain...${NC}"
pip install langchain

echo ""
echo -e "${GREEN}7/8: Instalando langchain-community...${NC}"
pip install langchain-community

echo ""
echo -e "${GREEN}8/8: Instalando langchain-groq e text-splitters...${NC}"
pip install langchain-groq langchain-text-splitters

echo ""
echo -e "${GREEN}Instalação concluída!${NC}"
echo "" 