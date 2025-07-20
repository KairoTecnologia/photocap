from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import cv2
import face_recognition
import easyocr
import numpy as np
from PIL import Image
import json
from datetime import datetime

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photocap.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Extensões permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Inicialização do banco de dados
db = SQLAlchemy(app)

# Inicialização do login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Inicialização do OCR
reader = easyocr.Reader(['en', 'pt'])

# Modelos do banco de dados
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'photographer' ou 'customer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200))
    category = db.Column(db.String(50))
    photographer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    photographer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, default=0.0)
    face_encodings = db.Column(db.Text)  # JSON com encodings faciais
    detected_numbers = db.Column(db.Text)  # JSON com números detectados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    price_paid = db.Column(db.Float, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image_for_faces(image_path):
    """Processa imagem para detectar faces e extrair encodings"""
    try:
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        return face_encodings
    except Exception as e:
        print(f"Erro ao processar faces: {e}")
        return []

def process_image_for_numbers(image_path):
    """Processa imagem para detectar números usando OCR"""
    try:
        results = reader.readtext(image_path)
        numbers = []
        for (bbox, text, prob) in results:
            # Filtra apenas números
            if text.isdigit() and prob > 0.5:
                numbers.append({
                    'number': text,
                    'confidence': prob,
                    'bbox': bbox
                })
        return numbers
    except Exception as e:
        print(f"Erro ao processar números: {e}")
        return []

# Rotas da aplicação
@app.route('/')
def index():
    """Página inicial"""
    events = Event.query.order_by(Event.date.desc()).limit(6).all()
    return render_template('index.html', events=events)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha inválidos')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            user_type=user_type
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Conta criada com sucesso!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard do usuário"""
    if current_user.user_type == 'photographer':
        events = Event.query.filter_by(photographer_id=current_user.id).all()
        return render_template('photographer_dashboard.html', events=events)
    else:
        purchases = Purchase.query.filter_by(customer_id=current_user.id).all()
        return render_template('customer_dashboard.html', purchases=purchases)

@app.route('/search')
def search():
    """Busca de eventos e fotos"""
    query = request.args.get('q', '')
    event_name = request.args.get('event_name', '')
    
    if event_name:
        events = Event.query.filter(Event.name.ilike(f'%{event_name}%')).all()
    else:
        events = Event.query.all()
    
    return render_template('search.html', events=events, query=query)

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    """Detalhes do evento"""
    event = Event.query.get_or_404(event_id)
    photos = Photo.query.filter_by(event_id=event_id).all()
    return render_template('event_detail.html', event=event, photos=photos)

@app.route('/upload_photos', methods=['GET', 'POST'])
@login_required
def upload_photos():
    """Upload de fotos para fotógrafos"""
    if current_user.user_type != 'photographer':
        flash('Acesso negado')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        event_id = request.form['event_id']
        files = request.files.getlist('photos')
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                file.save(filepath)
                
                # Processa a imagem para faces e números
                face_encodings = process_image_for_faces(filepath)
                detected_numbers = process_image_for_numbers(filepath)
                
                photo = Photo(
                    filename=new_filename,
                    original_filename=filename,
                    event_id=event_id,
                    photographer_id=current_user.id,
                    face_encodings=json.dumps([enc.tolist() for enc in face_encodings]),
                    detected_numbers=json.dumps(detected_numbers)
                )
                db.session.add(photo)
        
        db.session.commit()
        flash('Fotos enviadas com sucesso!')
        return redirect(url_for('dashboard'))
    
    events = Event.query.filter_by(photographer_id=current_user.id).all()
    return render_template('upload_photos.html', events=events)

@app.route('/search_by_face', methods=['POST'])
def search_by_face():
    """Busca fotos por reconhecimento facial"""
    if 'photo' not in request.files:
        return jsonify({'error': 'Nenhuma foto enviada'})
    
    file = request.files['photo']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
        file.save(filepath)
        
        # Processa a foto enviada
        face_encodings = process_image_for_faces(filepath)
        
        if not face_encodings:
            os.remove(filepath)
            return jsonify({'error': 'Nenhuma face detectada'})
        
        # Busca por fotos similares
        photos = Photo.query.all()
        matching_photos = []
        
        for photo in photos:
            if photo.face_encodings:
                stored_encodings = json.loads(photo.face_encodings)
                for stored_enc in stored_encodings:
                    stored_enc = np.array(stored_enc)
                    for query_enc in face_encodings:
                        distance = face_recognition.face_distance([stored_enc], query_enc)[0]
                        if distance < 0.6:  # Threshold para similaridade
                            matching_photos.append({
                                'id': photo.id,
                                'filename': photo.filename,
                                'event_id': photo.event_id,
                                'similarity': 1 - distance
                            })
        
        os.remove(filepath)
        return jsonify({'matches': matching_photos})
    
    return jsonify({'error': 'Arquivo inválido'})

@app.route('/search_by_number', methods=['POST'])
def search_by_number():
    """Busca fotos por número"""
    number = request.form.get('number')
    if not number:
        return jsonify({'error': 'Número não fornecido'})
    
    photos = Photo.query.all()
    matching_photos = []
    
    for photo in photos:
        if photo.detected_numbers:
            detected_numbers = json.loads(photo.detected_numbers)
            for detected in detected_numbers:
                if detected['number'] == number:
                    matching_photos.append({
                        'id': photo.id,
                        'filename': photo.filename,
                        'event_id': photo.event_id,
                        'confidence': detected['confidence']
                    })
    
    return jsonify({'matches': matching_photos})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 