from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from src.llm_service import LLMService
from src.code_analyzer import CodeAnalyzer

app = Flask(__name__, template_folder='front', static_folder='front/static')
load_dotenv()

# Configurações
API_KEY = os.environ.get("GEMINI_API_KEY") 
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
llm_service = LLMService(api_endpoint=API_ENDPOINT, api_key=API_KEY)
code_analyzer = CodeAnalyzer(llm_service=llm_service)

# Rotas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/refatorar', methods=['POST'])
def refatorar_codigo():
    codigo_original = request.form.get('codigo_original')
    linguagem = request.form.get('linguagem')

    if not codigo_original or not linguagem:
        return render_template('resultado.html', error=True, relatorio={"error": "Código e linguagem são obrigatórios."})

    try:
        relatorio = code_analyzer.refatorar_e_analisar(codigo_original, linguagem)
        return render_template('resultado.html', relatorio=relatorio, error=False)

    except RuntimeError as e:
        return render_template('resultado.html', error=True, relatorio={"error": str(e)})

if __name__ == '__main__':
    if not os.path.exists('src/__init__.py'):
        os.makedirs('src', exist_ok=True)
        with open('src/__init__.py', 'w') as f:
            f.write('')
            
    app.run(debug=True)