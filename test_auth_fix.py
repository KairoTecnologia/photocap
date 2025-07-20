#!/usr/bin/env python3
"""
Script para testar a autenticação de usuários
"""

from db_manager import DatabaseManager
import hashlib
import os

def test_auth():
    """Testa a autenticação de usuários"""
    print("🔐 Testando autenticação de usuários...")
    
    # Inicializa o gerenciador de banco
    db = DatabaseManager()
    
    # Teste 1: Criar um usuário de teste
    print("\n📝 Teste 1: Criando usuário de teste...")
    test_email = "teste@teste.com"
    test_password = "123456"
    test_username = "usuario_teste"
    
    # Remove usuário se já existir
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Users WHERE Email = ?", (test_email,))
            conn.commit()
            print("✅ Usuário anterior removido")
    except:
        pass
    
    # Cria novo usuário
    user_id = db.create_user(test_username, test_password, test_email)
    if user_id:
        print(f"✅ Usuário criado com ID: {user_id}")
    else:
        print("❌ Falha ao criar usuário")
        return
    
    # Teste 2: Verificar se o usuário foi salvo corretamente
    print("\n🔍 Teste 2: Verificando dados salvos...")
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT UserId, Username, Email, PasswordHash, PasswordSalt
                FROM Users WHERE Email = ?
            """, (test_email,))
            
            user_data = cursor.fetchone()
            if user_data:
                user_id, username, email, password_hash, password_salt = user_data
                print(f"✅ Usuário encontrado:")
                print(f"   ID: {user_id}")
                print(f"   Username: {username}")
                print(f"   Email: {email}")
                print(f"   PasswordHash: {password_hash[:20]}..." if password_hash else "None")
                print(f"   PasswordSalt: {password_salt[:20]}..." if password_salt else "None")
            else:
                print("❌ Usuário não encontrado no banco")
                return
    except Exception as e:
        print(f"❌ Erro ao verificar usuário: {e}")
        return
    
    # Teste 3: Testar autenticação
    print("\n🔐 Teste 3: Testando autenticação...")
    
    # Teste com senha correta
    print("   Testando com senha correta...")
    user = db.authenticate_user_by_email(test_email, test_password)
    if user:
        print(f"   ✅ Autenticação bem-sucedida: {user}")
    else:
        print("   ❌ Falha na autenticação com senha correta")
    
    # Teste com senha incorreta
    print("   Testando com senha incorreta...")
    user = db.authenticate_user_by_email(test_email, "senha_errada")
    if user:
        print("   ❌ Autenticação bem-sucedida com senha incorreta (ERRO)")
    else:
        print("   ✅ Autenticação corretamente rejeitada com senha incorreta")
    
    # Teste 4: Verificar hash manualmente
    print("\n🔍 Teste 4: Verificando hash manualmente...")
    try:
        # Gera hash da senha fornecida
        test_hash = hashlib.pbkdf2_hmac('sha256', test_password.encode('utf-8'), password_salt, 100000)
        
        print(f"   Hash da senha fornecida: {test_hash[:20]}...")
        print(f"   Hash armazenado: {password_hash[:20]}...")
        print(f"   Hashes são iguais: {test_hash == password_hash}")
        
        # Testa a função verify_password
        is_valid = db.verify_password(password_hash, password_salt, test_password)
        print(f"   verify_password retorna: {is_valid}")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar hash: {e}")
    
    print("\n✅ Teste de autenticação concluído!")

if __name__ == "__main__":
    test_auth() 