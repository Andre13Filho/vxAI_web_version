@echo off
echo ====================================
echo === Configuracao do Especialista ===
echo === em Impermeabilizacao         ===
echo ====================================
echo.

:: Verifica se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Erro: Python nao esta instalado.
    exit /b 1
)

echo Criando ambiente virtual...
python -m venv venv

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias...
pip install --upgrade pip

:: Usar o script de instalação sequencial para evitar conflitos
if exist install_deps.bat (
    echo Utilizando instalacao sequencial para evitar conflitos...
    call install_deps.bat
) else (
    echo Instalando dependencias do requirements.txt...
    pip install -r requirements.txt
    
    if %errorlevel% neq 0 (
        echo Erro: Falha na instalacao das dependencias.
        echo Tente instalar manualmente com: pip install -r requirements.txt
        exit /b 1
    )
)

:: Verifica se existe arquivo .env
if not exist .env (
    echo Arquivo .env nao encontrado. Vamos criar um.
    echo Por favor, digite sua chave da API do Groq:
    set /p groq_key="GROQ_API_KEY="
    echo GROQ_API_KEY=%groq_key%> .env
    echo Arquivo .env criado com sucesso!
)

:: Verifica se existe pasta .streamlit
if not exist .streamlit (
    mkdir .streamlit
    echo # Configuracoes e segredos do Streamlit> .streamlit\config.toml
    echo Diretorio .streamlit criado.
    
    :: Cria arquivo de segredos
    if not exist .streamlit\secrets.toml (
        :: Obtém a chave do arquivo .env (simplificado para Windows)
        for /f "tokens=2 delims==" %%a in ('type .env ^| findstr GROQ_API_KEY') do set groq_key=%%a
        echo # Arquivo de segredos - NAO compartilhe!> .streamlit\secrets.toml
        echo GROQ_API_KEY = "%groq_key%">> .streamlit\secrets.toml
        echo Arquivo de segredos do Streamlit criado.
    )
)

echo.
echo Configuracao concluida!
echo.
echo Para processar os documentos, execute:
echo   python ingest.py
echo.
echo Para iniciar a aplicacao, execute:
echo   streamlit run app.py 