@echo off
echo ===============================================
echo === Instalando dependencias (modo seguro)  ===
echo ===============================================
echo.

REM Atualiza o pip para a versão mais recente
pip install --upgrade pip

echo.
echo 1/8: Instalando dependencias basicas...
pip install python-dotenv pydantic streamlit

echo.
echo 2/8: Instalando pypdf...
pip install pypdf

echo.
echo 3/8: Instalando langchain-core...
pip install langchain-core

echo.
echo 4/8: Instalando sentence-transformers...
pip install sentence-transformers

echo.
echo 5/8: Instalando chromadb...
pip install chromadb

echo.
echo 6/8: Instalando langchain...
pip install langchain

echo.
echo 7/8: Instalando langchain-community...
pip install langchain-community

echo.
echo 8/8: Instalando langchain-groq e text-splitters...
pip install langchain-groq langchain-text-splitters

echo.
echo Instalacao concluida!
echo. 