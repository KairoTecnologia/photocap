#!/usr/bin/env python3
"""
Script para converter um usuário em fotógrafo
"""

from db_manager import DatabaseManager

def make_photographer():
    """Converte um usuário em fotógrafo"""
    print("📸 Convertendo usuário em fotógrafo...")
    
    db = DatabaseManager()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Lista usuários disponíveis
            cursor.execute("""
                SELECT UserId, Username, Email, UserType
                FROM Users
                ORDER BY UserId
            """)
            
            users = cursor.fetchall()
            print(f"\n📊 Usuários disponíveis ({len(users)} total):")
            
            for user in users:
                user_id, username, email, user_type = user
                print(f"   {user_id}. {username} ({email}) - Tipo: {user_type}")
            
            # Converte o primeiro usuário em fotógrafo
            if users:
                user_id = users[0][0]
                username = users[0][1]
                
                cursor.execute("""
                    UPDATE Users 
                    SET UserType = 'photographer' 
                    WHERE UserId = ?
                """, (user_id,))
                
                conn.commit()
                print(f"\n✅ Usuário '{username}' (ID: {user_id}) convertido em fotógrafo!")
                
                # Verifica a atualização
                cursor.execute("""
                    SELECT UserId, Username, Email, UserType
                    FROM Users
                    WHERE UserId = ?
                """, (user_id,))
                
                updated_user = cursor.fetchone()
                if updated_user:
                    print(f"   ✅ Confirmação: {updated_user[1]} agora é {updated_user[3]}")
            else:
                print("❌ Nenhum usuário encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao converter usuário: {e}")

if __name__ == "__main__":
    make_photographer() 