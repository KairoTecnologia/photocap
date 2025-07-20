import cv2
import numpy as np
import os
from datetime import datetime
import json

class FaceRecognitionModule:
    def __init__(self):
        """Inicializa o módulo de reconhecimento facial"""
        # Carrega o classificador de faces do OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Carrega o classificador de olhos para melhor detecção
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Parâmetros para detecção de texto (números de peito)
        self.text_params = {
            'min_area': 100,
            'min_width': 20,
            'min_height': 10
        }
        
        # Dados de faces conhecidas (simulado)
        self.known_faces = {}
        self.face_encodings = {}
        
        # Parâmetros para comparação de faces - Ajustado para ser mais preciso
        self.similarity_threshold = 0.6  # Aumentado para ser mais restritivo
        
    def extract_face_features(self, image_path, face_location):
        """
        Extrai características de uma face específica - versão melhorada
        """
        try:
            # Carrega a imagem
            image = cv2.imread(image_path)
            if image is None:
                print(f"DEBUG: Não foi possível carregar a imagem: {image_path}")
                return None
            
            # Extrai a região da face
            x, y, w, h = face_location['x'], face_location['y'], face_location['width'], face_location['height']
            face_region = image[y:y+h, x:x+w]
            
            # Redimensiona para tamanho padrão maior para mais detalhes
            face_region = cv2.resize(face_region, (128, 128))
            
            # Converte para escala de cinza
            face_gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Normaliza a imagem
            face_gray = face_gray.astype(np.float32) / 255.0
            
            # Extrai características mais robustas
            features = []
            
            # 1. Características básicas da imagem
            features.extend([
                face_gray.mean(),
                face_gray.std(),
                face_gray.min(),
                face_gray.max(),
                np.percentile(face_gray, 25),
                np.percentile(face_gray, 50),
                np.percentile(face_gray, 75)
            ])
            
            # 2. Histograma mais detalhado (32 bins)
            hist, _ = np.histogram(face_gray, bins=32, range=(0, 1))
            hist = hist / (hist.sum() + 1e-7)
            features.extend(hist)
            
            # 3. Características de bordas
            edges = cv2.Canny((face_gray * 255).astype(np.uint8), 50, 150)
            features.extend([
                edges.mean(),
                edges.std(),
                (edges > 0).sum() / edges.size,  # Densidade de bordas
                np.percentile(edges, 50),
                np.percentile(edges, 75)
            ])
            
            # 4. Características de textura mais detalhadas
            # Calcula gradientes
            gx = cv2.Sobel(face_gray, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(face_gray, cv2.CV_32F, 0, 1, ksize=3)
            magnitude = np.sqrt(gx**2 + gy**2)
            direction = np.arctan2(gy, gx)
            
            features.extend([
                gx.mean(), gx.std(), np.percentile(gx, 50), np.percentile(gx, 75),
                gy.mean(), gy.std(), np.percentile(gy, 50), np.percentile(gy, 75),
                magnitude.mean(), magnitude.std(), np.percentile(magnitude, 50), np.percentile(magnitude, 75),
                direction.mean(), direction.std()
            ])
            
            # 5. Características de forma (momentos)
            moments = cv2.moments((face_gray * 255).astype(np.uint8))
            if moments['m00'] != 0:
                features.extend([
                    moments['m10'] / moments['m00'],  # Centroide X
                    moments['m01'] / moments['m00'],  # Centroide Y
                    moments['mu20'] / moments['m00'],  # Variância X
                    moments['mu02'] / moments['m00'],  # Variância Y
                    moments['mu11'] / moments['m00']   # Covariância
                ])
            else:
                features.extend([0, 0, 0, 0, 0])
            
            # 6. Características de frequência (FFT simplificada)
            f_transform = np.fft.fft2(face_gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            
            # Extrai características do espectro de frequência
            features.extend([
                magnitude_spectrum.mean(),
                magnitude_spectrum.std(),
                np.percentile(magnitude_spectrum, 50),
                np.percentile(magnitude_spectrum, 75)
            ])
            
            # 7. Características de cor (se disponível)
            if len(face_region.shape) == 3:
                # Converte para HSV
                hsv = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(hsv)
                
                features.extend([
                    h.mean(), h.std(),
                    s.mean(), s.std(),
                    v.mean(), v.std()
                ])
            else:
                features.extend([0, 0, 0, 0, 0, 0])
            
            features = np.array(features, dtype=np.float32)
            print(f"DEBUG: Extraídas {len(features)} características da face")
            return features
            
        except Exception as e:
            print(f"Erro ao extrair características da face: {e}")
            return None
    
    def compare_faces(self, face1_features, face2_features):
        """
        Compara duas faces e retorna a similaridade - versão melhorada
        """
        if face1_features is None or face2_features is None:
            print("DEBUG: Uma das faces não tem características válidas")
            return 0.0
        
        try:
            # Converte para arrays numpy se necessário
            f1 = np.array(face1_features).flatten()
            f2 = np.array(face2_features).flatten()
            
            # Garante que têm o mesmo tamanho
            min_len = min(len(f1), len(f2))
            f1 = f1[:min_len]
            f2 = f2[:min_len]
            
            print(f"DEBUG: Comparando faces com {min_len} características")
            
            # Calcula similaridade usando múltiplas métricas
            similarities = []
            
            # 1. Correlação de Pearson
            if len(f1) > 1 and len(f2) > 1:
                try:
                    correlation = np.corrcoef(f1, f2)[0, 1]
                    if not np.isnan(correlation):
                        similarities.append(max(0, correlation))
                        print(f"DEBUG: Correlação Pearson: {correlation:.3f}")
                except Exception as e:
                    print(f"DEBUG: Erro na correlação Pearson: {e}")
            
            # 2. Distância euclidiana normalizada
            try:
                distance = np.linalg.norm(f1 - f2)
                max_distance = np.linalg.norm(f1) + np.linalg.norm(f2)
                if max_distance > 0:
                    euclidean_sim = 1.0 - (distance / max_distance)
                    similarities.append(max(0, euclidean_sim))
                    print(f"DEBUG: Similaridade Euclidiana: {euclidean_sim:.3f}")
            except Exception as e:
                print(f"DEBUG: Erro na similaridade euclidiana: {e}")
            
            # 3. Similaridade cosseno
            try:
                dot_product = np.dot(f1, f2)
                norm_f1 = np.linalg.norm(f1)
                norm_f2 = np.linalg.norm(f2)
                if norm_f1 > 0 and norm_f2 > 0:
                    cosine_sim = dot_product / (norm_f1 * norm_f2)
                    similarities.append(max(0, cosine_sim))
                    print(f"DEBUG: Similaridade Cosseno: {cosine_sim:.3f}")
            except Exception as e:
                print(f"DEBUG: Erro na similaridade cosseno: {e}")
            
            # 4. Similaridade baseada na diferença média
            try:
                mean_diff = np.mean(np.abs(f1 - f2))
                max_val = max(np.max(f1), np.max(f2))
                if max_val > 0:
                    diff_sim = 1.0 - (mean_diff / max_val)
                    similarities.append(max(0, diff_sim))
                    print(f"DEBUG: Similaridade Diferença: {diff_sim:.3f}")
            except Exception as e:
                print(f"DEBUG: Erro na similaridade diferença: {e}")
            
            # 5. Similaridade baseada na distância de Manhattan
            try:
                manhattan_dist = np.sum(np.abs(f1 - f2))
                max_manhattan = np.sum(np.abs(f1)) + np.sum(np.abs(f2))
                if max_manhattan > 0:
                    manhattan_sim = 1.0 - (manhattan_dist / max_manhattan)
                    similarities.append(max(0, manhattan_sim))
                    print(f"DEBUG: Similaridade Manhattan: {manhattan_sim:.3f}")
            except Exception as e:
                print(f"DEBUG: Erro na similaridade Manhattan: {e}")
            
            # Retorna a média das similaridades calculadas
            if similarities:
                final_similarity = np.mean(similarities)
                print(f"DEBUG: Similaridades calculadas: {[f'{s:.3f}' for s in similarities]}")
                print(f"DEBUG: Similaridade final: {final_similarity:.3f}")
                return final_similarity
            else:
                print("DEBUG: Nenhuma similaridade válida calculada")
                return 0.0
            
        except Exception as e:
            print(f"Erro ao comparar faces: {e}")
            return 0.0
    
    def detect_faces(self, image_path):
        """
        Detecta faces em uma imagem - versão mais precisa
        Retorna: lista de coordenadas das faces detectadas
        """
        try:
            # Carrega a imagem
            image = cv2.imread(image_path)
            if image is None:
                print(f"DEBUG: Não foi possível carregar a imagem: {image_path}")
                return []
            
            # Converte para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Aplica equalização de histograma para melhorar contraste
            gray = cv2.equalizeHist(gray)
            
            # Detecta faces com parâmetros mais restritivos para evitar falsos positivos
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,     # Menos sensível para evitar falsos positivos
                minNeighbors=8,      # Mais restritivo (era 3)
                minSize=(50, 50),    # Faces maiores (era 20, 20)
                maxSize=(400, 400)   # Faces maiores
            )
            
            print(f"DEBUG: Detectadas {len(faces)} faces na imagem")
            
            # Filtra faces muito pequenas ou muito próximas
            filtered_faces = []
            for (x, y, w, h) in faces:
                # Calcula a área da face
                area = w * h
                
                # Filtra faces muito pequenas (menos de 2500 pixels)
                if area < 2500:
                    continue
                
                # Verifica se não há faces muito próximas
                too_close = False
                for (fx, fy, fw, fh) in filtered_faces:
                    # Calcula a distância entre os centros
                    center_x = x + w/2
                    center_y = y + h/2
                    f_center_x = fx + fw/2
                    f_center_y = fy + fh/2
                    
                    distance = ((center_x - f_center_x)**2 + (center_y - f_center_y)**2)**0.5
                    
                    # Se as faces estão muito próximas, ignora a menor
                    if distance < min(w, h) * 0.5:
                        if area < fw * fh:
                            too_close = True
                            break
                        else:
                            # Remove a face menor
                            filtered_faces.remove((fx, fy, fw, fh))
                
                if not too_close:
                    filtered_faces.append((x, y, w, h))
            
            print(f"DEBUG: Após filtro: {len(filtered_faces)} faces válidas")
            
            # Converte para formato mais amigável
            face_locations = []
            for (x, y, w, h) in filtered_faces:
                face_locations.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'confidence': 0.95  # Confiança alta
                })
            
            return face_locations
            
        except Exception as e:
            print(f"Erro ao detectar faces: {e}")
            return []
    
    def detect_text_regions(self, image_path):
        """
        Detecta regiões que podem conter texto (números de peito)
        Retorna: lista de coordenadas das regiões de texto
        """
        try:
            # Carrega a imagem
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            # Converte para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Aplica filtros para melhorar a detecção de texto
            # Filtro de suavização
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detecção de bordas
            edges = cv2.Canny(blurred, 50, 150)
            
            # Encontra contornos
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = []
            for contour in contours:
                # Calcula a área do contorno
                area = cv2.contourArea(contour)
                
                if area > self.text_params['min_area']:
                    # Obtém o retângulo delimitador
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Filtra por tamanho mínimo
                    if w > self.text_params['min_width'] and h > self.text_params['min_height']:
                        # Calcula a razão largura/altura para filtrar textos
                        aspect_ratio = w / h
                        if 0.5 < aspect_ratio < 10:  # Texto geralmente tem essa proporção
                            text_regions.append({
                                'x': int(x),
                                'y': int(y),
                                'width': int(w),
                                'height': int(h),
                                'area': int(area),
                                'confidence': 0.6  # Confiança simulada
                            })
            
            return text_regions
            
        except Exception as e:
            print(f"Erro ao detectar regiões de texto: {e}")
            return []
    
    def process_image(self, image_path):
        """
        Processa uma imagem completa, detectando faces e regiões de texto
        Retorna: dicionário com resultados da análise
        """
        try:
            # Detecta faces
            faces = self.detect_faces(image_path)
            
            # Detecta regiões de texto
            text_regions = self.detect_text_regions(image_path)
            
            # Extrai características das faces detectadas (mas não salva no JSON)
            face_features = []
            for face in faces:
                # Cria uma cópia da face sem as características para salvar no JSON
                face_info = {
                    'x': face['x'],
                    'y': face['y'],
                    'width': face['width'],
                    'height': face['height'],
                    'confidence': face['confidence']
                }
                face_features.append(face_info)
            
            # Cria resultado
            result = {
                'image_path': image_path,
                'processed_at': datetime.now().isoformat(),
                'faces_detected': len(faces),
                'faces': face_features,  # Apenas informações básicas
                'text_regions_detected': len(text_regions),
                'text_regions': text_regions,
                'total_detections': len(faces) + len(text_regions)
            }
            
            return result
            
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")
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
            
            # Desenha retângulos ao redor das regiões de texto
            for text_region in detections.get('text_regions', []):
                x, y, w, h = text_region['x'], text_region['y'], text_region['width'], text_region['height']
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(image, 'Text', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Salva a imagem processada
            cv2.imwrite(output_path, image)
            return True
            
        except Exception as e:
            print(f"Erro ao salvar imagem processada: {e}")
            return False
    
    def register_face(self, user_id, image_path, face_location):
        """
        Registra uma face conhecida para um usuário
        """
        try:
            # Extrai características da face
            features = self.extract_face_features(image_path, face_location)
            if features is None:
                return False
            
            # Salva a face como arquivo
            face_filename = f"face_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            face_path = os.path.join('uploads', 'faces', face_filename)
            
            # Cria diretório se não existir
            os.makedirs(os.path.dirname(face_path), exist_ok=True)
            
            # Salva a imagem da face
            image = cv2.imread(image_path)
            x, y, w, h = face_location['x'], face_location['y'], face_location['width'], face_location['height']
            face_region = image[y:y+h, x:x+w]
            cv2.imwrite(face_path, face_region)
            
            # Armazena informações da face
            if user_id not in self.known_faces:
                self.known_faces[user_id] = []
            
            face_info = {
                'face_path': face_path,
                'features': features,
                'registered_at': datetime.now().isoformat(),
                'location': face_location
            }
            
            self.known_faces[user_id].append(face_info)
            
            return True
            
        except Exception as e:
            print(f"Erro ao registrar face: {e}")
            return False
    
    def get_statistics(self):
        """
        Retorna estatísticas do módulo
        """
        return {
            'known_faces_count': sum(len(faces) for faces in self.known_faces.values()),
            'users_with_faces': len(self.known_faces),
            'total_registered_faces': len(self.face_encodings)
        }

# Instância global do módulo
face_recognition = FaceRecognitionModule() 