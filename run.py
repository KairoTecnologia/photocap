#!/usr/bin/env python3
"""
Script para executar a aplicação PhotoCap
"""

import os
import sys
from app import app, db

def create_directories():
    """Cria diretórios necessários se não existirem"""
    directories = ['uploads', 'migrations']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Diretório '{directory}' criado.")

def init_database():
    """Inicializa o banco de dados"""
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado.")

def main():
    """Função principal"""
    print("🚀 Iniciando PhotoCap...")
    
    # Cria diretórios necessários
    create_directories()
    
    # Inicializa banco de dados
    init_database()
    
    print("✅ PhotoCap está pronto!")
    print("🌐 Acesse: http://localhost:5000")
    print("📸 Funcionalidades disponíveis:")
    print("   - Reconhecimento facial")
    print("   - Detecção de números de peito")
    print("   - Upload de fotos")
    print("   - Sistema de busca")
    print("\nPressione Ctrl+C para parar o servidor.")
    
    # Executa a aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main() 