#!/usr/bin/env python3
"""
Script para testar a sessão do Flask
"""

from app_simple_fixed import app
import requests

def test_session():
    """Testa a sessão do Flask"""
    print("🔍 Testando sessão do Flask...")
    
    with app.test_client() as client:
        # Teste 1: Verificar sessão inicial
        print("\n📄 Teste 1: Verificando sessão inicial...")
        response = client.get('/')
        print(f"   Status: {response.status_code}")
        print(f"   Sessão inicial: {dict(response.cookies)}")
        
        # Teste 2: Acessar dashboard sem login
        print("\n📊 Teste 2: Acessando dashboard sem login...")
        response = client.get('/dashboard')
        print(f"   Status: {response.status_code}")
        print(f"   Redirecionado para: {response.location}")
        
        # Teste 3: Fazer login
        print("\n🔐 Teste 3: Fazendo login...")
        login_data = {
            'email': 'teste@teste.com',
            'password': '123456'
        }
        
        response = client.post('/login', data=login_data, follow_redirects=False)
        print(f"   Status: {response.status_code}")
        print(f"   Redirecionado para: {response.location}")
        print(f"   Cookies após login: {dict(response.cookies)}")
        
        # Teste 4: Acessar dashboard após login
        print("\n📊 Teste 4: Acessando dashboard após login...")
        response = client.get('/dashboard')
        print(f"   Status: {response.status_code}")
        print(f"   URL final: {response.request.url}")
        
        if response.status_code == 200:
            print("   ✅ Dashboard acessado com sucesso!")
            # Verificar se há conteúdo do dashboard
            if "Dashboard" in response.get_data(as_text=True):
                print("   ✅ Conteúdo do dashboard encontrado!")
            else:
                print("   ❌ Conteúdo do dashboard não encontrado")
        else:
            print("   ❌ Falha ao acessar dashboard")
        
        # Teste 5: Verificar logout
        print("\n🚪 Teste 5: Testando logout...")
        response = client.get('/logout', follow_redirects=False)
        print(f"   Status: {response.status_code}")
        print(f"   Redirecionado para: {response.location}")
        
        # Teste 6: Tentar acessar dashboard após logout
        print("\n📊 Teste 6: Tentando acessar dashboard após logout...")
        response = client.get('/dashboard')
        print(f"   Status: {response.status_code}")
        print(f"   Redirecionado para: {response.location}")
        
        if "login" in response.location:
            print("   ✅ Logout funcionou - redirecionado para login")
        else:
            print("   ❌ Logout não funcionou corretamente")
    
    print("\n✅ Teste de sessão concluído!")

if __name__ == "__main__":
    test_session() 