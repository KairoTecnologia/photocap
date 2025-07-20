from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from db_manager import DatabaseManager
from datetime import datetime
import os

bp = Blueprint('search', __name__, url_prefix='/search')

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
    """Página de busca"""
    event_name = request.args.get('event_name', '')
    events = []
    
    if event_name and data_manager:
        events = data_manager.search_events(event_name)
    
    return render_template('search/search.html', events=events, event_name=event_name, format_date=format_date)

@bp.route('/event/<int:event_id>')
def event_details(event_id):
    """Detalhes do evento com fotos"""
    if not data_manager:
        flash('Sistema de dados não disponível')
        return redirect(url_for('search.index'))
    
    # Buscar evento
    event = data_manager.get_event_by_id(event_id)
    if not event:
        flash('Evento não encontrado')
        return redirect(url_for('search.index'))
    
    # Buscar fotos do evento
    photos = data_manager.get_photos_by_event(event_id)
    
    return render_template('search/event_details.html', 
                         event=event, 
                         photos=photos, 
                         format_date=format_date)

@bp.route('/face_search', methods=['GET', 'POST'])
def face_search():
    """Busca por reconhecimento facial"""
    if request.method == 'POST':
        # Aqui você implementaria a lógica de reconhecimento facial
        # Por enquanto, vamos apenas simular
        flash('Funcionalidade de busca por face em desenvolvimento')
        return redirect(url_for('search.index'))
    
    return render_template('search/face_search.html') 