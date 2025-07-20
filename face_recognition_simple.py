import cv2
import numpy as np
import os
from datetime import datetime

class SimpleFaceRecognition:
    def __init__(self):
        """Inicializa o módulo de reconhecimento facial simplificado"""
        # Carrega o classificador de faces do OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Threshold para similaridade (mais restritivo)
        self.similarity_threshold = 0.7
        
        print("✅ Módulo de reconhecimento facial simplificado carregado")
    
    def detect_faces(self, image_path):
        """
        Detecta faces em uma imagem - versão simplificada e precisa
        """
        try:
            # Carrega a imagem
            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ Não foi possível carregar a imagem: {image_path}")
                return []
            
            # Converte para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detecta faces com parâmetros conservadores
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=10,  # Mais restritivo
                minSize=(80, 80),  # Faces maiores
                maxSize=(500, 500)
            )
            
            print(f"🔍 Detectadas {len(faces)} faces na imagem")
            
            # Converte para formato amigável
            face_locations = []
            for (x, y, w, h) in faces:
                # Filtra faces muito pequenas
                if w * h < 6400:  # Mínimo 80x80 pixels
                    continue
                    
                face_locations.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'confidence': 0.95
                })
            
            print(f"✅ {len(face_locations)} faces válidas após filtro")
            return face_locations
            
        except Exception as e:
            print(f"❌ Erro ao detectar faces: {e}")
            return []
    
    def extract_face_features(self, image_path, face_location):
        """
        Extrai características simples de uma face
        """
        try:
            # Carrega a imagem
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Extrai a região da face
            x, y, w, h = face_location['x'], face_location['y'], face_location['width'], face_location['height']
            face_region = image[y:y+h, x:x+w]
            
            # Redimensiona para tamanho padrão
            face_region = cv2.resize(face_region, (64, 64))
            
            # Converte para escala de cinza
            face_gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Normaliza
            face_gray = face_gray.astype(np.float32) / 255.0
            
            # Extrai características simples
            features = []
            
            # 1. Características básicas
            features.extend([
                face_gray.mean(),
                face_gray.std(),
                face_gray.min(),
                face_gray.max()
            ])
            
            # 2. Histograma simplificado
            hist, _ = np.histogram(face_gray, bins=16, range=(0, 1))
            hist = hist / (hist.sum() + 1e-7)
            features.extend(hist)
            
            # 3. Características de bordas
            edges = cv2.Canny((face_gray * 255).astype(np.uint8), 50, 150)
            features.extend([
                edges.mean(),
                edges.std(),
                (edges > 0).sum() / edges.size
            ])
            
            # 4. Gradientes
            gx = cv2.Sobel(face_gray, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(face_gray, cv2.CV_32F, 0, 1, ksize=3)
            magnitude = np.sqrt(gx**2 + gy**2)
            
            features.extend([
                gx.mean(), gx.std(),
                gy.mean(), gy.std(),
                magnitude.mean(), magnitude.std()
            ])
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            print(f"❌ Erro ao extrair características: {e}")
            return None
    
    def compare_faces(self, face1_features, face2_features):
        """
        Compara duas faces e retorna a similaridade
        """
        if face1_features is None or face2_features is None:
            return 0.0
        
        try:
            # Converte para arrays
            f1 = np.array(face1_features).flatten()
            f2 = np.array(face2_features).flatten()
            
            # Garante mesmo tamanho
            min_len = min(len(f1), len(f2))
            f1 = f1[:min_len]
            f2 = f2[:min_len]
            
            # Calcula similaridade cosseno
            dot_product = np.dot(f1, f2)
            norm_f1 = np.linalg.norm(f1)
            norm_f2 = np.linalg.norm(f2)
            
            if norm_f1 > 0 and norm_f2 > 0:
                similarity = dot_product / (norm_f1 * norm_f2)
                print(f"🔍 Similaridade calculada: {similarity:.3f}")
                return max(0, similarity)
            else:
                return 0.0
                
        except Exception as e:
            print(f"❌ Erro ao comparar faces: {e}")
            return 0.0
    
    def process_image(self, image_path):
        """
        Processa uma imagem detectando faces
        """
        try:
            # Detecta faces
            faces = self.detect_faces(image_path)
            
            # Cria resultado
            result = {
                'image_path': image_path,
                'processed_at': datetime.now().isoformat(),
                'faces_detected': len(faces),
                'faces': faces,
                'text_regions_detected': 0,
                'text_regions': [],
                'total_detections': len(faces)
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Erro ao processar imagem: {e}")
            return {
                'image_path': image_path,
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
    
    def save_processed_image(self, image_path, output_path, detections):
        """
        Salva uma versão da imagem com as detecções marcadas
        """
        try:
            # Carrega a imagem original
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Desenha retângulos ao redor das faces
            for face in detections.get('faces', []):
                x, y, w, h = face['x'], face['y'], face['width'], face['height']
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, 'Face', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Salva a imagem processada
            cv2.imwrite(output_path, image)
            print(f"✅ Imagem processada salva: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar imagem processada: {e}")
            return False
    
    def get_statistics(self):
        """
        Retorna estatísticas do módulo
        """
        return {
            'known_faces_count': 0,
            'users_with_faces': 0,
            'total_registered_faces': 0
        }

# Instância global do módulo simplificado
face_recognition = SimpleFaceRecognition() 