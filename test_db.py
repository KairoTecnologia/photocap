#!/usr/bin/env python3
"""
Script de teste para o módulo de banco de dados
"""

import sys
import os

# Adiciona o diretório atual ao path para importar o módulo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_manager import DatabaseManager

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print("🔍 Testando conexão com o banco de dados...")
    
    try:
        # Usa configurações do config.py
        db = DatabaseManager()
        
        print("✅ Conexão estabelecida com sucesso!")
        return db
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("\n💡 Verifique:")
        print("1. Se o SQL Server está rodando")
        print("2. Se as credenciais estão corretas")
        print("3. Se o banco 'PhotoCap' existe")
        print("4. Se o driver ODBC está instalado")
        return None

def test_user_operations(db):
    """Testa operações de usuário"""
    print("\n👤 Testando operações de usuário...")
    
    # Teste de criação de usuário
    print("Criando usuário de teste...")
    user_id = db.create_user('usuario_teste', 'senha123', 'teste@email.com')
    
    if user_id:
        print(f"✅ Usuário criado com ID: {user_id}")
        
        # Teste de autenticação
        print("Testando autenticação...")
        user = db.authenticate_user('usuario_teste', 'senha123')
        if user:
            print(f"✅ Usuário autenticado: {user['Username']}")
        else:
            print("❌ Falha na autenticação")
        
        # Teste de busca por ID
        print("Buscando usuário por ID...")
        user_data = db.get_user_by_id(user_id)
        if user_data:
            print(f"✅ Usuário encontrado: {user_data['Username']}")
        else:
            print("❌ Usuário não encontrado")
    else:
        print("❌ Falha ao criar usuário")

def test_event_operations(db):
    """Testa operações de evento"""
    print("\n📅 Testando operações de evento...")
    
    # Teste de criação de evento
    print("Criando evento de teste...")
    event_id = db.create_event('Evento Teste 2024', '2024-01-15')
    
    if event_id:
        print(f"✅ Evento criado com ID: {event_id}")
        
        # Teste de busca por ID
        print("Buscando evento por ID...")
        event_data = db.get_event_by_id(event_id)
        if event_data:
            print(f"✅ Evento encontrado: {event_data['Name']}")
        else:
            print("❌ Evento não encontrado")
        
        # Teste de busca por nome
        print("Buscando eventos por nome...")
        events = db.search_events('Teste')
        print(f"✅ Encontrados {len(events)} eventos com 'Teste' no nome")
        
        # Listar todos os eventos
        print("Listando todos os eventos...")
        all_events = db.get_all_events()
        print(f"✅ Total de eventos: {len(all_events)}")
        for event in all_events:
            print(f"  - {event['Name']} ({event['Date']})")
    else:
        print("❌ Falha ao criar evento")

def test_photo_operations(db):
    """Testa operações de foto"""
    print("\n📸 Testando operações de foto...")
    
    # Primeiro, vamos criar um evento para associar a foto
    event_id = db.create_event('Evento para Fotos', '2024-01-20')
    
    if event_id:
        print(f"✅ Evento criado para teste de fotos (ID: {event_id})")
        
        # Teste de salvamento de foto (sem dados de imagem por enquanto)
        print("Salvando foto de teste...")
        photo_id = db.save_photo(event_id, 'foto_teste.jpg')
        
        if photo_id:
            print(f"✅ Foto salva com ID: {photo_id}")
            
            # Teste de busca por ID
            print("Buscando foto por ID...")
            photo_data = db.get_photo_by_id(photo_id)
            if photo_data:
                print(f"✅ Foto encontrada: {photo_data['Filename']}")
            else:
                print("❌ Foto não encontrada")
            
            # Teste de busca por evento
            print("Buscando fotos do evento...")
            photos = db.get_photos_by_event(event_id)
            print(f"✅ Encontradas {len(photos)} fotos no evento")
            
            # Listar todas as fotos
            print("Listando todas as fotos...")
            all_photos = db.get_all_photos()
            print(f"✅ Total de fotos: {len(all_photos)}")
            for photo in all_photos:
                print(f"  - {photo['Filename']} (Evento ID: {photo['EventId']})")
        else:
            print("❌ Falha ao salvar foto")
    else:
        print("❌ Falha ao criar evento para teste de fotos")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do módulo de banco de dados")
    print("=" * 50)
    
    # Teste de conexão
    db = test_database_connection()
    if not db:
        print("\n❌ Testes interrompidos devido a erro de conexão")
        return
    
    # Testes de operações
    test_user_operations(db)
    test_event_operations(db)
    test_photo_operations(db)
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes concluídos!")

if __name__ == "__main__":
    main() 