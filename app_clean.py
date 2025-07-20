from flask import Flask, request, render_template_string, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import traceback

# Importa o módulo de reconhecimento facial simplificado
try:
    from face_recognition_simple import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    print("✅ Módulo de reconhecimento facial carregado")
except ImportError as e:
    FACE_RECOGNITION_AVAILABLE = False
    print(f"⚠️ Módulo de reconhecimento facial não disponível: {e}")

# Importa o gerenciador de dados
try:
    from data_manager import data_manager
    print("✅ Gerenciador de dados carregado")
except ImportError as e:
    print(f"⚠️ Gerenciador de dados não disponível: {e}")
    data_manager = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Extensões permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_date(date_value):
    """Formata uma data para exibição"""
    if isinstance(date_value, str):
        try:
            dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y')
        except:
            return date_value
    elif hasattr(date_value, 'strftime'):
        return date_value.strftime('%d/%m/%Y')
    else:
        return str(date_value)

def get_base_html(title, content):
    """Template HTML base com Bootstrap 5"""
    return f'''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; }}
            .navbar-brand {{ font-weight: bold; }}
            .card {{ border: none; box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); }}
            .btn {{ border-radius: 0.5rem; }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">
                    <i class="fas fa-camera"></i> PhotoCap
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav me-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="/">Início</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/search">Buscar Fotos</a>
                        </li>
                    </ul>
                    <ul class="navbar-nav">
                        {f'''
                        <li class="nav-item">
                            <a class="nav-link" href="/dashboard">Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/logout">Sair</a>
                        </li>
                        ''' if session.get('user_id') else '''
                        <li class="nav-item">
                            <a class="nav-link" href="/login">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/register">Cadastro</a>
                        </li>
                        '''}
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            {content}
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

@app.route('/')
def index():
    """Página inicial"""
    if data_manager:
        events_data = data_manager.get_events()
        recent_events = list(events_data.values())[-6:] if events_data else []
    else:
        recent_events = []
    
    events_html = ""
    for event in recent_events:
        events_html += f'''
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">{event['name']}</h5>
                    <p class="card-text">
                        <i class="fas fa-calendar"></i> {format_date(event['date'])}<br>
                        <i class="fas fa-map-marker-alt"></i> {event.get('location', 'Local não informado')}
                    </p>
                    <a href="/event/{event['id']}" class="btn btn-primary">Ver Fotos</a>
                </div>
            </div>
        </div>
        '''
    
    content = f'''
    <div class="row">
        <div class="col-lg-6">
            <h1 class="display-4 fw-bold mb-4">
                Participou de um evento?<br>
                <span class="text-warning">Busque aqui suas fotos!</span>
            </h1>
            <p class="lead mb-4">
                Encontre suas fotos de eventos esportivos, festas, casamentos e muito mais.
            </p>
            <form action="/search" method="GET" class="mb-4">
                <div class="input-group">
                    <input type="text" name="event_name" class="form-control" placeholder="Digite o nome do evento...">
                    <button class="btn btn-warning" type="submit">
                        <i class="fas fa-search"></i> Buscar
                    </button>
                </div>
            </form>
        </div>
        <div class="col-lg-6 text-center">
            <img src="https://via.placeholder.com/500x400/ff6b35/ffffff?text=PhotoCap" class="img-fluid rounded">
        </div>
    </div>
    
    <div class="row mt-5">
        <div class="col-12">
            <h2 class="text-center mb-4">Eventos Recentes</h2>
            <div class="row">
                {events_html if events_html else '<div class="col-12 text-center"><p>Nenhum evento disponível ainda.</p></div>'}
            </div>
        </div>
    </div>
    '''
    
    return get_base_html("PhotoCap - Suas fotos de eventos", content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if data_manager:
            users_data = data_manager.get_users()
            user = None
            for u in users_data.values():
                if u['email'] == email and u['password'] == password:
                    user = u
                    break
            
            if user:
                session['user_id'] = user['id']
                flash('Login realizado com sucesso!')
                return redirect(url_for('dashboard'))
            else:
                flash('Email ou senha inválidos')
        else:
            flash('Sistema de dados não disponível')
    
    content = '''
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
            <div class="card border-0 shadow">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <h2 class="fw-bold text-primary">
                            <i class="fas fa-camera"></i> PhotoCap
                        </h2>
                        <p class="text-muted">Faça login na sua conta</p>
                    </div>
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Senha</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-sign-in-alt"></i> Entrar
                            </button>
                        </div>
                    </form>
                    
                    <hr class="my-4">
                    
                    <div class="text-center">
                        <p class="mb-0">Não tem uma conta?</p>
                        <a href="/register" class="btn btn-outline-primary">Criar Conta</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return get_base_html("Login - PhotoCap", content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        if data_manager:
            users_data = data_manager.get_users()
            for user in users_data.values():
                if user['email'] == email:
                    flash('Email já cadastrado')
                    return redirect(url_for('register'))
            
            user = {
                'username': username,
                'email': email,
                'password': password,
                'user_type': user_type,
                'created_at': datetime.now()
            }
            
            user_id = data_manager.add_user(user)
            flash('Conta criada com sucesso!')
            return redirect(url_for('login'))
        else:
            flash('Sistema de dados não disponível')
    
    content = '''
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <div class="card border-0 shadow">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <h2 class="fw-bold text-primary">
                            <i class="fas fa-camera"></i> PhotoCap
                        </h2>
                        <p class="text-muted">Crie sua conta</p>
                    </div>
                    
                    <form method="POST">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="username" class="form-label">Nome de usuário</label>
                                    <input type="text" class="form-control" id="username" name="username" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email</label>
                                    <input type="email" class="form-control" id="email" name="email" required>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Senha</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        
                        <div class="mb-4">
                            <label class="form-label">Tipo de conta</label>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="user_type" id="customer" value="customer" checked>
                                        <label class="form-check-label" for="customer">
                                            <i class="fas fa-user"></i> Cliente
                                        </label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="user_type" id="photographer" value="photographer">
                                        <label class="form-check-label" for="photographer">
                                            <i class="fas fa-camera"></i> Fotógrafo
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-user-plus"></i> Criar Conta
                            </button>
                        </div>
                    </form>
                    
                    <hr class="my-4">
                    
                    <div class="text-center">
                        <p class="mb-0">Já tem uma conta?</p>
                        <a href="/login" class="btn btn-outline-primary">Fazer Login</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return get_base_html("Cadastro - PhotoCap", content)

@app.route('/dashboard')
def dashboard():
    """Dashboard do usuário"""
    user_id = session.get('user_id')
    if not user_id or not data_manager:
        flash('Faça login para acessar o dashboard')
        return redirect(url_for('login'))
    
    users_data = data_manager.get_users()
    if user_id not in users_data:
        flash('Usuário não encontrado')
        return redirect(url_for('login'))
    
    user = users_data[user_id]
    if user['user_type'] == 'photographer':
        events_data = data_manager.get_events()
        user_events = [e for e in events_data.values() if e['photographer_id'] == user_id]
        
        events_html = ""
        for event in user_events:
            events_html += f'''
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <h6 class="card-title">{event['name']}</h6>
                        <p class="card-text text-muted">
                            <small>
                                <i class="fas fa-calendar"></i> {format_date(event['date'])}<br>
                                <i class="fas fa-map-marker-alt"></i> {event.get('location', 'Local não informado')}
                            </small>
                        </p>
                        <a href="/event/{event['id']}" class="btn btn-outline-primary btn-sm">Ver Evento</a>
                    </div>
                </div>
            </div>
            '''
        
        content = f'''
        <h1 class="mb-4"><i class="fas fa-camera"></i> Dashboard do Fotógrafo</h1>
        
        <div class="row mb-4">
            <div class="col-md-4">
                <a href="/create_event" class="btn btn-primary btn-lg w-100 mb-3">
                    <i class="fas fa-plus"></i> Criar Novo Evento
                </a>
            </div>
            <div class="col-md-4">
                <a href="/upload_photos" class="btn btn-success btn-lg w-100 mb-3">
                    <i class="fas fa-upload"></i> Enviar Fotos
                </a>
            </div>
            <div class="col-md-4">
                <a href="/register_face" class="btn btn-info btn-lg w-100 mb-3">
                    <i class="fas fa-user-plus"></i> Registrar Face
                </a>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-calendar"></i> Meus Eventos</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {events_html if events_html else '<div class="col-12 text-center"><p>Nenhum evento criado ainda.</p><a href="/create_event" class="btn btn-primary">Criar Primeiro Evento</a></div>'}
                </div>
            </div>
        </div>
        '''
    else:
        content = f'''
        <h1 class="mb-4"><i class="fas fa-user"></i> Minha Conta</h1>
        <p>Bem-vindo, {user['username']}!</p>
        <a href="/search" class="btn btn-primary">Buscar Fotos</a>
        '''
    
    return get_base_html("Dashboard - PhotoCap", content)

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.pop('user_id', None)
    flash('Logout realizado com sucesso!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Cria pasta uploads se não existir
    os.makedirs('uploads', exist_ok=True)
    
    print("🚀 Iniciando PhotoCap...")
    print("📁 Pasta uploads criada/verificada")
    print("🔧 Configurações carregadas")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 