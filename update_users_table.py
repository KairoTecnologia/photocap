#!/usr/bin/env python3
"""
Script para adicionar novos campos à tabela Users
"""

from db_manager import DatabaseManager

def update_users_table():
    """Adiciona novos campos à tabela Users"""
    print("🔧 Atualizando tabela Users com novos campos...")
    
    db = DatabaseManager()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Lista de campos para adicionar
            new_fields = [
                ('FullName', 'VARCHAR(255)'),
                ('CPF', 'VARCHAR(14)'),
                ('Phone', 'VARCHAR(20)')
            ]
            
            for field_name, field_type in new_fields:
                # Verifica se o campo já existe
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'Users' AND COLUMN_NAME = '{field_name}'
                """)
                
                field_exists = cursor.fetchone()[0] > 0
                
                if field_exists:
                    print(f"✅ Campo {field_name} já existe na tabela Users")
                else:
                    # Adiciona o campo
                    cursor.execute(f"""
                        ALTER TABLE Users 
                        ADD {field_name} {field_type}
                    """)
                    
                    conn.commit()
                    print(f"✅ Campo {field_name} adicionado com sucesso")
            
            # Atualiza usuários existentes com valores padrão
            cursor.execute("""
                UPDATE Users 
                SET FullName = Username,
                    CPF = NULL,
                    Phone = NULL
                WHERE FullName IS NULL
            """)
            
            conn.commit()
            print("✅ Usuários existentes atualizados com valores padrão")
            
            # Lista estrutura atual da tabela
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Users'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            print(f"\n📊 Estrutura atual da tabela Users:")
            
            for column in columns:
                col_name, data_type, is_nullable = column
                print(f"   📋 {col_name}: {data_type} ({'NULL' if is_nullable == 'YES' else 'NOT NULL'})")
            
            print("\n✅ Tabela Users atualizada com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao atualizar tabela Users: {e}")

if __name__ == "__main__":
    update_users_table() 