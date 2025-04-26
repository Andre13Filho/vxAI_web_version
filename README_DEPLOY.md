# Instruções para Implantação no Streamlit Cloud

Este documento contém instruções específicas para implantar este aplicativo no Streamlit Cloud.

## Antes de implantar

1. **Importante**: A pasta `vectordb` não é armazenada no Git, então você precisa criar manualmente seus bancos de dados vetoriais no Streamlit Cloud.

2. Certifique-se de que o arquivo `.gitignore` não esteja excluindo arquivos necessários para a implantação.

## Configurando os Segredos no Streamlit Cloud

1. Crie sua conta no [Streamlit Cloud](https://streamlit.io/cloud)
2. Implante o aplicativo a partir do GitHub
3. Na interface do Streamlit Cloud, vá para "Configurações do App" > "Segredos"
4. Adicione seu segredo `GROQ_API_KEY` com sua chave válida da API do Groq

```toml
GROQ_API_KEY = "sua_chave_aqui"
```

## Problemas comuns

Se você encontrar o erro `AttributeError` durante a implantação, tente o seguinte:

1. **Verifique os Logs**: No Streamlit Cloud, clique em "Gerenciar app" no canto inferior direito para acessar os logs completos.

2. **Banco de dados vetorial**: Esta aplicação precisa dos arquivos no diretório `vectordb`.
   Se o erro estiver relacionado a isso, você precisa:

   - Modificar o arquivo `.gitignore` para NÃO ignorar a pasta `vectordb`
   - Fazer commit e push da pasta `vectordb` para o GitHub
   - OU modificar o aplicativo para criar o banco de dados no primeiro uso

3. **Chave da API do Groq**: Verifique se sua chave da API está corretamente configurada nos segredos do Streamlit Cloud.

4. **Dependências**: Verifique se todas as dependências estão instaladas corretamente, em caso de problemas, tente especificar versões compatíveis no arquivo `requirements.txt`.

## Modificação para Incluir o VectorDB no Repositório

Para incluir o banco de dados vetorial no repositório e garantir que ele seja implantado para o Streamlit Cloud, modifique o arquivo `.gitignore` e remova ou comente a linha que menciona `vectordb/`.

Depois execute o script `ingest.py` para criar o banco de dados, e em seguida faça o commit e push de toda a pasta `vectordb` para o repositório.
