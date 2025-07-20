from flask import Flask, request, render_template_string, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import traceback

# Importa o módulo de reconhecimento facial
try:
    from face_recognition_module import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    print("✅ Módulo de reconhecimento facial carregado com sucesso")
except ImportError as e:
    FACE_RECOGNITION_AVAILABLE = False
    print(f"⚠️ Módulo de reconhecimento facial não disponível: {e}")

# Importa o gerenciador de dados
try:
    from data_manager import data_manager
    print("✅ Gerenciador de dados carregado com sucesso")
except ImportError as e:
    print(f"⚠️ Gerenciador de dados não disponível: {e}")
    data_manager = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Extensões permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Funções para acessar dados
def get_users():
    if data_manager:
        return data_manager.get_users()
    return {}

def get_events():
    if data_manager:
        return data_manager.get_events()
    return {}

def get_photos():
    if data_manager:
        return data_manager.get_photos()
    return {}

def get_photo_analyses():
    if data_manager:
        return data_manager.get_photo_analyses()
    return {}

def format_date(date_value):
    """Formata uma data para exibição"""
    if isinstance(date_value, str):
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y')
        except:
            return date_value
    elif hasattr(date_value, 'strftime'):
        return date_value.strftime('%d/%m/%Y')
    else:
        return str(date_value)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_uploaded_photos(files, event_id, photographer_id):
    """
    Processa fotos enviadas com reconhecimento facial - versão simplificada
    """
    uploaded_photos = []
    
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
                    'photographer_id': photographer_id,
                    'price': 0.0,
                    'created_at': datetime.now()
                }
                
                # Adiciona a foto usando o gerenciador de dados
                if data_manager:
                    photo_id = data_manager.add_photo(photo)
                    photo['id'] = photo_id
                else:
                    # Fallback para memória
                    photos_data = get_photos()
                    photo_id = len(photos_data) + 1
                    photo['id'] = photo_id
                
                # Processa a foto com reconhecimento facial se disponível
                if FACE_RECOGNITION_AVAILABLE:
                    try:
                        print(f"🔍 Processando reconhecimento facial para: {filename}")
                        
                        # Processa a imagem
                        analysis = face_recognition.process_image(filepath)
                        
                        # Salva a análise
                        if data_manager:
                            data_manager.add_photo_analysis(photo['id'], analysis)
                        
                        # Salva versão processada com detecções marcadas
                        processed_filename = f"processed_{new_filename}"
                        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
                        face_recognition.save_processed_image(filepath, processed_path, analysis)
                        
                        # Adiciona referência à versão processada
                        photo['processed_filename'] = processed_filename
                        
                        print(f"✅ Reconhecimento facial concluído: {analysis.get('faces_detected', 0)} faces detectadas")
                        
                    except Exception as e:
                        print(f"❌ Erro no reconhecimento facial para {filename}: {e}")
                        # Continua mesmo com erro no reconhecimento facial
                
                uploaded_photos.append(photo)
                print(f"✅ Foto {filename} processada com sucesso")
            else:
                print(f"⚠️ Arquivo ignorado: {file.filename if file else 'None'}")
                
        except Exception as e:
            print(f"❌ Erro ao processar foto {i+1}: {e}")
            continue
    
    return uploaded_photos

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
            {f'''
            <div class="alert alert-info alert-dismissible fade show" role="alert">
                <i class="fas fa-info-circle"></i> Para Testes Rápidos:
                <a href="/create_sample_data" class="btn btn-outline-primary btn-sm ms-2">Criar Dados de Exemplo</a>
                <a href="/clear_data" class="btn btn-outline-danger btn-sm ms-1">Limpar Dados</a>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            ''' if data_manager else ''}
            
            {content}
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

@app.route('/')
def index():
    """Página inicial"""
    events_data = get_events()
    recent_events = list(events_data.values())[-6:] if events_data else []
    
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
        
        users_data = get_users()
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
        
        users_data = get_users()
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
        
        if data_manager:
            user_id = data_manager.add_user(user)
        else:
            # Fallback para memória
            users_data = get_users()
            user_id = len(users_data) + 1
            user['id'] = user_id
        
        flash('Conta criada com sucesso!')
        return redirect(url_for('login'))
    
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
    if not user_id or user_id not in get_users():
        flash('Faça login para acessar o dashboard')
        return redirect(url_for('login'))
    
    user = get_users()[user_id]
    if user['user_type'] == 'photographer':
        user_events = [e for e in get_events().values() if e['photographer_id'] == user_id]
        
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
        
        {f'''
        <div class="card mt-4">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-brain"></i> Estatísticas de IA</h5>
            </div>
            <div class="card-body">
                <div class="row text-center">
                    <div class="col-md-4">
                        <h3 class="text-primary">{face_recognition.get_statistics()["known_faces_count"]}</h3>
                        <p class="text-muted">Faces Registradas</p>
                    </div>
                    <div class="col-md-4">
                        <h3 class="text-success">{face_recognition.get_statistics()["users_with_faces"]}</h3>
                        <p class="text-muted">Usuários com Faces</p>
                    </div>
                    <div class="col-md-4">
                        <h3 class="text-info">{len(get_photo_analyses())}</h3>
                        <p class="text-muted">Fotos Processadas</p>
                    </div>
                </div>
            </div>
        </div>
        ''' if FACE_RECOGNITION_AVAILABLE else ''}
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
    if not user_id or user_id not in get_users():
        flash('Faça login para criar eventos')
        return redirect(url_for('login'))
    
    user = get_users()[user_id]
    if user['user_type'] != 'photographer':
        flash('Apenas fotógrafos podem criar eventos')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        date_str = request.form['date']
        location = request.form['location']
        category = request.form['category']
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida')
            return redirect(url_for('create_event'))
        
        event = {
            'name': name,
            'description': description,
            'date': date,
            'location': location,
            'category': category,
            'photographer_id': user_id,
            'created_at': datetime.now()
        }
        
        if data_manager:
            event_id = data_manager.add_event(event)
        else:
            # Fallback para memória
            events_data = get_events()
            event_id = len(events_data) + 1
            event['id'] = event_id
        
        flash('Evento criado com sucesso!')
        return redirect(url_for('dashboard'))
    
    content = '''
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
    
    return get_base_html("Criar Evento - PhotoCap", content)

@app.route('/upload_photos', methods=['GET', 'POST'])
def upload_photos():
    """Upload de fotos para fotógrafos"""
    user_id = session.get('user_id')
    if not user_id or user_id not in get_users():
        flash('Faça login para enviar fotos')
        return redirect(url_for('login'))
    
    user = get_users()[user_id]
    if user['user_type'] != 'photographer':
        flash('Apenas fotógrafos podem enviar fotos')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            event_id = int(request.form['event_id'])
            files = request.files.getlist('photos')
            
            print(f"📤 Upload iniciado: {len(files)} arquivos para evento {event_id}")
            
            if event_id not in get_events():
                flash('Evento não encontrado')
                return redirect(url_for('upload_photos'))
            
            if not files or all(f.filename == '' for f in files):
                flash('Nenhuma foto selecionada')
                return redirect(url_for('upload_photos'))
            
            # Processa as fotos
            uploaded_photos = process_uploaded_photos(files, event_id, user_id)
            
            if uploaded_photos:
                flash(f'{len(uploaded_photos)} foto(s) enviada(s) com sucesso!')
                print(f"✅ Upload concluído: {len(uploaded_photos)} fotos processadas")
            else:
                flash('Nenhuma foto foi processada com sucesso')
                print("❌ Upload falhou: nenhuma foto processada")
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"❌ Erro no upload: {e}")
            print(traceback.format_exc())
            flash(f'Erro ao processar upload: {str(e)}')
            return redirect(url_for('upload_photos'))
    
    user_events = [e for e in get_events().values() if e['photographer_id'] == user_id]
    
    events_options = ""
    for event in user_events:
        events_options += f'<option value="{event["id"]}">{event["name"]} - {format_date(event["date"])}</option>'
    
    content = f'''
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
                                As fotos serão processadas automaticamente para detecção de faces e números de peito.
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
    
    return get_base_html("Enviar Fotos - PhotoCap", content)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir arquivos de upload"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/create_sample_data')
def create_sample_data():
    """Cria dados de exemplo para teste"""
    if data_manager:
        data_manager.create_sample_data()
        flash('Dados de exemplo criados com sucesso!')
    else:
        flash('Gerenciador de dados não disponível')
    return redirect(url_for('index'))

@app.route('/clear_data')
def clear_data():
    """Limpa todos os dados"""
    if data_manager:
        data_manager.clear_data()
        flash('Todos os dados foram limpos!')
    else:
        flash('Gerenciador de dados não disponível')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.pop('user_id', None)
    flash('Logout realizado com sucesso!')
    return redirect(url_for('index'))

@app.route('/search_faces_event/<int:event_id>', methods=['GET', 'POST'])
def search_faces_event(event_id):
    """Busca por reconhecimento facial em um evento específico"""
    if event_id not in get_events():
        flash('Evento não encontrado')
        return redirect(url_for('index'))
    
    event = get_events()[event_id]
    event_photos = [p for p in get_photos().values() if p['event_id'] == event_id]
    
    if request.method == 'POST':
        print(f"DEBUG: Recebido POST para busca facial no evento {event_id}")
        
        if 'face_photo' not in request.files:
            flash('Nenhuma foto selecionada')
            print("DEBUG: Nenhuma foto no request.files")
            return redirect(request.url)
        
        file = request.files['face_photo']
        if file.filename == '':
            flash('Nenhuma foto selecionada')
            print("DEBUG: Nome do arquivo vazio")
            return redirect(request.url)
        
        print(f"DEBUG: Arquivo recebido: {file.filename}")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"search_face_{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            file.save(filepath)
            
            print(f"DEBUG: Arquivo salvo em: {filepath}")
            
            if FACE_RECOGNITION_AVAILABLE:
                # Detecta faces na foto enviada
                search_faces = face_recognition.detect_faces(filepath)
                print(f"DEBUG: Faces detectadas na foto de busca: {len(search_faces)}")
                
                if not search_faces:
                    flash('Nenhuma face detectada na foto enviada. Tente uma foto mais clara do seu rosto.')
                    print("DEBUG: Nenhuma face detectada na foto de busca")
                    return redirect(request.url)
                
                # Extrai características da face de busca
                search_face_features = face_recognition.extract_face_features(filepath, search_faces[0])
                if search_face_features is None:
                    flash('Erro ao processar a face na foto enviada.')
                    return redirect(request.url)
                
                print(f"DEBUG: Características da face de busca extraídas: {len(search_face_features)}")
                
                # Procura por correspondências nas fotos do evento
                matching_photos = []
                print(f"DEBUG: Procurando em {len(event_photos)} fotos do evento")
                
                for photo in event_photos:
                    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo['filename'])
                    if os.path.exists(photo_path):
                        # Detecta faces na foto do evento
                        event_faces = face_recognition.detect_faces(photo_path)
                        
                        if event_faces:
                            # Compara com cada face detectada na foto do evento
                            best_similarity = 0.0
                            for event_face in event_faces:
                                event_face_features = face_recognition.extract_face_features(photo_path, event_face)
                                if event_face_features is not None:
                                    similarity = face_recognition.compare_faces(search_face_features, event_face_features)
                                    best_similarity = max(best_similarity, similarity)
                            
                            # Se encontrou uma similaridade acima do threshold
                            if best_similarity >= face_recognition.similarity_threshold:
                                photo['best_similarity'] = best_similarity
                                matching_photos.append(photo)
                                print(f"DEBUG: Foto {photo['id']} - similaridade: {best_similarity:.3f}")
                            else:
                                print(f"DEBUG: Foto {photo['id']} - similaridade baixa: {best_similarity:.3f}")
                        else:
                            print(f"DEBUG: Foto {photo['id']} - nenhuma face detectada")
                
                # Ordena por similaridade (melhor primeiro)
                matching_photos.sort(key=lambda x: x.get('best_similarity', 0), reverse=True)
                
                print(f"DEBUG: Total de fotos com correspondências encontradas: {len(matching_photos)}")
                
                # Se não encontrou correspondências, mostra uma mensagem específica
                if not matching_photos:
                    flash('Nenhuma foto com face similar encontrada. Tente com uma foto mais clara ou de um ângulo diferente.')
                    return redirect(request.url)
            else:
                # Fallback para quando o módulo não está disponível
                search_faces = [{'x': 0, 'y': 0, 'width': 100, 'height': 100}]
                matching_photos = event_photos[:3]  # Mostra as primeiras 3 fotos
                print("DEBUG: Usando fallback - módulo de reconhecimento não disponível")
            
            # Mostra resultados
            results_html = ""
            for photo in matching_photos:
                display_image = photo.get('processed_filename', photo['filename'])
                analysis = get_photo_analyses().get(photo['id'], {})
                faces_count = analysis.get('faces_detected', 0)
                
                # Calcula similaridade para exibição
                similarity = photo.get('best_similarity', 0)
                similarity_percent = int(similarity * 100)
                
                # Define cor do badge baseado na similaridade
                if similarity >= 0.8:
                    badge_class = "bg-success"
                    similarity_text = f"Alta similaridade ({similarity_percent}%)"
                elif similarity >= 0.6:
                    badge_class = "bg-warning"
                    similarity_text = f"Similaridade média ({similarity_percent}%)"
                else:
                    badge_class = "bg-info"
                    similarity_text = f"Similaridade baixa ({similarity_percent}%)"
                
                results_html += f'''
                <div class="col-md-6 col-lg-4">
                    <div class="card h-100">
                        <img src="/uploads/{display_image}" class="card-img-top" alt="Foto encontrada" style="height: 250px; object-fit: cover;">
                        <div class="card-body">
                            <h6 class="card-title">{photo['original_filename']}</h6>
                            <p class="card-text">
                                <span class="badge {badge_class} mb-2">
                                    <i class="fas fa-user-check"></i> {similarity_text}
                                </span>
                                {f'<br><span class="badge bg-secondary"><i class="fas fa-user"></i> {faces_count} faces</span>' if faces_count > 0 else ''}
                            </p>
                            <div class="btn-group-vertical w-100">
                                <a href="/uploads/{photo['filename']}" class="btn btn-outline-primary btn-sm" target="_blank">Ver Original</a>
                                <a href="/uploads/{display_image}" class="btn btn-outline-success btn-sm" target="_blank">Ver Processada</a>
                            </div>
                        </div>
                    </div>
                </div>
                '''
            
            content = f'''
            <div class="card border-0 shadow mb-4">
                <div class="card-body">
                    <h1 class="mb-3">
                        <i class="fas fa-search"></i> Resultados da Busca
                    </h1>
                    <p class="text-muted">
                        Evento: <strong>{event['name']}</strong><br>
                        Fotos encontradas: <strong>{len(matching_photos)}</strong><br>
                        Faces detectadas na sua foto: <strong>{len(search_faces)}</strong>
                    </p>
                </div>
            </div>
            
            <div class="card border-0 shadow">
                <div class="card-header">
                    <h5 class="mb-0"><i class="fas fa-user-check"></i> Fotos com Faces Detectadas</h5>
                </div>
                <div class="card-body">
                    <div class="row g-4">
                        {results_html if results_html else '<div class="col-12 text-center py-5"><p>Nenhuma foto com faces encontrada neste evento.</p><p class="text-muted">Tente enviar fotos com pessoas para o evento primeiro.</p></div>'}
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-4">
                <a href="/search_faces_event/{event_id}" class="btn btn-outline-primary">
                    <i class="fas fa-search"></i> Nova Busca
                </a>
                <a href="/event/{event_id}" class="btn btn-outline-secondary ms-2">
                    <i class="fas fa-arrow-left"></i> Voltar ao Evento
                </a>
            </div>
            '''
            
            return get_base_html(f"Resultados da Busca - {event['name']}", content)
    
    # Página de busca
    photos_count = len(event_photos)
    faces_count = sum(get_photo_analyses().get(p['id'], {}).get('faces_detected', 0) for p in event_photos)
    
    content = f'''
    <div class="card border-0 shadow mb-4">
        <div class="card-body">
            <h1 class="mb-3">{event['name']}</h1>
            <p class="text-muted mb-2">
                <i class="fas fa-calendar"></i> {format_date(event['date'])}<br>
                <i class="fas fa-map-marker-alt"></i> {event.get('location', 'Local não informado')}<br>
                <i class="fas fa-camera"></i> {photos_count} fotos
                {f'<br><i class="fas fa-user"></i> {faces_count} faces detectadas' if faces_count > 0 else ''}
            </p>
        </div>
    </div>
    
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card border-0 shadow">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <h2 class="fw-bold">Procure suas fotos</h2>
                        <p class="text-muted">
                            A galeria deste evento é privada. Para visualizar suas fotos, 
                            você precisa realizar uma busca usando reconhecimento facial.
                        </p>
                    </div>
                    
                    <div class="row align-items-center mb-4">
                        <div class="col-md-8">
                            <div class="d-flex align-items-center">
                                <div class="me-3">
                                    <i class="fas fa-user-circle fa-2x text-primary"></i>
                                </div>
                                <div>
                                    <h5 class="mb-1">Reconhecimento facial</h5>
                                    <p class="text-muted mb-0">
                                        Tire uma selfie ou envie uma foto do seu rosto
                                        <i class="fas fa-question-circle ms-1" data-bs-toggle="tooltip" title="Use uma foto clara do seu rosto para melhor precisão"></i>
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 text-end">
                            <form method="POST" enctype="multipart/form-data" id="faceSearchForm">
                                <input type="file" id="face_photo" name="face_photo" accept="image/*" style="display: none;" required>
                                <button type="button" class="btn btn-success btn-lg" onclick="document.getElementById('face_photo').click()">
                                    <i class="fas fa-camera"></i> Enviar Foto
                                </button>
                                <button type="submit" id="submitBtn" class="btn btn-primary btn-lg ms-2" style="display: none;">
                                    <i class="fas fa-search"></i> Buscar
                                </button>
                            </form>
                        </div>
                    </div>
                    
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i>
                        <strong>Dicas para melhor resultado:</strong>
                        <ul class="mb-0 mt-2">
                            <li>Use uma foto clara e bem iluminada do seu rosto</li>
                            <li>Evite óculos escuros, chapéus ou máscaras</li>
                            <li>Olhe diretamente para a câmera</li>
                            <li>Certifique-se de que o rosto está bem visível</li>
                        </ul>
                    </div>
                    
                    <div class="text-center">
                        <a href="/event/{event_id}" class="btn btn-outline-secondary">
                            <i class="fas fa-images"></i> Ver Todas as Fotos
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('face_photo').addEventListener('change', function() {{
            if (this.files.length > 0) {{
                console.log('Arquivo selecionado:', this.files[0].name);
                document.getElementById('submitBtn').style.display = 'inline-block';
                document.getElementById('submitBtn').click();
            }}
        }});
    </script>
    '''
    
    return get_base_html(f"Buscar por Face - {event['name']}", content)

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    """Detalhes do evento"""
    if event_id not in get_events():
        flash('Evento não encontrado')
        return redirect(url_for('index'))
    
    event = get_events()[event_id]
    event_photos = [p for p in get_photos().values() if p['event_id'] == event_id]
    
    photos_html = ""
    for photo in event_photos:
        # Verifica se há análise de reconhecimento facial
        analysis = get_photo_analyses().get(photo['id'], {})
        faces_count = analysis.get('faces_detected', 0)
        text_count = analysis.get('text_regions_detected', 0)
        
        # Escolhe qual imagem mostrar (original ou processada)
        display_image = photo.get('processed_filename', photo['filename'])
        
        photos_html += f'''
        <div class="col-md-4 col-lg-3">
            <div class="card h-100">
                <img src="/uploads/{display_image}" class="card-img-top" alt="Foto do evento" style="height: 200px; object-fit: cover;">
                <div class="card-body">
                    <p class="card-text"><small class="text-muted">{photo['original_filename']}</small></p>
                    <div class="mb-2">
                        {f'<span class="badge bg-success me-1"><i class="fas fa-user"></i> {faces_count} faces</span>' if faces_count > 0 else ''}
                        {f'<span class="badge bg-info me-1"><i class="fas fa-hashtag"></i> {text_count} textos</span>' if text_count > 0 else ''}
                    </div>
                    <div class="btn-group-vertical w-100">
                        <a href="/uploads/{photo['filename']}" class="btn btn-outline-primary btn-sm" target="_blank">Ver Original</a>
                        {f'<a href="/uploads/{display_image}" class="btn btn-outline-success btn-sm" target="_blank">Ver Processada</a>' if photo.get('processed_filename') else ''}
                    </div>
                </div>
            </div>
        </div>
        '''
    
    content = f'''
    <div class="card border-0 shadow mb-4">
        <div class="card-body">
            <h1 class="mb-3">{event['name']}</h1>
            <p class="text-muted mb-2">
                <i class="fas fa-calendar"></i> {format_date(event['date'])}<br>
                <i class="fas fa-map-marker-alt"></i> {event.get('location', 'Local não informado')}
            </p>
            <p class="mb-0">{event.get('description', '')}</p>
        </div>
    </div>
    
    <div class="card border-0 shadow">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0"><i class="fas fa-images"></i> Fotos do Evento</h5>
            <a href="/search_faces_event/{event_id}" class="btn btn-primary btn-sm">
                <i class="fas fa-search"></i> Buscar por Face
            </a>
        </div>
        <div class="card-body">
            <div class="row g-4">
                {photos_html if photos_html else '<div class="col-12 text-center py-5"><p>Nenhuma foto disponível ainda.</p></div>'}
            </div>
        </div>
    </div>
    '''
    
    return get_base_html(f"{event['name']} - PhotoCap", content)

@app.route('/search')
def search():
    """Busca de eventos"""
    event_name = request.args.get('event_name', '')
    
    if event_name:
        filtered_events = [e for e in get_events().values() if event_name.lower() in e['name'].lower()]
    else:
        filtered_events = list(get_events().values())
    
    events_html = ""
    for event in filtered_events:
        photos_count = len([p for p in get_photos().values() if p['event_id'] == event['id']])
        events_html += f'''
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">{event['name']}</h5>
                    <p class="card-text">
                        <i class="fas fa-calendar"></i> {format_date(event['date'])}<br>
                        <i class="fas fa-map-marker-alt"></i> {event.get('location', 'Local não informado')}<br>
                        <i class="fas fa-camera"></i> {photos_count} fotos
                    </p>
                    <div class="d-grid gap-2">
                        <a href="/event/{event['id']}" class="btn btn-primary">Ver Fotos</a>
                        <a href="/search_faces_event/{event['id']}" class="btn btn-outline-success">
                            <i class="fas fa-user"></i> Buscar por Face
                        </a>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    content = f'''
    <h1 class="text-center mb-5">Encontre suas fotos</h1>
    
    <form action="/search" method="GET" class="mb-5">
        <div class="input-group input-group-lg">
            <input type="text" name="event_name" class="form-control" placeholder="Digite o nome do evento..." value="{event_name}">
            <button class="btn btn-primary" type="submit">
                <i class="fas fa-search"></i> Buscar
            </button>
        </div>
    </form>
    
    <div class="row">
        {events_html if events_html else '<div class="col-12 text-center"><p>Nenhum evento encontrado.</p></div>'}
    </div>
    '''
    
    return get_base_html("Buscar Fotos - PhotoCap", content)

if __name__ == '__main__':
    # Cria pasta uploads se não existir
    os.makedirs('uploads', exist_ok=True)
    
    print("🚀 Iniciando PhotoCap...")
    print("📁 Pasta uploads criada/verificada")
    print("🔧 Configurações carregadas")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 