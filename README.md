# PhotoCap - Sistema de Gerenciamento de Fotos de Eventos

## 📋 Descrição

PhotoCap é um sistema web para gerenciamento de fotos de eventos, permitindo que fotógrafos criem eventos, façam upload de fotos e que clientes busquem e visualizem suas fotos.

## 🏗️ Estrutura do Projeto

```
PhotoCap/
├── app/                          # Aplicação Flask
│   ├── __init__.py              # Configuração da aplicação
│   ├── routes/                  # Blueprints das rotas
│   │   ├── __init__.py
│   │   ├── auth.py              # Autenticação (login, registro, logout)
│   │   ├── dashboard.py         # Dashboard e área do usuário
│   │   ├── events.py            # Criação de eventos e upload de fotos
│   │   └── search.py            # Busca por eventos e fotos
│   ├── templates/               # Templates HTML
│   │   ├── base.html            # Template base
│   │   ├── auth/                # Templates de autenticação
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── register_photographer.html
│   │   ├── dashboard/           # Templates do dashboard
│   │   │   ├── index.html
│   │   │   ├── area_fotografo.html
│   │   │   └── minha_conta.html
│   │   ├── events/              # Templates de eventos
│   │   │   ├── create_event.html
│   │   │   └── upload_photos.html
│   │   └── search/              # Templates de busca
│   │       ├── search.html
│   │       ├── event_details.html
│   │       └── face_search.html
│   └── static/                  # Arquivos estáticos
│       ├── css/
│       │   └── style.css        # Estilos personalizados
│       └── js/
│           └── main.js          # JavaScript personalizado
├── uploads/                     # Pasta para uploads de fotos
├── flask_session/               # Pasta para sessões Flask
├── db_manager.py                # Gerenciador de banco de dados
├── config.py                    # Configurações do banco
├── run.py                       # Arquivo principal para execução
├── requirements.txt             # Dependências Python
└── README.md                    # Este arquivo
```

## 🚀 Instalação e Configuração

### 1. Pré-requisitos

- Python 3.8+
- SQL Server
- Driver ODBC para SQL Server

### 2. Instalação

```bash
# Clone o repositório
git clone https://github.com/KairoTecnologia/photocap.git
cd photocap

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração do Banco de Dados

1. Configure o arquivo `config.py` com suas credenciais do SQL Server
2. Certifique-se de que o banco de dados `PhotoCap` existe no SQL Server
3. As tabelas serão criadas automaticamente na primeira execução

### 4. Executar a Aplicação

```bash
python run.py
```

A aplicação estará disponível em: http://localhost:5000

## 🔧 Funcionalidades

### 👤 Autenticação
- **Login** por email e senha
- **Registro** de clientes e fotógrafos
- **Logout** seguro
- **Sessões** persistentes

### 📸 Área do Fotógrafo
- **Criar eventos** com nome e data
- **Upload de fotos** para eventos
- **Gerenciar eventos** criados
- **Visualizar fotos** enviadas

### 🔍 Busca de Fotos
- **Buscar eventos** por nome
- **Visualizar fotos** de eventos
- **Busca facial** nas fotos
- **Download** de fotos

### 👥 Tipos de Usuário
- **Clientes**: Podem buscar e visualizar fotos
- **Fotógrafos**: Podem criar eventos e fazer upload de fotos

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python Flask
- **Banco de Dados**: SQL Server
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Autenticação**: Hash e salt com PBKDF2
- **Upload de Arquivos**: Flask-WTF
- **Sessões**: Flask-Session

## 🔒 Segurança

- Senhas hasheadas com salt usando PBKDF2
- Validação de entrada de dados
- Controle de acesso baseado em roles
- Sessões seguras
- Validação de tipos de arquivo

## 📁 Estrutura de Arquivos

### Arquivos Principais
- `run.py`: Ponto de entrada da aplicação
- `db_manager.py`: Gerenciador de banco de dados
- `config.py`: Configurações da aplicação

### Blueprints
- `auth.py`: Autenticação e registro
- `dashboard.py`: Dashboard e área do usuário
- `events.py`: Criação e gerenciamento de eventos
- `search.py`: Busca de eventos e fotos

## 🚀 Deploy

### Desenvolvimento
```bash
python run.py
```

### Produção
Para deploy em produção, configure:
1. Variáveis de ambiente para credenciais
2. WSGI server (Gunicorn, uWSGI)
3. Proxy reverso (Nginx, Apache)
4. SSL/TLS para HTTPS

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Suporte

Para suporte, entre em contato através do email: suporte@kairotecnologia.com

---

**Desenvolvido por Kairo Tecnologia** 🚀 