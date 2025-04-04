from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime
import os

app = Flask(__name__)

load_dotenv()

URL_SUPABASE = os.getenv("URL_SUPABASE")

app.config['SQLALCHEMY_DATABASE_URI'] = URL_SUPABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)    
    surname = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=True)
    number = db.Column(db.Integer(), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    dob = db.Column(db.Date, nullable=False)
    birthplace = db.Column(db.String(100), nullable=False)
    nationality = db.Column(db.String(100), nullable=False)
    dominant_leg = db.Column(db.String(100), nullable=True)
    is_international = db.Column(db.Boolean, nullable=False)
    is_trainer = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return f'Persona {self.name}'

@app.route('/')
def get_index():
    personas = Persona.query.all()
    return render_template("index.html", personas = personas)

@app.route('/personas_admin')
def get_personas_admin():
    personas = Persona.query.all()
    return render_template("personas_admin.html", personas = personas)

@app.route('/editar_persona/<int:id>', methods=['GET', 'POST'])
def editar_persona(id):
    persona = Persona.query.get(id)
    if not persona:
        return "Usuario no encontrado", 404
    if request.method == 'POST':
        persona.name = request.form.get('name')
        persona.surname = request.form.get('surname')
        persona.age = int(request.form.get('age'))
        persona.is_trainer = request.form.get('is_trainer')     == 'on'
        db.session.commit()
        return redirect(url_for('get_personas'))
    
    return render_template("editar_persona.html", persona = persona)

@app.route('/borrar_persona/<int:id>', methods=['GET', 'POST'])
def borrar_persona(id):
    persona = Persona.query.get(id)
    if not persona:
        return "Usuario no encontrado", 404
    db.session.delete(persona)
    db.session.commit()
    return redirect(url_for('get_personas_admin'))

@app.route('/add_persona', methods=['GET', 'POST'])
def add_persona():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        display_name = request.form.get('display_name')
        number = int(request.form.get('number')) if request.form.get('number') else None
        position = request.form.get('position')
        dob = datetime.strptime(request.form.get('dob'), "%Y-%m-%d").date()
        birthplace = request.form.get('birthplace')
        nationality = request.form.get('nationality')
        dominant_leg = request.form.get('dominant_leg')
        is_international = request.form.get('is_international') == 'on'
        is_trainer = request.form.get('is_trainer') == 'on'
        
        new_persona = Persona(
            name=name,
            surname=surname,
            display_name=display_name,
            number=number,
            position=position,
            dob=dob,
            birthplace=birthplace,
            nationality=nationality,
            dominant_leg=dominant_leg,
            is_international=is_international,
            is_trainer=is_trainer
        )
        
        db.session.add(new_persona)
        db.session.commit()

    return render_template("forms.html", type = type)


@app.route('/login')
def get_login():
    return render_template("login.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=8000, debug=True)