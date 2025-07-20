#!/usr/bin/env python3
"""
PhotoCap - Sistema de Reconhecimento Facial com SQL Server
Aplicação Flask para gerenciamento de fotos de eventos
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from config import APP_CONFIG, FACE_RECOGNITION_CONFIG
from db_manager import DatabaseManager

# Inicialização da aplicação Flask
app = Flask(__name__)
app.secret_key = APP_CONFIG['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = APP_CONFIG['UPLOAD_FOLDER']
app.config['MAX_CONTENT_LENGTH'] = APP_CONFIG['MAX_CONTENT_LENGTH']

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar gerenciador de banco de dados
try:
    db = DatabaseManager()
    print("✅ Gerenciador de banco de dados inicializado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao inicializar banco de dados: {e}")
    db = None

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in APP_CONFIG['ALLOWED_EXTENSIONS']

def format_date(date_str):
    """Formata uma data para exibição"""
    try:
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date_obj = date_str
        return date_obj.strftime('%d/%m/%Y')
    except:
        return str(date_str)

def get_base_html(title, content, messages=None):
    """Retorna o HTML base da aplicação"""
    if messages is None:
        messages = []
    
    flash_messages = ""
    for message in messages:
        flash_messages += f'<div class="alert alert-info">{message}</div>'
    
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .navbar-brand {{ font-weight: bold; }}
            .card {{ box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); }}
            .btn {{ border-radius: 0.375rem; }}
        </style>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">
                    <i class="fas fa-camera"></i> PhotoCap
                </a>
                <div class="navbar-nav ms-auto">
                    {f'''
                    <span class="navbar-text me-3">
                        <i class="fas fa-user"></i> {session.get('username', 'Usuário')}
                    </span>
                    <a class="nav-link" href="/logout">
                        <i class="fas fa-sign-out-alt"></i> Sair
                    </a>
                    ''' if session.get('user_id') else '''
                    <a class="nav-link" href="/login">
                        <i class="fas fa-sign-in-alt"></i> Entrar
                    </a>
                    <a class="nav-link" href="/register">
                        <i class="fas fa-user-plus"></i> Cadastrar
                    </a>
                    '''}
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            {flash_messages}
            {content}
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

# Rotas da aplicação
@app.route('/')
def index():
    """Página inicial"""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    # Buscar eventos recentes para mostrar na página inicial
    recent_events = []
    if db:
        recent_events = db.get_all_events()[:6]  # Últimos 6 eventos
    
    events_html = ""
    for event in recent_events:
        photos = db.get_photos_by_event(event['EventId']) if db else []
        events_html += f'''
        <div class="col-lg-4 col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <div class="feature-icon">
                        <i class="fas fa-calendar"></i>
                    </div>
                    <h5 class="card-title">{event['Name']}</h5>
                    <p class="card-text text-muted">
                        <i class="fas fa-calendar-alt"></i> {format_date(event['Date'])}<br>
                        <i class="fas fa-images"></i> {len(photos)} foto(s)
                    </p>
                    <a href="/event/{event['EventId']}" class="btn btn-primary">
                        <i class="fas fa-eye"></i> Ver Fotos
                    </a>
                </div>
            </div>
        </div>
        '''
    
    content = f'''
    <div class="row">
        <div class="col-12">
            <h1 class="mb-4"><i class="fas fa-home"></i> Bem-vindo ao PhotoCap</h1>
            
            <div class="row">
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-calendar-plus fa-3x text-primary mb-3"></i>
                            <h5 class="card-title">Criar Evento</h5>
                            <p class="card-text">Crie um novo evento para organizar suas fotos.</p>
                            <a href="/create_event" class="btn btn-primary">
                                <i class="fas fa-plus"></i> Criar Evento
                            </a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-search fa-3x text-success mb-3"></i>
                            <h5 class="card-title">Buscar Fotos</h5>
                            <p class="card-text">Encontre fotos por evento ou reconhecimento facial.</p>
                            <a href="/search" class="btn btn-success">
                                <i class="fas fa-search"></i> Buscar
                            </a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-upload fa-3x text-warning mb-3"></i>
                            <h5 class="card-title">Upload de Fotos</h5>
                            <p class="card-text">Faça upload de fotos para seus eventos.</p>
                            <a href="/upload" class="btn btn-warning">
                                <i class="fas fa-upload"></i> Upload
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return get_base_html("PhotoCap - Sistema de Reconhecimento Facial", content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de usuário"""
    messages = []
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        
        if not username or not password or not email:
            messages.append('Todos os campos são obrigatórios')
        elif len(password) < 6:
            messages.append('A senha deve ter pelo menos 6 caracteres')
        else:
            if db:
                user_id = db.create_user(username, password, email)
                if user_id:
                    messages.append('Usuário criado com sucesso! Faça login para continuar.')
                    return get_base_html("Cadastro - PhotoCap", get_register_content(), messages)
                else:
                    messages.append('Erro ao criar usuário. Tente novamente.')
            else:
                messages.append('Sistema de banco de dados não disponível')
    
    return get_base_html("Cadastro - PhotoCap", get_register_content(), messages)

def get_register_content():
    """Retorna o conteúdo HTML do formulário de registro"""
    return '''
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card border-0 shadow">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-user-plus"></i> Cadastro de Usuário</h4>
                </div>
                <div class="card-body p-4">
                    <form method="POST">
                        <div class="mb-3">
                            <label for="username" class="form-label">Nome de Usuário *</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="email" class="form-label">E-mail *</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Senha *</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                            <div class="form-text">Mínimo 6 caracteres</div>
                        </div>
                        
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="/login" class="btn btn-outline-secondary me-md-2">Já tenho conta</a>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-user-plus"></i> Cadastrar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuário"""
    messages = []
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            messages.append('E-mail e senha são obrigatórios')
        else:
            if db:
                user = db.authenticate_user_by_email(email, password)
                if user:
                    session['user_id'] = user['UserId']
                    session['username'] = user['Username']
                    return redirect(url_for('index'))
                else:
                    messages.append('E-mail ou senha incorretos')
            else:
                messages.append('Sistema de banco de dados não disponível')
    
    return get_base_html("Login - PhotoCap", get_login_content(), messages)

def get_login_content():
    """Retorna o conteúdo HTML do formulário de login"""
    return '''
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card border-0 shadow">
                <div class="card-header bg-success text-white">
                    <h4 class="mb-0"><i class="fas fa-sign-in-alt"></i> Login</h4>
                </div>
                <div class="card-body p-4">
                    <form method="POST">
                        <div class="mb-3">
                            <label for="email" class="form-label">E-mail</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Senha</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="/register" class="btn btn-outline-secondary me-md-2">Criar conta</a>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-sign-in-alt"></i> Entrar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    '''

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    """Criação de evento"""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    messages = []
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        date = request.form.get('date', '')
        
        if not name or not date:
            messages.append('Nome e data do evento são obrigatórios')
        else:
            if db:
                event_id = db.create_event(name, date)
                if event_id:
                    messages.append(f'Evento "{name}" criado com sucesso!')
                    return get_base_html("Criar Evento - PhotoCap", get_create_event_content(), messages)
                else:
                    messages.append('Erro ao criar evento. Tente novamente.')
            else:
                messages.append('Sistema de banco de dados não disponível')
    
    return get_base_html("Criar Evento - PhotoCap", get_create_event_content(), messages)

def get_create_event_content():
    """Retorna o conteúdo HTML do formulário de criação de evento"""
    return '''
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card border-0 shadow">
                <div class="card-header bg-info text-white">
                    <h4 class="mb-0"><i class="fas fa-calendar-plus"></i> Criar Novo Evento</h4>
                </div>
                <div class="card-body p-4">
                    <form method="POST">
                        <div class="mb-3">
                            <label for="name" class="form-label">Nome do Evento *</label>
                            <input type="text" class="form-control" id="name" name="name" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="date" class="form-label">Data do Evento *</label>
                            <input type="date" class="form-control" id="date" name="date" required>
                        </div>
                        
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="/" class="btn btn-outline-secondary me-md-2">Cancelar</a>
                            <button type="submit" class="btn btn-info">
                                <i class="fas fa-calendar-plus"></i> Criar Evento
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    '''

@app.route('/upload', methods=['GET', 'POST'])
def upload_photo():
    """Upload de fotos"""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    messages = []
    
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        file = request.files.get('photo')
        
        if not event_id or not file:
            messages.append('Selecione um evento e uma foto')
        elif not allowed_file(file.filename):
            messages.append('Tipo de arquivo não permitido')
        else:
            if db:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                
                file.save(filepath)
                
                # Salva no banco de dados
                photo_id = db.save_photo(int(event_id), new_filename)
                if photo_id:
                    messages.append(f'Foto "{filename}" enviada com sucesso!')
                    return get_base_html("Upload - PhotoCap", get_upload_content(db), messages)
                else:
                    messages.append('Erro ao salvar foto. Tente novamente.')
            else:
                messages.append('Sistema de banco de dados não disponível')
    
    return get_base_html("Upload - PhotoCap", get_upload_content(db), messages)

def get_upload_content(db):
    """Retorna o conteúdo HTML do formulário de upload"""
    events_options = ""
    if db:
        events = db.get_all_events()
        for event in events:
            events_options += f'<option value="{event["EventId"]}">{event["Name"]} ({format_date(event["Date"])})</option>'
    
    return f'''
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card border-0 shadow">
                <div class="card-header bg-warning text-dark">
                    <h4 class="mb-0"><i class="fas fa-upload"></i> Upload de Fotos</h4>
                </div>
                <div class="card-body p-4">
                    <form method="POST" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="event_id" class="form-label">Evento *</label>
                            <select class="form-select" id="event_id" name="event_id" required>
                                <option value="">Selecione um evento...</option>
                                {events_options}
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label for="photo" class="form-label">Foto *</label>
                            <input type="file" class="form-control" id="photo" name="photo" accept="image/*" required>
                            <div class="form-text">Formatos permitidos: {", ".join(APP_CONFIG['ALLOWED_EXTENSIONS'])}</div>
                        </div>
                        
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="/" class="btn btn-outline-secondary me-md-2">Cancelar</a>
                            <button type="submit" class="btn btn-warning">
                                <i class="fas fa-upload"></i> Enviar Foto
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    '''

@app.route('/search')
def search():
    """Busca de fotos"""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    event_name = request.args.get('event_name', '')
    messages = []
    
    if db:
        if event_name:
            events = db.search_events(event_name)
        else:
            events = db.get_all_events()
    else:
        events = []
        messages.append('Sistema de banco de dados não disponível')
    
    events_html = ""
    for event in events:
        photos = db.get_photos_by_event(event['EventId']) if db else []
        events_html += f'''
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">{event['Name']}</h5>
                    <p class="card-text">
                        <i class="fas fa-calendar"></i> {format_date(event['Date'])}<br>
                        <i class="fas fa-images"></i> {len(photos)} foto(s)
                    </p>
                    <a href="/event/{event['EventId']}" class="btn btn-primary">
                        <i class="fas fa-eye"></i> Ver Fotos
                    </a>
                </div>
            </div>
        </div>
        '''
    
    content = f'''
    <div class="row">
        <div class="col-12">
            <h1 class="mb-4"><i class="fas fa-search"></i> Buscar Fotos</h1>
            
            <form method="GET" class="mb-4">
                <div class="input-group">
                    <input type="text" name="event_name" class="form-control" placeholder="Digite o nome do evento..." value="{event_name}">
                    <button class="btn btn-primary" type="submit">
                        <i class="fas fa-search"></i> Buscar
                    </button>
                </div>
            </form>
            
            <div class="text-center mb-4">
                <p class="text-muted">ou</p>
                <a href="/face_search" class="btn btn-warning">
                    <i class="fas fa-user-search"></i> Buscar por Reconhecimento Facial
                </a>
            </div>
            
            <div class="row">
                {events_html if events_html else '''
                <div class="col-12 text-center">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5>Nenhum evento encontrado</h5>
                    <p class="text-muted">Crie um evento ou tente uma busca diferente.</p>
                </div>
                '''}
            </div>
        </div>
    </div>
    '''
    
    return get_base_html("Busca - PhotoCap", content, messages)

@app.route('/event/<int:event_id>')
def event_details(event_id):
    """Detalhes do evento com fotos"""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    messages = []
    
    if db:
        event = db.get_event_by_id(event_id)
        photos = db.get_photos_by_event(event_id)
        
        if not event:
            messages.append('Evento não encontrado')
            return get_base_html("Evento - PhotoCap", '<div class="text-center"><h3>Evento não encontrado</h3></div>', messages)
        
        photos_html = ""
        for photo in photos:
            photos_html += f'''
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card h-100">
                    <img src="/uploads/{photo['Filename']}" class="card-img-top" alt="Foto" style="height: 200px; object-fit: cover;">
                    <div class="card-body">
                        <p class="card-text">
                            <small class="text-muted">
                                <i class="fas fa-calendar"></i> {photo['UploadDate']}
                            </small>
                        </p>
                        <a href="/uploads/{photo['Filename']}" target="_blank" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-eye"></i> Ver Foto
                        </a>
                    </div>
                </div>
            </div>
            '''
        
        content = f'''
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4"><i class="fas fa-calendar"></i> {event['Name']}</h1>
                <p class="text-muted mb-4">
                    <i class="fas fa-calendar"></i> {format_date(event['Date'])} | 
                    <i class="fas fa-images"></i> {len(photos)} foto(s)
                </p>
                
                <div class="row">
                    {photos_html if photos_html else '''
                    <div class="col-12 text-center">
                        <i class="fas fa-images fa-3x text-muted mb-3"></i>
                        <h5>Nenhuma foto encontrada</h5>
                        <p class="text-muted">Faça upload de fotos para este evento.</p>
                    </div>
                    '''}
                </div>
            </div>
        </div>
        '''
        
        return get_base_html(f"{event['Name']} - PhotoCap", content, messages)
    else:
        messages.append('Sistema de banco de dados não disponível')
        return get_base_html("Evento - PhotoCap", '<div class="text-center"><h3>Erro no sistema</h3></div>', messages)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve arquivos de upload"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("🚀 Iniciando PhotoCap com SQL Server...")
    print(f"📁 Pasta de uploads: {app.config['UPLOAD_FOLDER']}")
    print(f"🔗 Aplicação disponível em: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 