from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Administrador:Integracion2025%25@clinicadb.postgres.database.azure.com:5432/clinicaDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos de datos
class Medico(db.Model):
    __tablename__ = 'medicos'
    id_medico = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    especialidad = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)

class Horario(db.Model):
    __tablename__ = 'horarios'
    id_horario = db.Column(db.Integer, primary_key=True)
    id_medico = db.Column(db.Integer, db.ForeignKey('medicos.id_medico'))
    dia_semana = db.Column(db.String(20))
    hora_inicio = db.Column(db.Time)
    hora_salida = db.Column(db.Time)
    activo = db.Column(db.Boolean, default=True)

class User(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    correo = db.Column(db.String(120), unique=True)

# Endpoints de la API
@app.route('/api/medico/<int:id_medico>/horarios', methods=['GET'])
def get_horarios_medico(id_medico):
    try:
        horarios = Horario.query.filter(
            Horario.id_medico == id_medico,
            Horario.activo == True
        ).order_by(
            Horario.dia_semana,
            Horario.hora_inicio
        ).all()

        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        horarios_formateados = []
        
        for horario in horarios:
            dia_nombre = horario.dia_semana if horario.dia_semana in dias_semana else str(horario.dia_semana)
            horario_data = {
                'diaSemana': dia_nombre,
                'horaInicio': horario.hora_inicio.strftime('%H:%M'),
                'horaSalida': horario.hora_salida.strftime('%H:%M'),
                'idHorario': str(horario.id_horario)
            }
            horarios_formateados.append(horario_data)
        
        return jsonify(horarios_formateados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medicos', methods=['GET'])
def api_listar_medicos():
    try:
        medicos = db.session.query(Medico, User).join(User).all()
        medicos_formateados = []
        for medico, usuario in medicos:
            medico_data = {
                'id': str(medico.id_medico),
                'nombre': f"{usuario.nombre} {usuario.apellido}",
                'especialidad': medico.especialidad,
                'activo': medico.activo
            }
            medicos_formateados.append(medico_data)
        return jsonify(medicos_formateados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medico/<int:id_medico>', methods=['GET'])
def api_detalle_medico(id_medico):
    try:
        medico = Medico.query.get_or_404(id_medico)
        usuario = User.query.get(medico.id_usuario)
        
        return jsonify({
            'id': str(medico.id_medico),
            'nombre': f"{usuario.nombre} {usuario.apellido}",
            'especialidad': medico.especialidad,
            'activo': medico.activo
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medico', methods=['POST'])
def api_registrar_medico():
    try:
        data = request.get_json()
        nuevo_medico = Medico(
            id_usuario=data['id_usuario'],
            especialidad=data['especialidad'],
            activo=True
        )
        db.session.add(nuevo_medico)
        db.session.commit()
        return jsonify({'message': 'Médico registrado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/medico/<int:id_medico>/disponibilidad', methods=['PUT'])
def api_actualizar_disponibilidad(id_medico):
    try:
        medico = Medico.query.get_or_404(id_medico)
        data = request.get_json()
        medico.activo = data['activo']
        db.session.commit()
        return jsonify({'message': 'Disponibilidad actualizada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/medico/<int:id_medico>/inhabilitar', methods=['PUT'])
def api_inhabilitar_medico(id_medico):
    try:
        medico = Medico.query.get_or_404(id_medico)
        medico.activo = False
        db.session.commit()
        return jsonify({'message': 'Médico inhabilitado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
