#!/usr/bin/env python3
"""
Script para adicionar o campo UserType à tabela Users
"""

from db_manager import DatabaseManager

def add_user_type_column():
    """Adiciona o campo UserType à tabela Users"""
    print("🔧 Adicionando campo UserType à tabela Users...")
    
    db = DatabaseManager()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verifica se o campo já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Users' AND COLUMN_NAME = 'UserType'
            """)
            
            column_exists = cursor.fetchone()[0] > 0
            
            if column_exists:
                print("✅ Campo UserType já existe na tabela Users")
            else:
                # Adiciona o campo UserType
                cursor.execute("""
                    ALTER TABLE Users 
                    ADD UserType VARCHAR(20) DEFAULT 'customer'
                """)
                
                conn.commit()
                print("✅ Campo UserType adicionado com sucesso")
            
            # Atualiza usuários existentes para ter um tipo padrão
            cursor.execute("""
                UPDATE Users 
                SET UserType = 'customer' 
                WHERE UserType IS NULL
            """)
            
            conn.commit()
            print("✅ Usuários existentes atualizados com tipo padrão 'customer'")
            
            # Lista todos os usuários com seus tipos
            cursor.execute("""
                SELECT UserId, Username, Email, UserType
                FROM Users
                ORDER BY UserId
            """)
            
            users = cursor.fetchall()
            print(f"\n📊 Usuários na tabela ({len(users)} total):")
            
            for user in users:
                user_id, username, email, user_type = user
                print(f"   👤 ID: {user_id}, Username: {username}, Email: {email}, Tipo: {user_type}")
            
            print("\n✅ Campo UserType configurado com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao adicionar campo UserType: {e}")

if __name__ == "__main__":
    add_user_type_column() 