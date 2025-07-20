# 📸 PhotoCap - Guia de Instalação

## 🚀 Instalação Rápida

### 1. Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 2. Clone ou baixe o projeto
```bash
# Se você já tem o projeto, navegue até a pasta
cd PhotoCap
```

### 3. Crie um ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

### 5. Execute a aplicação
```bash
python run.py
```

### 6. Acesse no navegador
Abra: http://localhost:5000

## 🔧 Configuração Avançada

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///photocap.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
FACE_RECOGNITION_TOLERANCE=0.6
OCR_CONFIDENCE_THRESHOLD=0.5
```

### Instalação do Tesseract (OCR)
Para o reconhecimento de números funcionar corretamente:

#### Windows:
1. Baixe o Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Instale e adicione ao PATH
3. Reinicie o terminal

#### Linux:
```bash
sudo apt-get install tesseract-ocr
```

#### Mac:
```bash
brew install tesseract
```

## 🎯 Funcionalidades

### Para Clientes:
- ✅ Busca por nome do evento
- ✅ Reconhecimento facial (envie uma foto sua)
- ✅ Busca por número de peito
- ✅ Visualização de fotos
- ✅ Sistema de compra

### Para Fotógrafos:
- ✅ Upload de fotos
- ✅ Criação de eventos
- ✅ Processamento automático de faces e números
- ✅ Dashboard de gerenciamento

## 🐛 Solução de Problemas

### Erro ao instalar dlib:
```bash
# Windows - instale o Visual Studio Build Tools primeiro
# Linux/Mac
sudo apt-get install cmake
pip install dlib
```

### Erro de permissão:
```bash
# Linux/Mac
chmod +x run.py
```

### Porta já em uso:
```bash
# Mude a porta no arquivo run.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📁 Estrutura do Projeto

```
PhotoCap/
├── app/
│   ├── templates/          # Templates HTML
│   ├── static/            # CSS, JS, imagens
│   ├── models/            # Modelos do banco
│   ├── routes/            # Rotas da aplicação
│   └── services/          # Serviços (IA, etc.)
├── uploads/               # Fotos enviadas
├── migrations/            # Migrações do banco
├── app.py                 # Aplicação principal
├── run.py                 # Script de execução
├── config.py              # Configurações
├── requirements.txt       # Dependências
└── README.md             # Documentação
```

## 🎉 Pronto!

Agora você pode:
1. Cadastrar como fotógrafo e enviar fotos
2. Cadastrar como cliente e buscar fotos
3. Testar o reconhecimento facial
4. Testar a detecção de números

## 📞 Suporte

Se encontrar problemas:
1. Verifique se todas as dependências foram instaladas
2. Confirme se o Tesseract está instalado
3. Verifique os logs no terminal
4. Consulte a documentação das bibliotecas 