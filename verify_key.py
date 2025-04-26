import os
import sys
from dotenv import load_dotenv
import requests
import json
import streamlit as st

def check_groq_api_key(api_key):
    """
    Verifica se a chave da API do Groq é válida fazendo uma chamada de teste.
    Retorna (True, None) se for válida, (False, erro) se for inválida.
    """
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return True, None
        else:
            error_message = f"Status: {response.status_code} - {response.text}"
            return False, error_message
    except Exception as e:
        return False, str(e)

def main():
    print("Verificador de Chave da API do Groq")
    print("==================================")
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Verifica a chave da API do ambiente
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("\nNenhuma chave encontrada no ambiente (.env).")
        print("Vamos testar uma chave fornecida manualmente.")
        api_key = input("\nDigite sua chave da API do Groq: ")
    else:
        print(f"\nChave encontrada no arquivo .env: {api_key[:5]}...{api_key[-4:]}")
    
    # Verifica se a chave está em branco
    if not api_key or api_key.strip() == "":
        print("\nERRO: Chave da API não foi fornecida.")
        return
    
    # Verificar se há caracteres extras ou espaços em branco
    cleaned_key = api_key.strip()
    if cleaned_key != api_key:
        print("\nAVISO: A chave contém espaços extras no início ou no fim.")
        print(f"Chave original: '{api_key}'")
        print(f"Chave limpa: '{cleaned_key}'")
        api_key = cleaned_key
    
    # Verifica comprimento típico das chaves do Groq (geralmente começam com 'gsk_')
    if not api_key.startswith("gsk_"):
        print("\nAVISO: A chave não começa com 'gsk_', o que é o padrão para chaves do Groq.")
    
    # Faz o teste real da chave
    print("\nTestando a chave da API...")
    is_valid, error = check_groq_api_key(api_key)
    
    if is_valid:
        print("\n✅ SUCESSO: A chave da API do Groq é válida!")
        print("\nDicas para solucionar o erro:")
        print("1. Verifique se o arquivo .env está no diretório correto")
        print("2. Reinicie o aplicativo após atualizar a chave")
        print("3. Verifique se há caracteres invisíveis ou espaços no arquivo .env")
    else:
        print(f"\n❌ ERRO: A chave da API do Groq é inválida!")
        print(f"Detalhes do erro: {error}")
        print("\nPossíveis causas:")
        print("1. A chave está incorreta ou expirou")
        print("2. Há um problema de rede ou firewall")
        print("3. A chave tem caracteres invisíveis ou formatação incorreta")
        
    # Sugestões para resolver o problema
    print("\nPara corrigir o problema:")
    print("1. Obtenha uma nova chave em https://console.groq.com/keys")
    print("2. Crie um novo arquivo .env com o conteúdo exato:")
    print(f'   GROQ_API_KEY="{api_key}"')
    print("3. Alternativamente, adicione-a ao Streamlit Secret Management")

if __name__ == "__main__":
    main() 