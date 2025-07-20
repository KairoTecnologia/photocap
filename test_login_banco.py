#!/usr/bin/env python3
"""
Script para testar se o login está buscando corretamente no banco PhotoCap
"""

from db_manager import DatabaseManager
import hashlib

def test_login_banco():
    """Testa se o login está buscando corretamente no banco PhotoCap"""
    print("🔍 Testando busca no banco PhotoCap durante login...")
    
    # Inicializa o gerenciador de banco
    db = DatabaseManager()
    
    # Teste 1: Verificar conexão com o banco PhotoCap
    print("\n📊 Teste 1: Verificando conexão com banco PhotoCap...")
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()[0]
            print(f"   ✅ Conectado ao banco: {db_name}")
            
            if db_name == "PhotoCap":
                print("   ✅ Banco correto: PhotoCap")
            else:
                print(f"   ❌ Banco incorreto: {db_name} (esperado: PhotoCap)")
                return
    except Exception as e:
        print(f"   ❌ Erro ao verificar banco: {e}")
        return
    
    # Teste 2: Verificar se a tabela Users existe
    print("\n📋 Teste 2: Verificando tabela Users...")
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'Users'
            """)
            table_exists = cursor.fetchone()[0] > 0
            
            if table_exists:
                print("   ✅ Tabela Users existe")
            else:
                print("   ❌ Tabela Users não existe")
                return
    except Exception as e:
        print(f"   ❌ Erro ao verificar tabela: {e}")
        return
    
    # Teste 3: Listar todos os usuários no banco
    print("\n👥 Teste 3: Listando usuários no banco...")
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT UserId, Username, Email, 
                       CASE WHEN PasswordHash IS NOT NULL THEN 'HASHED' ELSE 'NULL' END as PasswordStatus
                FROM Users
                ORDER BY UserId
            """)
            
            users = cursor.fetchall()
            print(f"   📊 Total de usuários: {len(users)}")
            
            for user in users:
                user_id, username, email, password_status = user
                print(f"   👤 ID: {user_id}, Username: {username}, Email: {email}, Senha: {password_status}")
    except Exception as e:
        print(f"   ❌ Erro ao listar usuários: {e}")
        return
    
    # Teste 4: Testar busca por email específico
    print("\n🔍 Teste 4: Testando busca por email...")
    test_email = "teste@teste.com"
    
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
                print(f"   ✅ Usuário encontrado:")
                print(f"      ID: {user_id}")
                print(f"      Username: {username}")
                print(f"      Email: {email}")
                print(f"      PasswordHash: {'Presente' if password_hash else 'Ausente'}")
                print(f"      PasswordSalt: {'Presente' if password_salt else 'Ausente'}")
            else:
                print(f"   ❌ Usuário com email '{test_email}' não encontrado")
                return
    except Exception as e:
        print(f"   ❌ Erro ao buscar usuário: {e}")
        return
    
    # Teste 5: Testar autenticação completa
    print("\n🔐 Teste 5: Testando autenticação completa...")
    test_password = "123456"
    
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
    
    # Teste 6: Verificar hash manualmente
    print("\n🔍 Teste 6: Verificando hash manualmente...")
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT PasswordHash, PasswordSalt
                FROM Users WHERE Email = ?
            """, (test_email,))
            
            hash_data = cursor.fetchone()
            if hash_data:
                stored_hash, stored_salt = hash_data
                
                # Gera hash da senha fornecida
                test_hash = hashlib.pbkdf2_hmac('sha256', test_password.encode('utf-8'), stored_salt, 100000)
                
                print(f"   Hash da senha fornecida: {test_hash[:20]}...")
                print(f"   Hash armazenado: {stored_hash[:20]}...")
                print(f"   Hashes são iguais: {test_hash == stored_hash}")
                
                # Testa a função verify_password
                is_valid = db.verify_password(stored_hash, stored_salt, test_password)
                print(f"   verify_password retorna: {is_valid}")
            else:
                print("   ❌ Dados de hash não encontrados")
    except Exception as e:
        print(f"   ❌ Erro ao verificar hash: {e}")
    
    print("\n✅ Teste de busca no banco PhotoCap concluído!")

if __name__ == "__main__":
    test_login_banco() 