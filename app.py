import os
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Configuração do Banco de Dados
# Em produção (como no Render), ele buscará uma pasta 'data' persistente
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    importance = db.Column(db.Integer, nullable=False)
    prompt = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {"id": self.id, "importance": self.importance, "prompt": self.prompt}

with app.app_context():
    db.create_all()

# --- ROTAS DA API ---

@app.route('/')
def index():
    return jsonify({"status": "API rodando!", "backend": "Python Flask"})

@app.route('/items', methods=['GET'])
def get_items():
    items = Task.query.all()
    return jsonify([item.to_dict() for item in items])

@app.route('/items', methods=['POST'])
def add_item():
    dados = request.get_json()
    if not dados or 'prompt' not in dados:
        return jsonify({"erro": "O campo 'nome' é obrigatório"}), 400
    
    novo_item = Task(importance=dados.get('importance', 2), prompt=dados.get('prompt'))
    db.session.add(novo_item)
    db.session.commit()
    return jsonify(novo_item.to_dict()), 201

if __name__ == '__main__':
    app.run(debug=True)