from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db_manager import DatabaseManager
import os

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Inicializar o gerenciador de dados
data_manager = DatabaseManager()

def clean_cpf(cpf):
    """Remove pontos e hífens do CPF"""
    if not cpf:
        return None
    return cpf.replace('.', '').replace('-', '').replace('/', '')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        print(f"🔐 Tentativa de login: {email}")
        
        if data_manager:
            # Usa autenticação por email com hash e salt
            user = data_manager.authenticate_user_by_email(email, password)
            
            if user:
                # Torna a sessão permanente
                session.permanent = True
                session['user_id'] = user['UserId']
                session['username'] = user['Username']
                session['email'] = user['Email']
                session['user_type'] = user['UserType']
                
                print(f"✅ Sessão definida - user_id: {session['user_id']}")
                print(f"✅ Tipo de usuário: {user['UserType']}")
                flash('Login realizado com sucesso!')
                print(f"✅ Login bem-sucedido para: {user['Username']}")
                return redirect(url_for('dashboard.index'))
            else:
                flash('Email ou senha inválidos')
                print("❌ Login falhou - credenciais inválidas")
        else:
            flash('Sistema de dados não disponível')
            print("❌ Sistema de dados não disponível")
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro único"""
    if request.method == 'POST':
        # Coleta todos os dados do formulário
        full_name = request.form['full_name']
        cpf = request.form.get('cpf', '')
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        user_type = 'customer'  # Tipo padrão para novos usuários
        terms_accepted = request.form.get('terms_accepted') == 'on'
        
        print(f"📝 Tentativa de cadastro: {email} ({user_type})")
        
        # Validações
        if password != password_confirm:
            flash('As senhas não coincidem')
            return render_template('auth/register.html')
        
        if not terms_accepted:
            flash('Você deve aceitar os termos de uso')
            return render_template('auth/register.html')
        
        if data_manager:
            try:
                # Cria o novo usuário com todos os dados
                user_id = data_manager.create_user(
                    username=email,  # Usa email como username
                    password=password,
                    email=email,
                    user_type=user_type,
                    full_name=full_name,
                    cpf=clean_cpf(cpf),
                    phone=phone
                )
                
                if user_id:
                    flash('Conta criada com sucesso!')
                    print(f"✅ Usuário criado com ID: {user_id}, Tipo: {user_type}")
                    return redirect(url_for('auth.login'))
                else:
                    flash('Erro ao criar conta - usuário já existe')
                    print(f"❌ Erro ao criar usuário - já existe")
            except Exception as e:
                flash(f'Erro ao criar conta: {str(e)}')
                print(f"❌ Erro ao criar usuário: {e}")
        else:
            flash('Sistema de dados não disponível')
            print("❌ Sistema de dados não disponível")
    
    return render_template('auth/register.html')

@bp.route('/register/photographer', methods=['GET', 'POST'])
def register_photographer():
    """Página de registro específica para fotógrafos"""
    if request.method == 'POST':
        # Coleta todos os dados do formulário
        country = request.form.get('country', 'Brasil')
        cpf_cnpj = request.form.get('cpf_cnpj', '')
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        how_knew = request.form.get('how_knew', '')
        terms_accepted = request.form.get('terms_accepted') == 'on'
        
        print(f"📸 Tentativa de cadastro de fotógrafo: {email}")
        
        # Validações
        if password != password_confirm:
            flash('As senhas não coincidem')
            return render_template('auth/register_photographer.html')
        
        if not terms_accepted:
            flash('Você deve aceitar os termos de uso')
            return render_template('auth/register_photographer.html')
        
        if data_manager:
            try:
                # Cria o novo usuário fotógrafo com todos os dados
                user_id = data_manager.create_user(
                    username=email,  # Usa email como username
                    password=password,
                    email=email,
                    user_type='photographer',  # Sempre fotógrafo
                    full_name=full_name,
                    cpf=clean_cpf(cpf_cnpj),
                    phone=phone
                )
                
                if user_id:
                    flash('Conta de fotógrafo criada com sucesso!')
                    print(f"✅ Fotógrafo criado com ID: {user_id}")
                    return redirect(url_for('auth.login'))
                else:
                    flash('Erro ao criar conta - usuário já existe')
                    print(f"❌ Erro ao criar fotógrafo - já existe")
            except Exception as e:
                flash(f'Erro ao criar conta: {str(e)}')
                print(f"❌ Erro ao criar fotógrafo: {e}")
        else:
            flash('Sistema de dados não disponível')
            print("❌ Sistema de dados não disponível")
    
    return render_template('auth/register_photographer.html')

@bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Logout realizado com sucesso!')
    return redirect(url_for('dashboard.index')) 