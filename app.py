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
        return jsonify({"erro": "O campo 'prompt' é obrigatório"}), 400
    
    novo_item = Task(importance=dados.get('importance'), prompt=dados.get('prompt'))
    db.session.add(novo_item)
    db.session.commit()
    return jsonify(novo_item.to_dict()), 201

@app.route('/items/delete_all', methods=['DELETE'])
def delete_all():
    try:
        # Apaga todos os registos da tabela Task
        db.session.query(Task).delete()
        db.session.commit()
        return jsonify({"mensagem": "Todos os itens foram apagados!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Task.query.get(item_id) # Procura o item pelo ID
    if not item:
        return jsonify({"erro": "Item não encontrado"}), 404
    
    db.session.delete(item) # Marca para apagar
    db.session.commit() # Confirma a alteração na DB
    return jsonify({"mensagem": "Item apagado com sucesso!"}), 200

if __name__ == '__main__':
    app.run(debug=True)