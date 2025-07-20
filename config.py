import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do Banco de Dados SQL Server
DB_CONFIG = {
    'server': 'DESKTOP-R2179A0\\SQLEXPRESS',  # Endereço do servidor SQL Server Express
    'database': 'PhotoCap',       # Nome do banco de dados
    'username': '',              # Vazio para autenticação Windows
    'password': '',              # Vazio para autenticação Windows
    'driver': 'ODBC Driver 17 for SQL Server',  # Driver ODBC
    'trusted_connection': 'yes'  # Usar autenticação Windows
}

# Configurações da Aplicação Flask
APP_CONFIG = {
    'SECRET_KEY': 'sua_chave_secreta_aqui',  # Chave secreta para sessões
    'UPLOAD_FOLDER': 'uploads',              # Pasta para uploads
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # Tamanho máximo de upload (16MB)
    'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif', 'bmp'}  # Extensões permitidas
}

# Configurações de Reconhecimento Facial
FACE_RECOGNITION_CONFIG = {
    'similarity_threshold': 0.7,  # Limiar de similaridade (0.0 a 1.0)
    'min_face_size': 20,         # Tamanho mínimo da face para detecção
    'scale_factor': 1.1,         # Fator de escala para detecção
    'min_neighbors': 5           # Número mínimo de vizinhos para detecção
}

# Configurações de Debug
DEBUG = True  # Ative para desenvolvimento, desative para produção 