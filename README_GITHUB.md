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

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/photocap.git
cd photocap
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o Banco de Dados

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

### 5. Configure a conexão com o banco

Edite o arquivo `config.py` e ajuste as configurações:

```python
DB_CONFIG = {
    'server': 'localhost',        # Seu servidor SQL Server
    'database': 'PhotoCap',       # Nome do banco criado
    'username': 'sa',            # Seu usuário SQL Server
    'password': 'sua_senha',     # Sua senha SQL Server
    'driver': 'ODBC Driver 17 for SQL Server'
}
```

### 6. Teste a conexão
```bash
python test_db.py
```

## 🚀 Executando a Aplicação

### Versão com SQL Server (Recomendada)
```bash
python app_sql_server.py
```

### Versão com JSON (Para testes)
```bash
python app_simple_fixed.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 📁 Estrutura do Projeto

```
PhotoCap/
├── app_sql_server.py          # Aplicação principal com SQL Server
├── app_simple_fixed.py        # Aplicação com JSON (para testes)
├── db_manager.py              # Gerenciador de banco de dados SQL Server
├── face_recognition_simple.py # Módulo de reconhecimento facial
├── test_db.py                 # Script de teste do banco
├── setup_database.py          # Script de configuração interativa
├── config.py                  # Configurações do projeto
├── requirements.txt           # Dependências Python
├── README.md                  # Documentação
├── .gitignore                 # Arquivos ignorados pelo Git
└── uploads/                   # Pasta para uploads (criada automaticamente)
```

## 🔧 Configurações

### Configurações do Banco de Dados

No arquivo `config.py`, ajuste:

```python
DB_CONFIG = {
    'server': 'localhost',      # Endereço do SQL Server
    'database': 'PhotoCap',     # Nome do banco
    'username': 'sa',          # Usuário SQL Server
    'password': '',            # Senha SQL Server
    'driver': 'ODBC Driver 17 for SQL Server'
}
```

### Configurações da Aplicação

- Porta da aplicação (padrão: 5000)
- Pasta de uploads: `uploads/`
- Tamanho máximo de upload: 100MB
- Extensões permitidas: PNG, JPG, JPEG, GIF

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
- Autenticação por e-mail

## 🐛 Solução de Problemas

### Erro de Conexão com SQL Server

1. Verifique se o SQL Server está rodando
2. Confirme as credenciais de acesso
3. Verifique se o banco de dados existe
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
4. Abra uma issue no GitHub

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🔄 Próximas Melhorias

- [ ] Interface de administração
- [ ] Relatórios de eventos
- [ ] Backup automático do banco
- [ ] API REST para integração
- [ ] Sistema de notificações
- [ ] Otimização de performance
- [ ] Suporte a múltiplos idiomas
- [ ] Sistema de tags para fotos
- [ ] Galeria de fotos melhorada
- [ ] Sistema de comentários

---

**Desenvolvido com ❤️ usando Python, Flask e SQL Server** 