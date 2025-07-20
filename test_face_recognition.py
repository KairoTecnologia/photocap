#!/usr/bin/env python3
"""
Script de teste para o módulo de reconhecimento facial
"""

import os
import sys
from face_recognition_module import face_recognition

def test_face_detection():
    """Testa a detecção de faces"""
    print("=== TESTE DE DETECÇÃO DE FACES ===")
    
    # Verifica se existe a pasta uploads
    if not os.path.exists('uploads'):
        print("❌ Pasta 'uploads' não encontrada")
        return False
    
    # Lista arquivos de imagem na pasta uploads
    image_files = []
    for file in os.listdir('uploads'):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            image_files.append(file)
    
    if not image_files:
        print("❌ Nenhuma imagem encontrada na pasta 'uploads'")
        return False
    
    print(f"📁 Encontradas {len(image_files)} imagens para teste")
    
    # Testa detecção em cada imagem
    for i, filename in enumerate(image_files[:3]):  # Testa apenas as 3 primeiras
        filepath = os.path.join('uploads', filename)
        print(f"\n🔍 Testando {filename}...")
        
        faces = face_recognition.detect_faces(filepath)
        print(f"   Faces detectadas: {len(faces)}")
        
        if faces:
            for j, face in enumerate(faces):
                print(f"   Face {j+1}: x={face['x']}, y={face['y']}, w={face['width']}, h={face['height']}")
                
                # Testa extração de características
                features = face_recognition.extract_face_features(filepath, face)
                if features is not None:
                    print(f"   ✅ Características extraídas: {len(features)} valores")
                else:
                    print(f"   ❌ Falha na extração de características")
        else:
            print(f"   ⚠️ Nenhuma face detectada")
    
    return True

def test_face_comparison():
    """Testa a comparação de faces"""
    print("\n=== TESTE DE COMPARAÇÃO DE FACES ===")
    
    # Verifica se existe a pasta uploads
    if not os.path.exists('uploads'):
        print("❌ Pasta 'uploads' não encontrada")
        return False
    
    # Lista arquivos de imagem na pasta uploads
    image_files = []
    for file in os.listdir('uploads'):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            image_files.append(file)
    
    if len(image_files) < 2:
        print("❌ Precisa de pelo menos 2 imagens para teste de comparação")
        return False
    
    # Testa comparação entre as duas primeiras imagens
    file1 = os.path.join('uploads', image_files[0])
    file2 = os.path.join('uploads', image_files[1])
    
    print(f"🔍 Comparando {image_files[0]} com {image_files[1]}...")
    
    # Detecta faces nas duas imagens
    faces1 = face_recognition.detect_faces(file1)
    faces2 = face_recognition.detect_faces(file2)
    
    if not faces1:
        print(f"❌ Nenhuma face detectada em {image_files[0]}")
        return False
    
    if not faces2:
        print(f"❌ Nenhuma face detectada em {image_files[1]}")
        return False
    
    # Extrai características das primeiras faces
    features1 = face_recognition.extract_face_features(file1, faces1[0])
    features2 = face_recognition.extract_face_features(file2, faces2[0])
    
    if features1 is None:
        print(f"❌ Falha na extração de características de {image_files[0]}")
        return False
    
    if features2 is None:
        print(f"❌ Falha na extração de características de {image_files[1]}")
        return False
    
    # Compara as faces
    similarity = face_recognition.compare_faces(features1, features2)
    print(f"📊 Similaridade entre as faces: {similarity:.3f} ({similarity*100:.1f}%)")
    
    # Testa threshold
    threshold = face_recognition.similarity_threshold
    if similarity >= threshold:
        print(f"✅ Similaridade acima do threshold ({threshold:.3f}) - Faces consideradas similares")
    else:
        print(f"❌ Similaridade abaixo do threshold ({threshold:.3f}) - Faces consideradas diferentes")
    
    return True

def test_sample_data():
    """Testa com dados de exemplo"""
    print("\n=== TESTE COM DADOS DE EXEMPLO ===")
    
    # Cria dados de exemplo se não existirem
    try:
        from data_manager import data_manager
        if not data_manager.get_users():
            print("📝 Criando dados de exemplo...")
            data_manager.create_sample_data()
            print("✅ Dados de exemplo criados")
        else:
            print("✅ Dados já existem")
    except ImportError:
        print("⚠️ Módulo data_manager não disponível")
        return False
    
    # Lista eventos
    events = data_manager.get_events()
    print(f"📅 Eventos disponíveis: {len(events)}")
    
    for event_id, event in events.items():
        print(f"   - {event['name']} (ID: {event_id})")
    
    # Lista fotos
    photos = data_manager.get_photos()
    print(f"📸 Fotos disponíveis: {len(photos)}")
    
    for photo_id, photo in photos.items():
        print(f"   - {photo['original_filename']} (ID: {photo_id})")
    
    return True

def main():
    """Função principal"""
    print("🧪 TESTE DO MÓDULO DE RECONHECIMENTO FACIAL")
    print("=" * 50)
    
    # Testa se o módulo está disponível
    try:
        import cv2
        print("✅ OpenCV disponível")
    except ImportError:
        print("❌ OpenCV não disponível")
        return
    
    try:
        import numpy as np
        print("✅ NumPy disponível")
    except ImportError:
        print("❌ NumPy não disponível")
        return
    
    # Executa testes
    test_face_detection()
    test_face_comparison()
    test_sample_data()
    
    print("\n" + "=" * 50)
    print("🏁 TESTES CONCLUÍDOS")

if __name__ == "__main__":
    main() 