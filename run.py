#!/usr/bin/env python3
"""
PhotoCap - Aplicação Principal
Sistema de gerenciamento de fotos de eventos
"""

from app import create_app
from db_manager import DatabaseManager
import os

def main():
    """Função principal para iniciar a aplicação"""
    print("🚀 Iniciando PhotoCap...")
    
    # Verificar conexão com banco de dados
    data_manager = DatabaseManager()
    if data_manager.test_connection():
        print("✅ Conexão com SQL Server estabelecida com sucesso!")
        print("✅ Gerenciador de dados SQL Server carregado")
    else:
        print("❌ Erro ao conectar com o banco de dados")
        return
    
    # Criar pasta de uploads se não existir
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print("📁 Pasta uploads criada")
    else:
        print("📁 Pasta uploads verificada")
    
    # Criar pasta de sessões se não existir
    sessions_dir = 'flask_session'
    if not os.path.exists(sessions_dir):
        os.makedirs(sessions_dir)
        print("📁 Pasta de sessões criada")
    
    print("🔧 Configurações carregadas")
    
    # Criar e executar a aplicação
    app = create_app()
    
    # Configurações de desenvolvimento
    app.config['DEBUG'] = True
    app.config['HOST'] = '0.0.0.0'
    app.config['PORT'] = 5000
    
    print(f"🌐 Servidor iniciado em http://localhost:{app.config['PORT']}")
    print("📝 Modo debug ativado")
    print("🔄 Para parar o servidor, pressione Ctrl+C")
    
    # Executar a aplicação
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )

if __name__ == '__main__':
    main() 