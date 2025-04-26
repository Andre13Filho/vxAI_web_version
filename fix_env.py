#!/usr/bin/env python
import os
import sys

def main():
    print("Ferramenta para corrigir o arquivo .env")
    print("======================================")
    print("")
    
    # Verifica se o arquivo .env existe
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            content = f.read()
        print(f"Arquivo .env atual:\n{content}\n")
        
        # Pergunta se deseja recriar
        recreate = input("Deseja recriar o arquivo .env? (s/n): ").lower()
        if recreate != "s":
            print("Operação cancelada.")
            return
    
    # Solicita a chave da API
    api_key = input("Digite sua chave da API do Groq: ").strip()
    
    if not api_key:
        print("Nenhuma chave fornecida. Operação cancelada.")
        return
    
    # Cria o arquivo .env com a chave
    with open(".env", "w") as f:
        f.write(f'GROQ_API_KEY={api_key}\n')
    
    print("\nArquivo .env criado com sucesso!")
    
    # Cria diretório .streamlit se não existir
    if not os.path.exists(".streamlit"):
        os.makedirs(".streamlit")
        print("Diretório .streamlit criado.")
    
    # Cria o arquivo secrets.toml
    with open(".streamlit/secrets.toml", "w") as f:
        f.write(f'GROQ_API_KEY = "{api_key}"\n')
    
    print("Arquivo .streamlit/secrets.toml criado com sucesso!")
    
    print("\nAgora tente executar o aplicativo novamente:")
    print("streamlit run app.py")

if __name__ == "__main__":
    main() 