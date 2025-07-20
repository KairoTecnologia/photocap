import json
import os
from datetime import datetime

class DataManager:
    def __init__(self, data_file='photocap_data.json'):
        self.data_file = data_file
        self.data = {
            'users': {},
            'events': {},
            'photos': {},
            'photo_analyses': {},
            'next_user_id': 1,
            'next_event_id': 1,
            'next_photo_id': 1
        }
        self.load_data()
    
    def load_data(self):
        """Carrega dados do arquivo JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.data.update(loaded_data)
                print(f"✅ Dados carregados: {len(self.data['users'])} usuários, {len(self.data['events'])} eventos, {len(self.data['photos'])} fotos")
            else:
                print("📁 Arquivo de dados não encontrado. Criando novo arquivo.")
                self.save_data()
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados: {e}")
    
    def save_data(self):
        """Salva dados no arquivo JSON"""
        try:
            # Converte objetos datetime e arrays numpy para formatos serializáveis
            data_to_save = {}
            for key, value in self.data.items():
                if key in ['users', 'events', 'photos', 'photo_analyses']:
                    data_to_save[key] = {}
                    for item_id, item in value.items():
                        data_to_save[key][item_id] = {}
                        for field, field_value in item.items():
                            if isinstance(field_value, datetime):
                                data_to_save[key][item_id][field] = field_value.isoformat()
                            elif hasattr(field_value, 'isoformat'):  # Para objetos date
                                data_to_save[key][item_id][field] = field_value.isoformat()
                            elif hasattr(field_value, 'tolist'):  # Para arrays numpy
                                data_to_save[key][item_id][field] = field_value.tolist()
                            elif isinstance(field_value, list):
                                # Converte arrays numpy dentro de listas
                                converted_list = []
                                for list_item in field_value:
                                    if hasattr(list_item, 'tolist'):
                                        converted_list.append(list_item.tolist())
                                    else:
                                        converted_list.append(list_item)
                                data_to_save[key][item_id][field] = converted_list
                            else:
                                data_to_save[key][item_id][field] = field_value
                else:
                    data_to_save[key] = value
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            print(f"💾 Dados salvos com sucesso")
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")
            import traceback
            print(traceback.format_exc())
    
    def get_users(self):
        """Retorna todos os usuários"""
        return self.data['users']
    
    def get_events(self):
        """Retorna todos os eventos"""
        return self.data['events']
    
    def get_photos(self):
        """Retorna todas as fotos"""
        return self.data['photos']
    
    def get_photo_analyses(self):
        """Retorna todas as análises de fotos"""
        return self.data['photo_analyses']
    
    def add_user(self, user):
        """Adiciona um usuário"""
        user_id = self.data['next_user_id']
        user['id'] = user_id
        self.data['users'][user_id] = user
        self.data['next_user_id'] += 1
        self.save_data()
        return user_id
    
    def add_event(self, event):
        """Adiciona um evento"""
        event_id = self.data['next_event_id']
        event['id'] = event_id
        self.data['events'][event_id] = event
        self.data['next_event_id'] += 1
        self.save_data()
        return event_id
    
    def add_photo(self, photo):
        """Adiciona uma foto"""
        photo_id = self.data['next_photo_id']
        photo['id'] = photo_id
        self.data['photos'][photo_id] = photo
        self.data['next_photo_id'] += 1
        self.save_data()
        return photo_id
    
    def add_photo_analysis(self, photo_id, analysis):
        """Adiciona análise de uma foto"""
        self.data['photo_analyses'][photo_id] = analysis
        self.save_data()
    
    def update_user(self, user_id, user_data):
        """Atualiza um usuário"""
        if user_id in self.data['users']:
            self.data['users'][user_id].update(user_data)
            self.save_data()
    
    def update_event(self, event_id, event_data):
        """Atualiza um evento"""
        if event_id in self.data['events']:
            self.data['events'][event_id].update(event_data)
            self.save_data()
    
    def update_photo(self, photo_id, photo_data):
        """Atualiza uma foto"""
        if photo_id in self.data['photos']:
            self.data['photos'][photo_id].update(photo_data)
            self.save_data()
    
    def delete_user(self, user_id):
        """Remove um usuário"""
        if user_id in self.data['users']:
            del self.data['users'][user_id]
            self.save_data()
    
    def delete_event(self, event_id):
        """Remove um evento"""
        if event_id in self.data['events']:
            del self.data['events'][event_id]
            self.save_data()
    
    def delete_photo(self, photo_id):
        """Remove uma foto"""
        if photo_id in self.data['photos']:
            del self.data['photos'][photo_id]
            if photo_id in self.data['photo_analyses']:
                del self.data['photo_analyses'][photo_id]
            self.save_data()
    
    def get_next_ids(self):
        """Retorna os próximos IDs disponíveis"""
        return {
            'next_user_id': self.data['next_user_id'],
            'next_event_id': self.data['next_event_id'],
            'next_photo_id': self.data['next_photo_id']
        }
    
    def create_sample_data(self):
        """Cria dados de exemplo para teste"""
        print("🎯 Criando dados de exemplo...")
        
        # Usuário fotógrafo
        photographer = {
            'username': 'Fotógrafo Teste',
            'email': 'fotografo@teste.com',
            'password': '123456',
            'user_type': 'photographer',
            'created_at': datetime.now().isoformat()
        }
        photographer_id = self.add_user(photographer)
        
        # Usuário cliente
        client = {
            'username': 'Cliente Teste',
            'email': 'cliente@teste.com',
            'password': '123456',
            'user_type': 'customer',
            'created_at': datetime.now().isoformat()
        }
        client_id = self.add_user(client)
        
        # Evento de exemplo
        event = {
            'name': 'Corrida da Cidade',
            'description': 'Corrida de 5km pela cidade',
            'date': datetime.now().date().isoformat(),
            'location': 'Centro da Cidade',
            'category': 'Corrida',
            'photographer_id': photographer_id,
            'created_at': datetime.now().isoformat()
        }
        event_id = self.add_event(event)
        
        # Fotos de exemplo (simuladas)
        sample_photos = [
            {
                'filename': 'sample_photo_1.jpg',
                'original_filename': 'foto1.jpg',
                'event_id': event_id,
                'photographer_id': photographer_id,
                'price': 0.0,
                'created_at': datetime.now().isoformat()
            },
            {
                'filename': 'sample_photo_2.jpg',
                'original_filename': 'foto2.jpg',
                'event_id': event_id,
                'photographer_id': photographer_id,
                'price': 0.0,
                'created_at': datetime.now().isoformat()
            },
            {
                'filename': 'sample_photo_3.jpg',
                'original_filename': 'foto3.jpg',
                'event_id': event_id,
                'photographer_id': photographer_id,
                'price': 0.0,
                'created_at': datetime.now().isoformat()
            }
        ]
        
        for photo_data in sample_photos:
            photo_id = self.add_photo(photo_data)
            
            # Análise simulada
            analysis = {
                'image_path': f'uploads/{photo_data["filename"]}',
                'processed_at': datetime.now().isoformat(),
                'faces_detected': 1,
                'faces': [{'x': 100, 'y': 100, 'width': 150, 'height': 150, 'confidence': 0.8}],
                'text_regions_detected': 0,
                'text_regions': [],
                'total_detections': 1
            }
            self.add_photo_analysis(photo_id, analysis)
        
        print(f"✅ Dados de exemplo criados:")
        print(f"   - Fotógrafo: {photographer['email']} / {photographer['password']}")
        print(f"   - Cliente: {client['email']} / {client['password']}")
        print(f"   - Evento: {event['name']}")
        print(f"   - Fotos: {len(sample_photos)} fotos de exemplo")
    
    def clear_data(self):
        """Limpa todos os dados"""
        self.data = {
            'users': {},
            'events': {},
            'photos': {},
            'photo_analyses': {},
            'next_user_id': 1,
            'next_event_id': 1,
            'next_photo_id': 1
        }
        self.save_data()
        print("🗑️ Todos os dados foram limpos")

# Instância global do gerenciador de dados
data_manager = DataManager() 