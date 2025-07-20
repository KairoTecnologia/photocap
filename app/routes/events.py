from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from db_manager import DatabaseManager
import os
from werkzeug.utils import secure_filename

bp = Blueprint('events', __name__, url_prefix='/events')

# Inicializar o gerenciador de dados
data_manager = DatabaseManager()

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/create_event', methods=['GET', 'POST'])
def create_event():
    """Criar novo evento"""
    # Verificar se usuário está logado
    if not session.get('user_id'):
        flash('Você precisa estar logado para criar eventos')
        return redirect(url_for('auth.login'))
    
    # Verificar se é fotógrafo
    if session.get('user_type') != 'photographer':
        flash('Apenas fotógrafos podem criar eventos.')
        return redirect(url_for('dashboard.area_fotografo'))
    
    if request.method == 'POST':
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        
        print(f"📅 Tentativa de criar evento: {event_name} em {event_date}")
        
        if data_manager:
            try:
                event_id = data_manager.create_event(event_name, event_date)
                
                if event_id:
                    flash('Evento criado com sucesso!')
                    print(f"✅ Evento criado com ID: {event_id}")
                    return redirect(url_for('dashboard.area_fotografo'))
                else:
                    flash('Erro ao criar evento')
                    print("❌ Erro ao criar evento")
            except Exception as e:
                flash(f'Erro ao criar evento: {str(e)}')
                print(f"❌ Erro ao criar evento: {e}")
        else:
            flash('Sistema de dados não disponível')
            print("❌ Sistema de dados não disponível")
    
    return render_template('events/create_event.html')

@bp.route('/upload_photos', methods=['GET', 'POST'])
def upload_photos():
    """Upload de fotos"""
    # Verificar se usuário está logado
    if not session.get('user_id'):
        flash('Você precisa estar logado para enviar fotos')
        return redirect(url_for('auth.login'))
    
    # Verificar se é fotógrafo
    if session.get('user_type') != 'photographer':
        flash('Apenas fotógrafos podem enviar fotos.')
        return redirect(url_for('dashboard.area_fotografo'))
    
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        files = request.files.getlist('photos')
        
        print(f"📸 Tentativa de upload para evento ID: {event_id}")
        print(f"📸 Número de arquivos: {len(files)}")
        
        if not event_id:
            flash('Selecione um evento')
            return render_template('events/upload_photos.html', events=data_manager.get_events() if data_manager else [])
        
        if not files or all(f.filename == '' for f in files):
            flash('Selecione pelo menos uma foto')
            return render_template('events/upload_photos.html', events=data_manager.get_events() if data_manager else [])
        
        uploaded_count = 0
        
        try:
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    
                    # Salvar no banco de dados
                    photo_id = data_manager.save_photo(int(event_id), filename)
                    
                    if photo_id:
                        uploaded_count += 1
                        print(f"✅ Foto salva: {filename} (ID: {photo_id})")
                    else:
                        print(f"❌ Erro ao salvar foto: {filename}")
            
            if uploaded_count > 0:
                flash(f'{uploaded_count} foto(s) enviada(s) com sucesso!')
                print(f"✅ Upload concluído: {uploaded_count} fotos")
            else:
                flash('Nenhuma foto foi processada')
                print("❌ Upload falhou: nenhuma foto processada")
            
            return redirect(url_for('dashboard.area_fotografo'))
            
        except Exception as e:
            flash(f'Erro ao enviar fotos: {str(e)}')
            print(f"❌ Erro no upload: {e}")
    
    events = data_manager.get_events() if data_manager else []
    return render_template('events/upload_photos.html', events=events) 