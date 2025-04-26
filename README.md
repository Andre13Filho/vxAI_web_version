# Especialista em Impermeabilização - IA

Um assistente virtual baseado em IA especializado em produtos de impermeabilização de diversas marcas.

## 📝 Descrição

Este projeto implementa um chatbot especializado em produtos de impermeabilização, utilizando fichas técnicas oficiais dos fabricantes como base de conhecimento. A aplicação permite que os usuários selecionem uma marca específica e façam perguntas sobre seus produtos.

O sistema utiliza o modelo Llama 3 da Groq, combinado com técnicas de RAG (Retrieval Augmented Generation) para fornecer respostas precisas e baseadas na documentação oficial dos produtos.

## 🏢 Marcas Suportadas

- Denver
- Dryko
- MC Bauchemie
- Vedacit
- Viapol
- Sika

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Interface de usuário
- **LangChain**: Framework para construção de aplicações de IA
- **Groq**: Provedor do modelo de linguagem Llama 3
- **ChromaDB**: Banco de dados vetorial para armazenamento e recuperação semântica
- **HuggingFace Embeddings**: Transformação de texto em vetores
- **PyPDF**: Extração de texto de documentos PDF

## 🚀 Como Executar

### Pré-requisitos

- Python 3.9 ou superior
- Chave de API da Groq (obtenha em https://console.groq.com/)

### Instalação Rápida

Para facilitar a configuração, use um dos scripts de configuração automática:

**No Linux/Mac**:

```bash
chmod +x setup.sh
./setup.sh
```

**No Windows**:

```
setup.bat
```

Estes scripts irão:

1. Criar um ambiente virtual Python
2. Instalar todas as dependências
3. Solicitar e configurar sua chave da API do Groq
4. Configurar os arquivos necessários

### Instalação Manual

Se preferir configurar manualmente:

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/especialista-impermeabilizacao.git
   cd especialista-impermeabilizacao
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instale as dependências:

   **Modo recomendado (instalação sequencial para evitar conflitos)**:

   No Windows:

   ```bash
   install_deps.bat
   ```

   No Linux/Mac:

   ```bash
   chmod +x install_deps.sh
   ./install_deps.sh
   ```

   **Modo alternativo**:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure a chave da API Groq (escolha uma das opções):

   **Opção 1**: Crie um arquivo `.env` na raiz do projeto:

   ```
   GROQ_API_KEY=sua_chave_aqui
   ```

   **Opção 2**: Crie um arquivo `.streamlit/secrets.toml`:

   ```toml
   GROQ_API_KEY = "sua_chave_aqui"
   ```

### Processamento dos Documentos

Antes de usar o sistema, você precisa processar os documentos PDF para criar os bancos de dados vetoriais:

```bash
python ingest.py
```

Este processo pode demorar alguns minutos, dependendo da quantidade de documentos.

### Executando a Aplicação

```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`.

## 🌐 Implantação no Streamlit Cloud

Para implantar a aplicação no Streamlit Cloud:

1. Faça o push do código para o GitHub (certifique-se de que `.env` e `.streamlit/secrets.toml` estão no `.gitignore`)

2. Crie uma nova aplicação no Streamlit Cloud apontando para o seu repositório

3. Configure a chave da API do Groq no Streamlit Cloud:

   - Acesse o painel de controle do seu aplicativo
   - Vá para "Settings" > "Secrets"
   - Adicione a chave `GROQ_API_KEY` com seu valor

4. (Opcional) Durante o primeiro acesso, clique no botão "Processar Documentos" para gerar os bancos de dados vetoriais

**Importante**: O diretório `vectordb` não deve ser enviado ao GitHub. Ele será gerado automaticamente na primeira execução da aplicação. Você pode usar o botão "Processar Documentos" na interface para criar os bancos de dados vetoriais.

## 📜 Solução de Problemas

### Erro na instalação das dependências

Se você encontrar erros ao instalar as dependências relacionadas a versões incompatíveis, use os scripts de instalação sequencial fornecidos:

```bash
# Windows
install_deps.bat

# Linux/Mac
chmod +x install_deps.sh
./install_deps.sh
```

Estes scripts instalam as dependências em uma ordem específica para evitar conflitos.

Como alternativa, você pode instalar manualmente as principais dependências em ordem:

```bash
pip install --upgrade pip
pip install langchain-core
pip install -r requirements.txt
```

### Erro ao processar documentos PDF

Se ocorrerem erros durante o processamento dos PDFs, verifique se os documentos estão corrompidos ou protegidos por senha. O script `ingest.py` vai ignorar documentos que não puderem ser processados, mas informará no console quais arquivos tiveram problemas.

### Erro com o PyPDFLoader

Se você encontrar erros relacionados ao `PyPDFLoader` ou a definições de linguagem como "COBOL", o script foi atualizado para usar uma abordagem direta com `pypdf` que evita esse problema.

## 📂 Estrutura do Projeto

```
especialista-impermeabilizacao/
├── app.py                  # Aplicação Streamlit
├── ingest.py               # Script para processamento dos documentos
├── models.py               # Configuração e gerenciamento dos modelos de IA
├── setup.sh                # Script de configuração para Linux/Mac
├── setup.bat               # Script de configuração para Windows
├── install_deps.sh         # Script de instalação sequencial para Linux/Mac
├── install_deps.bat        # Script de instalação sequencial para Windows
├── requirements.txt        # Dependências do projeto
├── .env                    # Arquivo de variáveis de ambiente (local)
├── .streamlit/             # Configurações do Streamlit
│   └── secrets.toml        # Arquivo de segredos (local)
├── .gitignore              # Configuração do Git
├── README.md               # Documentação
├── FT - DENVER/            # Documentos da Denver
├── FT - DRYKO/             # Documentos da Dryko
├── FT - MC BAUCHEMIE/      # Documentos da MC Bauchemie
├── FT - VEDACIT/           # Documentos da Vedacit
├── FT - VIAPOL/            # Documentos da Viapol
└── FT_SIKA/                # Documentos da Sika
```

## 🔒 Segurança

A chave da API do Groq é sensível e nunca deve ser compartilhada ou enviada ao GitHub. Este projeto utiliza as seguintes práticas para proteger sua chave:

1. Armazenamento local em arquivos que não são enviados ao GitHub (`.env` e `.streamlit/secrets.toml`)
2. Configuração de segredos no Streamlit Cloud para implantação segura

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

---

Desenvolvido com 💧 e ❤️
