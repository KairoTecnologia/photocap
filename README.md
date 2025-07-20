# PhotoCap - Sistema de Reconhecimento Facial

Sistema web para gerenciamento de fotos de eventos com reconhecimento facial, desenvolvido em Python Flask e SQL Server.

## 🚀 Funcionalidades

- ✅ Cadastro e login de usuários com senha hash + salt
- ✅ Criação e gerenciamento de eventos
- ✅ Upload de fotos para eventos
- ✅ Reconhecimento facial para busca de pessoas
- ✅ Busca de fotos por evento
- ✅ Interface web responsiva com Bootstrap 5

## 📋 Pré-requisitos

### 1. SQL Server
- SQL Server 2019 ou superior
- SQL Server Management Studio (SSMS) ou Azure Data Studio
- Driver ODBC 17 para SQL Server

### 2. Python
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 3. Dependências do Sistema
- OpenCV para processamento de imagens
- pyodbc para conexão com SQL Server

## 🛠️ Instalação

### 1. Configurar o Banco de Dados

Execute o seguinte script SQL no SQL Server Management Studio:

```sql
-- Criação do banco de dados
CREATE DATABASE PhotoCap;
GO

USE PhotoCap;
GO

-- Tabela de Usuários
CREATE TABLE Users (
    UserId INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARBINARY(256) NOT NULL,
    PasswordSalt VARBINARY(64) NOT NULL,
    Email NVARCHAR(255) NOT NULL
);
GO

-- Tabela de Eventos
CREATE TABLE Events (
    EventId INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(255) NOT NULL,
    Date DATE NOT NULL
);
GO

-- Tabela de Fotos
CREATE TABLE Photos (
    PhotoId INT IDENTITY(1,1) PRIMARY KEY,
    EventId INT NOT NULL,
    Filename NVARCHAR(255) NOT NULL,
    UploadDate DATETIME NOT NULL,
    Image VARBINARY(MAX) NULL,
    FOREIGN KEY (EventId) REFERENCES Events(EventId)
);
GO
```

### 2. Instalar Dependências Python

```bash
# Instalar as dependências
pip install -r requirements.txt
```

### 3. Configurar Conexão com Banco

Edite o arquivo `db_manager.py` e ajuste as configurações de conexão:

```python
db = DatabaseManager(
    server='localhost',        # Seu servidor SQL Server
    database='PhotoCap',       # Nome do banco criado
    username='sa',            # Seu usuário SQL Server
    password='sua_senha'      # Sua senha SQL Server
)
```

### 4. Testar a Conexão

```bash
# Executar teste de conexão
python test_db.py
```

## 🚀 Executando a Aplicação

### 1. Testar o Banco de Dados

```bash
python test_db.py
```

### 2. Executar a Aplicação Web

```bash
python app_simple_fixed.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 📁 Estrutura do Projeto

```
PhotoCap/
├── app_simple_fixed.py      # Aplicação Flask principal
├── db_manager.py            # Gerenciador de banco de dados
├── face_recognition_simple.py # Módulo de reconhecimento facial
├── test_db.py               # Script de teste do banco
├── requirements.txt         # Dependências Python
├── README.md               # Este arquivo
└── uploads/                # Pasta para uploads (criada automaticamente)
```

## 🔧 Configurações

### Configurações do Banco de Dados

No arquivo `db_manager.py`, ajuste:

```python
# Configurações de conexão
server = 'localhost'      # Endereço do SQL Server
database = 'PhotoCap'     # Nome do banco
username = 'sa'          # Usuário SQL Server
password = ''            # Senha SQL Server
```

### Configurações da Aplicação

No arquivo `app_simple_fixed.py`, você pode ajustar:

- Porta da aplicação (padrão: 5000)
- Pasta de uploads
- Configurações de debug

## 🧪 Testes

### Teste de Conexão com Banco

```bash
python test_db.py
```

### Teste de Reconhecimento Facial

```bash
python test_face_recognition.py
```

## 🔒 Segurança

- Senhas são armazenadas com hash PBKDF2 + salt
- Upload de arquivos com validação de tipo
- Sanitização de nomes de arquivo
- Validação de entrada de dados

## 🐛 Solução de Problemas

### Erro de Conexão com SQL Server

1. Verifique se o SQL Server está rodando
2. Confirme as credenciais de acesso
3. Verifique se o driver ODBC está instalado
4. Teste a conexão com: `python test_db.py`

### Erro de Módulo não Encontrado

```bash
pip install -r requirements.txt
```

### Erro de Permissão de Pasta

Certifique-se de que a pasta `uploads/` tem permissões de escrita.

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique os logs da aplicação
2. Execute os scripts de teste
3. Confirme as configurações do banco de dados

## 🔄 Próximas Melhorias

- [ ] Interface de administração
- [ ] Relatórios de eventos
- [ ] Backup automático do banco
- [ ] API REST para integração
- [ ] Sistema de notificações
- [ ] Otimização de performance 