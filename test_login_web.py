#!/usr/bin/env python3
"""
Script para testar o login via web
"""

import requests
from bs4 import BeautifulSoup

def test_login():
    """Testa o login via web"""
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("🌐 Testando login via web...")
    
    # Teste 1: Acessar página inicial
    print("\n📄 Teste 1: Acessando página inicial...")
    response = session.get(f"{base_url}/")
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    
    # Teste 2: Acessar página de login
    print("\n🔐 Teste 2: Acessando página de login...")
    response = session.get(f"{base_url}/login")
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    
    # Teste 3: Tentar fazer login
    print("\n📝 Teste 3: Tentando fazer login...")
    login_data = {
        'email': 'teste@teste.com',
        'password': '123456'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    print(f"   Redirecionado para: {response.url}")
    
    # Teste 4: Acessar dashboard
    print("\n📊 Teste 4: Acessando dashboard...")
    response = session.get(f"{base_url}/dashboard")
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    
    if "dashboard" in response.url.lower():
        print("   ✅ Dashboard acessado com sucesso!")
        
        # Verificar se há conteúdo do dashboard
        soup = BeautifulSoup(response.text, 'html.parser')
        dashboard_title = soup.find('h1')
        if dashboard_title:
            print(f"   📋 Título da página: {dashboard_title.text.strip()}")
    else:
        print("   ❌ Falha ao acessar dashboard")
        print(f"   🔍 Redirecionado para: {response.url}")
    
    # Teste 5: Verificar cookies da sessão
    print("\n🍪 Teste 5: Verificando cookies da sessão...")
    cookies = session.cookies
    print(f"   Cookies: {dict(cookies)}")
    
    print("\n✅ Teste de login via web concluído!")

if __name__ == "__main__":
    test_login() 