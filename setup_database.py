#!/usr/bin/env python3
"""
Script interativo para configurar a conexão com o banco de dados SQL Server
"""

import os
import sys
from config import DB_CONFIG

def get_user_input(prompt, default_value=""):
    """Obtém entrada do usuário com valor padrão"""
    if default_value:
        user_input = input(f"{prompt} [{default_value}]: ").strip()
        return user_input if user_input else default_value
    else:
        return input(f"{prompt}: ").strip()

def test_connection(server, database, username, password):
    """Testa a conexão com o banco de dados"""
    try:
        import pyodbc
        
        connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        
        with pyodbc.connect(connection_string) as conn:
            print("✅ Conexão estabelecida com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def update_config_file(server, database, username, password):
    """Atualiza o arquivo config.py com as novas configurações"""
    config_content = f'''# Configurações do Banco de Dados SQL Server
DB_CONFIG = {{
    'server': '{server}',        # Endereço do servidor SQL Server
    'database': '{database}',    # Nome do banco de dados
    'username': '{username}',    # Usuário SQL Server
    'password': '{password}',    # Senha SQL Server (ajuste conforme necessário)
    'driver': 'ODBC Driver 17 for SQL Server'  # Driver ODBC
}}

# Configurações da Aplicação Flask
APP_CONFIG = {{
    'SECRET_KEY': 'sua_chave_secreta_aqui',  # Chave secreta para sessões
    'UPLOAD_FOLDER': 'uploads',              # Pasta para uploads
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # Tamanho máximo de upload (16MB)
    'ALLOWED_EXTENSIONS': {{'png', 'jpg', 'jpeg', 'gif', 'bmp'}}  # Extensões permitidas
}}

# Configurações de Reconhecimento Facial
FACE_RECOGNITION_CONFIG = {{
    'similarity_threshold': 0.7,  # Limiar de similaridade (0.0 a 1.0)
    'min_face_size': 20,         # Tamanho mínimo da face para detecção
    'scale_factor': 1.1,         # Fator de escala para detecção
    'min_neighbors': 5           # Número mínimo de vizinhos para detecção
}}

# Configurações de Debug
DEBUG = True  # Ative para desenvolvimento, desative para produção
'''
    
    try:
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ Arquivo config.py atualizado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar config.py: {e}")
        return False

def main():
    """Função principal do script de configuração"""
    print("🔧 Configuração do Banco de Dados SQL Server")
    print("=" * 50)
    
    print("\n📋 Informações necessárias:")
    print("1. Endereço do servidor SQL Server")
    print("2. Nome do banco de dados")
    print("3. Usuário SQL Server")
    print("4. Senha SQL Server")
    print("5. Driver ODBC (padrão: ODBC Driver 17 for SQL Server)")
    
    print("\n💡 Dicas:")
    print("- Para SQL Server local: use 'localhost' ou '.'")
    print("- Para SQL Server Express: use 'localhost\\SQLEXPRESS'")
    print("- Para Azure SQL: use 'seu-servidor.database.windows.net'")
    
    print("\n" + "=" * 50)
    
    # Obtém as configurações do usuário
    server = get_user_input("Endereço do servidor SQL Server", DB_CONFIG['server'])
    database = get_user_input("Nome do banco de dados", DB_CONFIG['database'])
    username = get_user_input("Usuário SQL Server", DB_CONFIG['username'])
    password = get_user_input("Senha SQL Server", DB_CONFIG['password'])
    
    print("\n🔍 Testando conexão...")
    
    # Testa a conexão
    if test_connection(server, database, username, password):
        print("\n💾 Salvando configurações...")
        
        # Atualiza o arquivo config.py
        if update_config_file(server, database, username, password):
            print("\n✅ Configuração concluída com sucesso!")
            print("\n📝 Próximos passos:")
            print("1. Execute: python test_db.py")
            print("2. Execute: python app_simple_fixed.py")
            print("3. Acesse: http://localhost:5000")
        else:
            print("\n❌ Erro ao salvar configurações")
    else:
        print("\n❌ Falha na conexão. Verifique:")
        print("1. Se o SQL Server está rodando")
        print("2. Se as credenciais estão corretas")
        print("3. Se o banco de dados existe")
        print("4. Se o driver ODBC está instalado")
        print("\n🔄 Execute este script novamente após corrigir os problemas.")

if __name__ == "__main__":
    main() 