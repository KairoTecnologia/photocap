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
    """Formata uma data para exibição, lidando com strings e objetos datetime"""
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
    Processa fotos enviadas com reconhecimento facial - versão otimizada
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
                    photo['id'] = len(get_photos()) + 1
                
                # Processa a foto com reconhecimento facial se disponível
                if FACE_RECOGNITION_AVAILABLE:
                    try:
                        print(f"🔍 Processando reconhecimento facial para: {filename}")
                        
                        # Limita o número de faces processadas para evitar sobrecarga
                        analysis = face_recognition.process_image(filepath)
                        
                        # Se detectou muitas faces, limita para as primeiras 10
                        if analysis.get('faces_detected', 0) > 10:
                            print(f"⚠️ Muitas faces detectadas ({analysis['faces_detected']}), limitando para 10")
                            analysis['faces'] = analysis['faces'][:10]
                            analysis['faces_detected'] = 10
                        
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
            print(traceback.format_exc())
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

@app.route('/upload_photos', methods=['GET', 'POST'])
def upload_photos():
    """Upload de fotos para fotógrafos - versão otimizada"""
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
                                <br><small class="text-muted">Para melhor performance, limite a 10 fotos por vez.</small>
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

if __name__ == '__main__':
    # Cria pasta uploads se não existir
    os.makedirs('uploads', exist_ok=True)
    
    print("🚀 Iniciando PhotoCap...")
    print("📁 Pasta uploads criada/verificada")
    print("🔧 Configurações carregadas")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 