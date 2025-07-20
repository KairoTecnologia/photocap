import pyodbc
import hashlib
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self, server=None, database=None, username=None, password=None):
        """Inicializa o gerenciador de banco de dados"""
        # Usa configurações do config.py se não fornecidas
        self.server = server or DB_CONFIG['server']
        self.database = database or DB_CONFIG['database']
        self.username = username or DB_CONFIG['username']
        self.password = password or DB_CONFIG['password']
        self.driver = DB_CONFIG['driver']
        
        # Configura string de conexão baseada no tipo de autenticação
        if self.username and self.password:
            # Autenticação SQL Server
            self.connection_string = (
                f'DRIVER={{{self.driver}}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password}'
            )
        else:
            # Autenticação Windows
            self.connection_string = (
                f'DRIVER={{{self.driver}}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'Trusted_Connection=yes;'
            )
        self.test_connection()
    
    def test_connection(self):
        """Testa a conexão com o banco de dados"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                print("✅ Conexão com SQL Server estabelecida com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao conectar com SQL Server: {e}")
            raise
    
    def get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        return pyodbc.connect(self.connection_string)
    
    # Métodos para hash e salt de senhas
    def hash_password(self, password: str) -> tuple:
        """Gera hash e salt para uma senha"""
        salt = os.urandom(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return pwd_hash, salt
    
    def verify_password(self, stored_hash: bytes, stored_salt: bytes, provided_password: str) -> bool:
        """Verifica se uma senha fornecida corresponde ao hash armazenado"""
        pwd_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), stored_salt, 100000)
        return pwd_hash == stored_hash
    
    # Métodos para usuários
    def create_user(self, username: str, password: str, email: str, user_type: str = 'customer', full_name: str = None, cpf: str = None, phone: str = None) -> Optional[int]:
        """Cria um novo usuário no banco de dados"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verifica se o usuário já existe
                cursor.execute("SELECT UserId FROM Users WHERE Username = ?", (username,))
                if cursor.fetchone():
                    print(f"❌ Usuário '{username}' já existe")
                    return None
                
                # Gera hash e salt da senha
                password_hash, password_salt = self.hash_password(password)
                
                # Insere o usuário
                cursor.execute("""
                    INSERT INTO Users (Username, PasswordHash, PasswordSalt, Email, UserType, FullName, CPF, Phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (username, password_hash, password_salt, email, user_type, full_name, cpf, phone))
                
                conn.commit()
                user_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
                print(f"✅ Usuário '{username}' criado com sucesso (ID: {user_id}, Tipo: {user_type})")
                return user_id
                
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica um usuário por username"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT UserId, Username, PasswordHash, PasswordSalt, Email
                    FROM Users WHERE Username = ?
                """, (username,))
                
                user_data = cursor.fetchone()
                if not user_data:
                    print(f"❌ Usuário '{username}' não encontrado")
                    return None
                
                user_id, username, password_hash, password_salt, email = user_data
                
                # Verifica a senha
                if self.verify_password(password_hash, password_salt, password):
                    print(f"✅ Usuário '{username}' autenticado com sucesso")
                    return {
                        'UserId': user_id,
                        'Username': username,
                        'Email': email
                    }
                else:
                    print(f"❌ Senha incorreta para usuário '{username}'")
                    return None
                    
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            return None

    def authenticate_user_by_email(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica um usuário por e-mail"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT UserId, Username, PasswordHash, PasswordSalt, Email, UserType, FullName, CPF, Phone
                    FROM Users WHERE Email = ?
                """, (email,))
                
                user_data = cursor.fetchone()
                if not user_data:
                    print(f"❌ E-mail '{email}' não encontrado")
                    return None
                
                user_id, username, password_hash, password_salt, email, user_type, full_name, cpf, phone = user_data
                
                # Verifica a senha
                if self.verify_password(password_hash, password_salt, password):
                    print(f"✅ Usuário '{username}' autenticado com sucesso (Tipo: {user_type})")
                    return {
                        'UserId': user_id,
                        'Username': username,
                        'Email': email,
                        'UserType': user_type,
                        'FullName': full_name,
                        'CPF': cpf,
                        'Phone': phone
                    }
                else:
                    print(f"❌ Senha incorreta para e-mail '{email}'")
                    return None
                    
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Busca um usuário pelo ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT UserId, Username, Email
                    FROM Users WHERE UserId = ?
                """, (user_id,))
                
                user_data = cursor.fetchone()
                if user_data:
                    return {
                        'UserId': user_data[0],
                        'Username': user_data[1],
                        'Email': user_data[2]
                    }
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar usuário: {e}")
            return None
    
    # Métodos para eventos
    def create_event(self, name: str, date: str) -> Optional[int]:
        """Cria um novo evento"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO Events (Name, Date)
                    VALUES (?, ?)
                """, (name, date))
                
                conn.commit()
                event_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
                print(f"✅ Evento '{name}' criado com sucesso (ID: {event_id})")
                return event_id
                
        except Exception as e:
            print(f"❌ Erro ao criar evento: {e}")
            return None
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Retorna todos os eventos"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT EventId, Name, Date
                    FROM Events
                    ORDER BY Date DESC
                """)
                
                events = []
                for row in cursor.fetchall():
                    events.append({
                        'EventId': row[0],
                        'Name': row[1],
                        'Date': row[2].strftime('%Y-%m-%d') if row[2] else None
                    })
                
                return events
                
        except Exception as e:
            print(f"❌ Erro ao buscar eventos: {e}")
            return []
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Busca um evento pelo ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT EventId, Name, Date
                    FROM Events WHERE EventId = ?
                """, (event_id,))
                
                event_data = cursor.fetchone()
                if event_data:
                    return {
                        'EventId': event_data[0],
                        'Name': event_data[1],
                        'Date': event_data[2].strftime('%Y-%m-%d') if event_data[2] else None
                    }
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar evento: {e}")
            return None
    
    def search_events(self, event_name: str) -> List[Dict[str, Any]]:
        """Busca eventos por nome"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT EventId, Name, Date
                    FROM Events 
                    WHERE Name LIKE ?
                    ORDER BY Date DESC
                """, (f'%{event_name}%',))
                
                events = []
                for row in cursor.fetchall():
                    events.append({
                        'EventId': row[0],
                        'Name': row[1],
                        'Date': row[2].strftime('%Y-%m-%d') if row[2] else None
                    })
                
                return events
                
        except Exception as e:
            print(f"❌ Erro ao buscar eventos: {e}")
            return []
    
    # Métodos para fotos
    def save_photo(self, event_id: int, filename: str, image_data: bytes = None) -> Optional[int]:
        """Salva uma foto no banco de dados"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO Photos (EventId, Filename, UploadDate, Image)
                    VALUES (?, ?, ?, ?)
                """, (event_id, filename, datetime.now(), image_data))
                
                conn.commit()
                photo_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
                print(f"✅ Foto '{filename}' salva com sucesso (ID: {photo_id})")
                return photo_id
                
        except Exception as e:
            print(f"❌ Erro ao salvar foto: {e}")
            return None
    
    def get_photos_by_event(self, event_id: int) -> List[Dict[str, Any]]:
        """Retorna todas as fotos de um evento"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT PhotoId, EventId, Filename, UploadDate
                    FROM Photos 
                    WHERE EventId = ?
                    ORDER BY UploadDate DESC
                """, (event_id,))
                
                photos = []
                for row in cursor.fetchall():
                    photos.append({
                        'PhotoId': row[0],
                        'EventId': row[1],
                        'Filename': row[2],
                        'UploadDate': row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None
                    })
                
                return photos
                
        except Exception as e:
            print(f"❌ Erro ao buscar fotos: {e}")
            return []
    
    def get_all_photos(self) -> List[Dict[str, Any]]:
        """Retorna todas as fotos"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT PhotoId, EventId, Filename, UploadDate
                    FROM Photos
                    ORDER BY UploadDate DESC
                """)
                
                photos = []
                for row in cursor.fetchall():
                    photos.append({
                        'PhotoId': row[0],
                        'EventId': row[1],
                        'Filename': row[2],
                        'UploadDate': row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None
                    })
                
                return photos
                
        except Exception as e:
            print(f"❌ Erro ao buscar fotos: {e}")
            return []
    
    def get_photo_by_id(self, photo_id: int) -> Optional[Dict[str, Any]]:
        """Busca uma foto pelo ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT PhotoId, EventId, Filename, UploadDate, Image
                    FROM Photos WHERE PhotoId = ?
                """, (photo_id,))
                
                photo_data = cursor.fetchone()
                if photo_data:
                    return {
                        'PhotoId': photo_data[0],
                        'EventId': photo_data[1],
                        'Filename': photo_data[2],
                        'UploadDate': photo_data[3].strftime('%Y-%m-%d %H:%M:%S') if photo_data[3] else None,
                        'Image': photo_data[4]
                    }
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar foto: {e}")
            return None
    
    # Métodos de compatibilidade com o app_simple_fixed.py
    def get_users(self) -> List[Dict[str, Any]]:
        """Retorna todos os usuários (compatibilidade)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT UserId, Username, Email, UserType, FullName, CPF, Phone, CreatedDate
                    FROM Users
                    ORDER BY CreatedDate DESC
                """)
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'UserId': row[0],
                        'Username': row[1],
                        'Email': row[2],
                        'UserType': row[3] if row[3] else 'customer',
                        'FullName': row[4],
                        'CPF': row[5],
                        'Phone': row[6],
                        'CreatedDate': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None
                    })
                
                return users
                
        except Exception as e:
            print(f"❌ Erro ao buscar usuários: {e}")
            return []
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Retorna todos os eventos (compatibilidade)"""
        return self.get_all_events()
    
    def get_photos(self) -> List[Dict[str, Any]]:
        """Retorna todas as fotos (compatibilidade)"""
        return self.get_all_photos()
    
    def get_photo_analyses(self) -> List[Dict[str, Any]]:
        """Retorna análises de fotos (compatibilidade)"""
        # Por enquanto retorna lista vazia, pode ser implementado depois
        return []
    
    def add_user(self, user_data: Dict[str, Any]) -> Optional[int]:
        """Adiciona um usuário (compatibilidade)"""
        return self.create_user(
            user_data.get('username', ''),
            user_data.get('password', ''),
            user_data.get('email', ''),
            user_data.get('user_type', 'customer'),
            user_data.get('full_name'),
            user_data.get('cpf'),
            user_data.get('phone')
        )
    
    def add_event(self, event_data: Dict[str, Any]) -> Optional[int]:
        """Adiciona um evento (compatibilidade)"""
        return self.create_event(
            event_data.get('name', ''),
            event_data.get('date', '')
        )
    
    def add_photo(self, photo_data: Dict[str, Any]) -> Optional[int]:
        """Adiciona uma foto (compatibilidade)"""
        return self.save_photo(
            photo_data.get('event_id', 0),
            photo_data.get('filename', ''),
            photo_data.get('image_data')
        )

# Exemplo de uso
if __name__ == "__main__":
    # Configurações do banco - ajuste conforme seu ambiente
    db = DatabaseManager(
        server='localhost',
        database='PhotoCap',
        username='sa',  # ou seu usuário
        password=''     # sua senha
    )
    
    # Teste de criação de usuário
    user_id = db.create_user('teste', 'senha123', 'teste@email.com')
    if user_id:
        print(f"Usuário criado com ID: {user_id}")
    
    # Teste de autenticação
    user = db.authenticate_user('teste', 'senha123')
    if user:
        print(f"Usuário autenticado: {user}")
    
    # Teste de criação de evento
    event_id = db.create_event('Evento Teste', '2024-01-15')
    if event_id:
        print(f"Evento criado com ID: {event_id}")
    
    # Listar eventos
    events = db.get_all_events()
    print(f"Eventos encontrados: {len(events)}")
    for event in events:
        print(f"- {event['Name']} ({event['Date']})") 