from flask import Blueprint, render_template, redirect, url_for, session, flash
from db_manager import DatabaseManager
from datetime import datetime

bp = Blueprint('dashboard', __name__)

# Inicializar o gerenciador de dados
data_manager = DatabaseManager()

def format_date(date_value):
    """Formata uma data para exibição"""
    if isinstance(date_value, str):
        try:
            date_obj = datetime.strptime(date_value, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except:
            return date_value
    elif hasattr(date_value, 'strftime'):
        return date_value.strftime('%d/%m/%Y')
    return str(date_value)

@bp.route('/')
def index():
    """Página inicial"""
    if data_manager:
        events_data = data_manager.get_events()
        recent_events = events_data[-6:] if events_data else []
    else:
        recent_events = []
    
    return render_template('dashboard/index.html', events=recent_events, format_date=format_date)

@bp.route('/area_fotografo')
def area_fotografo():
    """Área do usuário"""
    print(f"🔍 Área do Fotógrafo acessado - session: {session}")
    print(f"🔍 Session permanent: {session.permanent}")
    print(f"🔍 Session modified: {session.modified}")
    
    user_id = session.get('user_id')
    username = session.get('username')
    email = session.get('email')
    user_type = session.get('user_type', 'customer')
    
    print(f"🔍 User ID da sessão: {user_id}")
    print(f"🔍 Username da sessão: {username}")
    print(f"🔍 User Type da sessão: {user_type}")
    print(f"🔍 Data manager disponível: {data_manager is not None}")
    
    if not user_id:
        print("❌ Nenhum user_id na sessão - redirecionando para login")
        return redirect(url_for('auth.login'))
    
    if not data_manager:
        print("❌ Data manager não disponível - redirecionando para login")
        return redirect(url_for('auth.login'))
    
    # Se temos username na sessão, usamos ele diretamente
    if username:
        print(f"✅ Usando username da sessão: {username}")
        user = {
            'UserId': user_id,
            'Username': username,
            'Email': email,
            'UserType': user_type
        }
    else:
        # Busca no banco como fallback
        users_data = data_manager.get_users()
        print(f"🔍 Total de usuários no banco: {len(users_data)}")
        
        user = None
        for u in users_data:
            if u['UserId'] == user_id:
                user = u
                break
        
        if not user:
            print(f"❌ Usuário com ID {user_id} não encontrado no banco - redirecionando para login")
            return redirect(url_for('auth.login'))
    
    print(f"✅ Usuário encontrado: {user['Username']} (Tipo: {user['UserType']})")
    
    # Verifica se é fotógrafo ou cliente
    if user['UserType'] == 'photographer':
        # Conteúdo para fotógrafos
        events_data = data_manager.get_events()
        user_events = events_data
        
        return render_template('dashboard/area_fotografo.html', 
                             user=user, 
                             events=user_events, 
                             format_date=format_date)
    else:
        # Conteúdo para clientes
        return render_template('dashboard/minha_conta.html', 
                             user=user) 