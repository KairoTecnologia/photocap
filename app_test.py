from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_key'

# Rota simples para testar
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PhotoCap - Teste</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-8 text-center">
                    <h1 class="text-primary mb-4">
                        <i class="fas fa-camera"></i> PhotoCap
                    </h1>
                    <h2>🎉 Aplicação Funcionando!</h2>
                    <p class="lead">O projeto PhotoCap está rodando com sucesso!</p>
                    
                    <div class="row mt-5">
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-body">
                                    <h5>✅ Flask</h5>
                                    <p>Framework web funcionando</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-body">
                                    <h5>✅ Bootstrap</h5>
                                    <p>Interface responsiva</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-body">
                                    <h5>✅ Python</h5>
                                    <p>Backend operacional</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <h4>Próximos Passos:</h4>
                        <ul class="list-unstyled">
                            <li>📸 Instalar bibliotecas de IA (OpenCV, face-recognition)</li>
                            <li>🗄️ Configurar banco de dados</li>
                            <li>👥 Implementar sistema de usuários</li>
                            <li>🔍 Adicionar reconhecimento facial</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 Iniciando PhotoCap...")
    print("✅ Aplicação funcionando!")
    print("🌐 Acesse: http://localhost:5000")
    print("📸 Funcionalidades disponíveis:")
    print("   - Interface web básica")
    print("   - Bootstrap CSS")
    print("   - Estrutura pronta para IA")
    print("\nPressione Ctrl+C para parar o servidor.")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 