from flask import Flask, request, render_template_string, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime

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

def get_base_html(title, content, messages=None):
    """Template HTML base com Bootstrap 5"""
    messages_html = ""
    if messages:
        for message in messages:
            messages_html += f'''
            <div class="alert alert-info alert-dismissible fade show" role="alert">
                {message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            '''
    
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
            {messages_html}
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
    messages = []
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        print(f"🔐 Tentativa de login: {email}")
        
        if data_manager:
            users_data = data_manager.get_users()
            print(f"📊 Total de usuários: {len(users_data)}")
            
            user = None
            for u in users_data.values():
                print(f"🔍 Verificando usuário: {u['email']} - {u['password']}")
                if u['email'] == email and u['password'] == password:
                    user = u
                    break
            
            if user:
                session['user_id'] = user['id']
                messages.append('Login realizado com sucesso!')
                print(f"✅ Login bem-sucedido para: {user['username']}")
                return redirect(url_for('dashboard'))
            else:
                messages.append('Email ou senha inválidos')
                print("❌ Login falhou - credenciais inválidas")
        else:
            messages.append('Sistema de dados não disponível')
            print("❌ Sistema de dados não disponível")
    
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
    
    return get_base_html("Login - PhotoCap", content, messages)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    messages = []
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        print(f"📝 Tentativa de cadastro: {email} ({user_type})")
        
        if data_manager:
            users_data = data_manager.get_users()
            
            # Verifica se o email já existe
            for user in users_data.values():
                if user['email'] == email:
                    messages.append('Email já cadastrado')
                    print(f"❌ Email já cadastrado: {email}")
                    return get_base_html("Cadastro - PhotoCap", get_register_content(), messages)
            
            # Cria o novo usuário
            user = {
                'username': username,
                'email': email,
                'password': password,
                'user_type': user_type,
                'created_at': datetime.now()
            }
            
            try:
                user_id = data_manager.add_user(user)
                messages.append('Conta criada com sucesso!')
                print(f"✅ Usuário criado com ID: {user_id}")
                return redirect(url_for('login'))
            except Exception as e:
                messages.append(f'Erro ao criar conta: {str(e)}')
                print(f"❌ Erro ao criar usuário: {e}")
        else:
            messages.append('Sistema de dados não disponível')
            print("❌ Sistema de dados não disponível")
    
    return get_base_html("Cadastro - PhotoCap", get_register_content(), messages)

def get_register_content():
    """Retorna o conteúdo HTML do formulário de registro"""
    return '''
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

@app.route('/dashboard')
def dashboard():
    """Dashboard do usuário"""
    user_id = session.get('user_id')
    if not user_id or not data_manager:
        return redirect(url_for('login'))
    
    users_data = data_manager.get_users()
    if user_id not in users_data:
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

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    """Criar novo evento"""
    user_id = session.get('user_id')
    if not user_id or not data_manager:
        return redirect(url_for('login'))
    
    users_data = data_manager.get_users()
    if user_id not in users_data:
        return redirect(url_for('login'))
    
    user = users_data[user_id]
    if user['user_type'] != 'photographer':
        return redirect(url_for('dashboard'))
    
    messages = []
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        date_str = request.form['date']
        location = request.form['location']
        category = request.form['category']
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.append('Data inválida')
            return get_base_html("Criar Evento - PhotoCap", get_create_event_content(), messages)
        
        event = {
            'name': name,
            'description': description,
            'date': date,
            'location': location,
            'category': category,
            'photographer_id': user_id,
            'created_at': datetime.now()
        }
        
        try:
            event_id = data_manager.add_event(event)
            messages.append('Evento criado com sucesso!')
            print(f"✅ Evento criado com ID: {event_id}")
            return redirect(url_for('dashboard'))
        except Exception as e:
            messages.append(f'Erro ao criar evento: {str(e)}')
            print(f"❌ Erro ao criar evento: {e}")
    
    return get_base_html("Criar Evento - PhotoCap", get_create_event_content(), messages)

def get_create_event_content():
    """Retorna o conteúdo HTML do formulário de criação de evento"""
    return '''
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card border-0 shadow">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-plus"></i> Criar Novo Evento</h4>
                </div>
                <div class="card-body p-4">
                    <form method="POST">
                        <div class="row">
                            <div class="col-md-8">
                                <div class="mb-3">
                                    <label for="name" class="form-label">Nome do Evento *</label>
                                    <input type="text" class="form-control" id="name" name="name" required>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="category" class="form-label">Categoria</label>
                                    <select class="form-select" id="category" name="category">
                                        <option value="">Selecione...</option>
                                        <option value="Corrida">Corrida</option>
                                        <option value="Ciclismo">Ciclismo</option>
                                        <option value="Futebol">Futebol</option>
                                        <option value="Casamento">Casamento</option>
                                        <option value="Festa">Festa</option>
                                        <option value="Outros">Outros</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="description" class="form-label">Descrição</label>
                            <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="date" class="form-label">Data do Evento *</label>
                                    <input type="date" class="form-control" id="date" name="date" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="location" class="form-label">Local</label>
                                    <input type="text" class="form-control" id="location" name="location">
                                </div>
                            </div>
                        </div>
                        
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="/dashboard" class="btn btn-outline-secondary me-md-2">Cancelar</a>
                            <button type="submit" class="btn btn-primary">Criar Evento</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    '''

@app.route('/upload_photos', methods=['GET', 'POST'])
def upload_photos():
    """Upload de fotos para fotógrafos"""
    user_id = session.get('user_id')
    if not user_id or not data_manager:
        return redirect(url_for('login'))
    
    users_data = data_manager.get_users()
    if user_id not in users_data:
        return redirect(url_for('login'))
    
    user = users_data[user_id]
    if user['user_type'] != 'photographer':
        return redirect(url_for('dashboard'))
    
    messages = []
    
    if request.method == 'POST':
        try:
            event_id = int(request.form['event_id'])
            files = request.files.getlist('photos')
            
            print(f"📤 Upload iniciado: {len(files)} arquivos para evento {event_id}")
            
            if event_id not in data_manager.get_events():
                messages.append('Evento não encontrado')
                return get_base_html("Enviar Fotos - PhotoCap", get_upload_photos_content(), messages)
            
            if not files or all(f.filename == '' for f in files):
                messages.append('Nenhuma foto selecionada')
                return get_base_html("Enviar Fotos - PhotoCap", get_upload_photos_content(), messages)
            
            uploaded_count = 0
            for i, file in enumerate(files):
                try:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        new_filename = f"{timestamp}_{filename}"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                        
                        print(f"📸 Processando foto {i+1}/{len(files)}: {filename}")
                        
                        # Salva o arquivo
                        file.save(filepath)
                        print(f"✅ Arquivo salvo: {filepath}")
                        
                        # Cria registro da foto
                        photo = {
                            'filename': new_filename,
                            'original_filename': filename,
                            'event_id': event_id,
                            'photographer_id': user_id,
                            'price': 0.0,
                            'created_at': datetime.now()
                        }
                        
                        photo_id = data_manager.add_photo(photo)
                        uploaded_count += 1
                        print(f"✅ Foto {filename} processada com sucesso")
                    else:
                        print(f"⚠️ Arquivo ignorado: {file.filename if file else 'None'}")
                        
                except Exception as e:
                    print(f"❌ Erro ao processar foto {i+1}: {e}")
                    continue
            
            if uploaded_count > 0:
                messages.append(f'{uploaded_count} foto(s) enviada(s) com sucesso!')
                print(f"✅ Upload concluído: {uploaded_count} fotos processadas")
            else:
                messages.append('Nenhuma foto foi processada com sucesso')
                print("❌ Upload falhou: nenhuma foto processada")
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"❌ Erro no upload: {e}")
            messages.append(f'Erro ao processar upload: {str(e)}')
    
    return get_base_html("Enviar Fotos - PhotoCap", get_upload_photos_content(), messages)

def get_upload_photos_content():
    """Retorna o conteúdo HTML do formulário de upload de fotos"""
    if not data_manager:
        return '''
        <div class="text-center py-4">
            <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
            <h5>Sistema de dados não disponível</h5>
            <p class="text-muted">Não é possível enviar fotos no momento.</p>
        </div>
        '''
    
    events_data = data_manager.get_events()
    user_id = session.get('user_id')
    user_events = [e for e in events_data.values() if e['photographer_id'] == user_id]
    
    events_options = ""
    for event in user_events:
        events_options += f'<option value="{event["id"]}">{event["name"]} - {format_date(event["date"])}</option>'
    
    return f'''
    <div class="row justify-content-center">
        <div class="col-md-10">
            <div class="card border-0 shadow">
                <div class="card-header bg-success text-white">
                    <h4 class="mb-0"><i class="fas fa-upload"></i> Enviar Fotos</h4>
                </div>
                <div class="card-body p-4">
                    {f'''
                    <form method="POST" enctype="multipart/form-data">
                        <div class="mb-4">
                            <label for="event_id" class="form-label">Selecione o Evento *</label>
                            <select class="form-select" id="event_id" name="event_id" required>
                                <option value="">Escolha um evento...</option>
                                {events_options}
                            </select>
                        </div>
                        
                        <div class="mb-4">
                            <label for="photos" class="form-label">Selecione as Fotos *</label>
                            <input type="file" class="form-control" id="photos" name="photos" multiple accept="image/*" required>
                            <div class="form-text">Formatos aceitos: JPG, PNG, GIF. Máximo 16MB por arquivo.</div>
                        </div>
                        
                        <div class="mb-4">
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle"></i>
                                <strong>Processamento Automático:</strong> 
                                As fotos serão processadas automaticamente para detecção de faces.
                            </div>
                        </div>
                        
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="/dashboard" class="btn btn-outline-secondary me-md-2">Cancelar</a>
                            <button type="submit" class="btn btn-success">Enviar Fotos</button>
                        </div>
                    </form>
                    ''' if user_events else '''
                    <div class="text-center py-4">
                        <i class="fas fa-calendar-times fa-3x text-muted mb-3"></i>
                        <h5>Nenhum evento criado</h5>
                        <p class="text-muted">Você precisa criar um evento antes de enviar fotos.</p>
                        <a href="/create_event" class="btn btn-primary">
                            <i class="fas fa-plus"></i> Criar Evento
                        </a>
                    </div>
                    '''}
                </div>
            </div>
        </div>
    </div>
    '''

@app.route('/search')
def search():
    """Busca de fotos"""
    event_name = request.args.get('event_name', '')
    
    if data_manager:
        events_data = data_manager.get_events()
        
        if event_name:
            # Filtra eventos pelo nome
            filtered_events = []
            for event in events_data.values():
                if event_name.lower() in event['name'].lower():
                    filtered_events.append(event)
        else:
            filtered_events = list(events_data.values())
    else:
        filtered_events = []
    
    events_html = ""
    for event in filtered_events:
        events_html += f'''
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">{event['name']}</h5>
                    <p class="card-text">
                        <i class="fas fa-calendar"></i> {format_date(event['date'])}<br>
                        <i class="fas fa-map-marker-alt"></i> {event.get('location', 'Local não informado')}<br>
                        <i class="fas fa-tag"></i> {event.get('category', 'Não categorizado')}
                    </p>
                    <a href="/event/{event['id']}" class="btn btn-primary">Ver Fotos</a>
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
                    <p class="text-muted">Tente buscar por outro termo.</p>
                </div>
                '''}
            </div>
        </div>
    </div>
    '''
    
    return get_base_html("Buscar Fotos - PhotoCap", content)

@app.route('/event/<int:event_id>')
def event_details(event_id):
    """Detalhes de um evento específico"""
    if not data_manager:
        return redirect(url_for('index'))
    
    events_data = data_manager.get_events()
    if event_id not in events_data:
        return redirect(url_for('index'))
    
    event = events_data[event_id]
    photos_data = data_manager.get_photos()
    event_photos = [p for p in photos_data.values() if p['event_id'] == event_id]
    
    # Agrupa fotos por fotógrafo
    users_data = data_manager.get_users()
    photos_by_photographer = {}
    for photo in event_photos:
        photographer_id = photo['photographer_id']
        if photographer_id in users_data:
            photographer_name = users_data[photographer_id]['username']
            if photographer_name not in photos_by_photographer:
                photos_by_photographer[photographer_name] = []
            photos_by_photographer[photographer_name].append(photo)
    
    photos_html = ""
    for photographer_name, photos in photos_by_photographer.items():
        photos_html += f'''
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-camera"></i> Fotos por {photographer_name}</h5>
            </div>
            <div class="card-body">
                <div class="row">
        '''
        
        for photo in photos:
            photos_html += f'''
            <div class="col-md-4 col-lg-3 mb-3">
                <div class="card h-100">
                    <img src="/uploads/{photo['filename']}" class="card-img-top" alt="Foto" style="height: 200px; object-fit: cover;">
                    <div class="card-body">
                        <p class="card-text">
                            <small class="text-muted">
                                <i class="fas fa-calendar"></i> {format_date(photo['created_at'])}
                            </small>
                        </p>
                        <a href="/uploads/{photo['filename']}" target="_blank" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-eye"></i> Ver
                        </a>
                    </div>
                </div>
            </div>
            '''
        
        photos_html += '''
                </div>
            </div>
        </div>
        '''
    
    content = f'''
    <div class="row">
        <div class="col-12">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/">Início</a></li>
                    <li class="breadcrumb-item active">{event['name']}</li>
                </ol>
            </nav>
            
            <div class="card mb-4">
                <div class="card-body">
                    <h1 class="card-title">{event['name']}</h1>
                    <p class="card-text">{event.get('description', 'Sem descrição')}</p>
                    <div class="row">
                        <div class="col-md-6">
                            <p><i class="fas fa-calendar"></i> <strong>Data:</strong> {format_date(event['date'])}</p>
                        </div>
                        <div class="col-md-6">
                            <p><i class="fas fa-map-marker-alt"></i> <strong>Local:</strong> {event.get('location', 'Local não informado')}</p>
                        </div>
                    </div>
                    <p><i class="fas fa-tag"></i> <strong>Categoria:</strong> {event.get('category', 'Não categorizado')}</p>
                </div>
            </div>
            
            {photos_html if photos_html else '''
            <div class="text-center py-5">
                <i class="fas fa-camera-slash fa-3x text-muted mb-3"></i>
                <h5>Nenhuma foto disponível</h5>
                <p class="text-muted">Ainda não há fotos para este evento.</p>
            </div>
            '''}
        </div>
    </div>
    '''
    
    return get_base_html(f"{event['name']} - PhotoCap", content)

@app.route('/face_search', methods=['GET', 'POST'])
def face_search():
    """Busca de fotos por reconhecimento facial"""
    messages = []
    
    if request.method == 'POST':
        try:
            file = request.files['search_face']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_filename = f"search_{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                
                file.save(filepath)
                
                # Verifica se o módulo de reconhecimento facial está disponível
                try:
                    from face_recognition_simple import face_recognition
                    FACE_RECOGNITION_AVAILABLE = True
                except ImportError:
                    FACE_RECOGNITION_AVAILABLE = False
                
                if FACE_RECOGNITION_AVAILABLE:
                    # Detecta faces na foto de busca
                    search_faces = face_recognition.detect_faces(filepath)
                    
                    if search_faces:
                        # Extrai características da primeira face detectada
                        search_features = face_recognition.extract_face_features(filepath, search_faces[0])
                        
                        if search_features is not None:
                            # Busca em todas as fotos
                            if data_manager:
                                photos_data = data_manager.get_photos()
                                events_data = data_manager.get_events()
                                users_data = data_manager.get_users()
                                photo_analyses = data_manager.get_photo_analyses()
                                
                                similar_photos = []
                                
                                for photo_id, photo in photos_data.items():
                                    # Verifica se a foto tem análise
                                    if photo_id in photo_analyses:
                                        analysis = photo_analyses[photo_id]
                                        
                                        # Compara com cada face detectada na foto
                                        for face in analysis.get('faces', []):
                                            if 'features' in face:
                                                similarity = face_recognition.compare_faces(
                                                    search_features, face['features']
                                                )
                                                
                                                if similarity >= face_recognition.similarity_threshold:
                                                    # Adiciona informações do evento
                                                    event = events_data.get(photo['event_id'])
                                                    photographer = users_data.get(photo['photographer_id'])
                                                    
                                                    similar_photos.append({
                                                        'photo': photo,
                                                        'event': event,
                                                        'photographer': photographer,
                                                        'similarity': similarity,
                                                        'face_location': face
                                                    })
                                
                                # Ordena por similaridade
                                similar_photos.sort(key=lambda x: x['similarity'], reverse=True)
                                
                                # Gera HTML dos resultados
                                results_html = ""
                                for result in similar_photos[:20]:  # Limita a 20 resultados
                                    photo = result['photo']
                                    event = result['event']
                                    photographer = result['photographer']
                                    similarity = result['similarity']
                                    
                                    results_html += f'''
                                    <div class="col-md-6 col-lg-4 mb-4">
                                        <div class="card h-100">
                                            <img src="/uploads/{photo['filename']}" class="card-img-top" alt="Foto" style="height: 200px; object-fit: cover;">
                                            <div class="card-body">
                                                <h6 class="card-title">{event['name'] if event else 'Evento não encontrado'}</h6>
                                                <p class="card-text">
                                                    <small class="text-muted">
                                                        <i class="fas fa-calendar"></i> {format_date(event['date']) if event else 'N/A'}<br>
                                                        <i class="fas fa-user"></i> {photographer['username'] if photographer else 'Fotógrafo desconhecido'}<br>
                                                        <i class="fas fa-percentage"></i> <strong>Similaridade: {similarity:.1%}</strong>
                                                    </small>
                                                </p>
                                                <a href="/uploads/{photo['filename']}" target="_blank" class="btn btn-outline-primary btn-sm">
                                                    <i class="fas fa-eye"></i> Ver Foto
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                    '''
                                
                                content = f'''
                                <div class="row">
                                    <div class="col-12">
                                        <h1 class="mb-4"><i class="fas fa-search"></i> Busca por Reconhecimento Facial</h1>
                                        
                                        <div class="alert alert-success">
                                            <i class="fas fa-check-circle"></i>
                                            <strong>Busca concluída!</strong> 
                                            Encontradas {len(similar_photos)} foto(s) com similaridade acima de {face_recognition.similarity_threshold:.0%}.
                                        </div>
                                        
                                        <div class="row">
                                            {results_html if results_html else '''
                                            <div class="col-12 text-center">
                                                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                                                <h5>Nenhuma foto similar encontrada</h5>
                                                <p class="text-muted">Tente com uma foto diferente ou ajuste os critérios de busca.</p>
                                            </div>
                                            '''}
                                        </div>
                                        
                                        <div class="mt-4">
                                            <a href="/face_search" class="btn btn-primary">
                                                <i class="fas fa-search"></i> Nova Busca
                                            </a>
                                        </div>
                                    </div>
                                </div>
                                '''
                                
                                return get_base_html("Resultados da Busca - PhotoCap", content, messages)
                            else:
                                messages.append('Sistema de dados não disponível')
                        else:
                            messages.append('Não foi possível extrair características da face na foto de busca')
                    else:
                        messages.append('Nenhuma face detectada na foto de busca')
                else:
                    messages.append('Módulo de reconhecimento facial não disponível')
            else:
                messages.append('Arquivo inválido')
        except Exception as e:
            print(f"❌ Erro na busca facial: {e}")
            messages.append(f'Erro na busca: {str(e)}')
    
    return get_base_html("Busca Facial - PhotoCap", get_face_search_content(), messages)

def get_face_search_content():
    """Retorna o conteúdo HTML do formulário de busca facial"""
    return '''
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card border-0 shadow">
                <div class="card-header bg-warning text-dark">
                    <h4 class="mb-0"><i class="fas fa-search"></i> Busca por Reconhecimento Facial</h4>
                </div>
                <div class="card-body p-4">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i>
                        <strong>Como funciona:</strong> 
                        Envie uma foto do rosto da pessoa que você quer encontrar nas fotos dos eventos.
                    </div>
                    
                    <form method="POST" enctype="multipart/form-data">
                        <div class="mb-4">
                            <label for="search_face" class="form-label">Foto do Rosto para Busca *</label>
                            <input type="file" class="form-control" id="search_face" name="search_face" accept="image/*" required>
                            <div class="form-text">Envie uma foto clara do rosto da pessoa que você quer encontrar.</div>
                        </div>
                        
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="/search" class="btn btn-outline-secondary me-md-2">Cancelar</a>
                            <button type="submit" class="btn btn-warning">
                                <i class="fas fa-search"></i> Buscar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    '''

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir arquivos de upload"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Cria pasta uploads se não existir
    os.makedirs('uploads', exist_ok=True)
    
    print("🚀 Iniciando PhotoCap...")
    print("📁 Pasta uploads criada/verificada")
    print("🔧 Configurações carregadas")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 