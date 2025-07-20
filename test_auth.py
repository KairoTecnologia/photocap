#!/usr/bin/env python3
"""
Script para testar o sistema de autenticação do PhotoCap
"""

from data_manager import DataManager
from datetime import datetime

def test_auth_system():
    """Testa o sistema de autenticação"""
    print("🧪 Testando sistema de autenticação...")
    
    # Cria uma instância do gerenciador de dados
    dm = DataManager('test_data.json')
    
    # Limpa dados de teste anteriores
    dm.clear_data()
    
    # Teste 1: Cadastro de usuário
    print("\n1️⃣ Testando cadastro de usuário...")
    try:
        user_data = {
            'username': 'Teste Usuário',
            'email': 'teste@exemplo.com',
            'password': '123456',
            'user_type': 'customer',
            'created_at': datetime.now()
        }
        
        user_id = dm.add_user(user_data)
        print(f"✅ Usuário cadastrado com ID: {user_id}")
        
        # Verifica se o usuário foi salvo
        users = dm.get_users()
        if user_id in users:
            saved_user = users[user_id]
            print(f"✅ Usuário encontrado: {saved_user['username']} ({saved_user['email']})")
        else:
            print("❌ Usuário não encontrado após cadastro")
            return False
            
    except Exception as e:
        print(f"❌ Erro no cadastro: {e}")
        return False
    
    # Teste 2: Login de usuário
    print("\n2️⃣ Testando login de usuário...")
    try:
        users = dm.get_users()
        email = 'teste@exemplo.com'
        password = '123456'
        
        user = None
        for u in users.values():
            if u['email'] == email and u['password'] == password:
                user = u
                break
        
        if user:
            print(f"✅ Login bem-sucedido: {user['username']} (ID: {user['id']})")
        else:
            print("❌ Login falhou - usuário não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False
    
    # Teste 3: Cadastro de fotógrafo
    print("\n3️⃣ Testando cadastro de fotógrafo...")
    try:
        photographer_data = {
            'username': 'Fotógrafo Teste',
            'email': 'fotografo@exemplo.com',
            'password': '123456',
            'user_type': 'photographer',
            'created_at': datetime.now()
        }
        
        photographer_id = dm.add_user(photographer_data)
        print(f"✅ Fotógrafo cadastrado com ID: {photographer_id}")
        
        # Verifica se o fotógrafo foi salvo
        users = dm.get_users()
        if photographer_id in users:
            saved_photographer = users[photographer_id]
            print(f"✅ Fotógrafo encontrado: {saved_photographer['username']} ({saved_photographer['email']})")
        else:
            print("❌ Fotógrafo não encontrado após cadastro")
            return False
            
    except Exception as e:
        print(f"❌ Erro no cadastro do fotógrafo: {e}")
        return False
    
    # Teste 4: Login do fotógrafo
    print("\n4️⃣ Testando login do fotógrafo...")
    try:
        users = dm.get_users()
        email = 'fotografo@exemplo.com'
        password = '123456'
        
        photographer = None
        for u in users.values():
            if u['email'] == email and u['password'] == password:
                photographer = u
                break
        
        if photographer:
            print(f"✅ Login do fotógrafo bem-sucedido: {photographer['username']} (ID: {photographer['id']})")
            print(f"   Tipo de usuário: {photographer['user_type']}")
        else:
            print("❌ Login do fotógrafo falhou")
            return False
            
    except Exception as e:
        print(f"❌ Erro no login do fotógrafo: {e}")
        return False
    
    # Teste 5: Verificar dados salvos
    print("\n5️⃣ Verificando dados salvos...")
    try:
        users = dm.get_users()
        print(f"✅ Total de usuários: {len(users)}")
        
        for user_id, user in users.items():
            print(f"   - ID {user_id}: {user['username']} ({user['email']}) - {user['user_type']}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")
        return False
    
    print("\n🎉 Todos os testes passaram!")
    return True

if __name__ == '__main__':
    success = test_auth_system()
    if success:
        print("\n✅ Sistema de autenticação funcionando corretamente!")
    else:
        print("\n❌ Sistema de autenticação com problemas!") 