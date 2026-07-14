import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)  # Permite que tu frontend se comunique con el backend sin problemas de seguridad (CORS)

# Configuración de la base de datos
# Reemplaza la URL de abajo con tu 'External Database URL' de Render si pruebas localmente.
# En producción, es mejor usar variables de entorno.
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://saludmass_db_user:PhfB38anRIn8dGzrPxOthETZL8b4QMpC@dpg-d9b80emcjfls73e4arfg-a.oregon-postgres.render.com/saludmass_db')

# Solución para compatibilidad de esquemas en Render/Heroku (de postgres:// a postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# MODELO DE LA BASE DE DATOS (TABLA USUARIO)
# ==========================================
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    document = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "document": self.document,
            "email": self.email
        }

# Crear las tablas en la base de datos si no existen
with app.app_context():
    db.create_all()

# ==========================================
# ENDPOINTS DE LA API
# ==========================================

# Ruta de prueba para verificar que el backend está vivo
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "healthy", "message": "Servidor de SaludMass EPS funcionando correctamente"}), 200

# Endpoint de Registro
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "Datos no proporcionados"}), 400
        
    name = data.get('name')
    document = data.get('document')
    email = data.get('email')
    password = data.get('password')

    # Validaciones básicas
    if not all([name, document, email, password]):
        return jsonify({"message": "Todos los campos son obligatorios"}), 400

    # Verificar si el correo o el documento ya existen
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "El correo electrónico ya está registrado"}), 400
        
    if User.query.filter_by(document=document).first():
        return jsonify({"message": "El documento de identidad ya está registrado"}), 400

    try:
        # Crear nuevo usuario con contraseña encriptada
        new_user = User(name=name, document=document, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "message": "Usuario registrado exitosamente",
            "user": new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error al procesar el registro: {str(e)}"}), 500

# Endpoint de Inicio de Sesión (Login)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "Datos de acceso requeridos"}), 400
        
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Correo y contraseña requeridos"}), 400

    # Buscar usuario por correo
    user = User.query.filter_by(email=email).first()

    # Verificar existencia y validar contraseña encriptada
    if user and user.check_password(password):
        return jsonify({
            "message": "Acceso concedido",
            "user": user.to_dict()
        }), 200
    else:
        return jsonify({"message": "Correo electrónico o contraseña incorrectos"}), 401

# RUTA TEMPORAL DE PRUEBA: Obtener todos los usuarios registrados
@app.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        users = User.query.all()
        # Convertimos la lista de usuarios a diccionarios y la retornamos
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({"message": f"Error al obtener usuarios: {str(e)}"}), 500

if __name__ == '__main__':
    # Usar el puerto que asigne Render o el 5000 por defecto de forma local
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)