from flask import Flask, render_template, request, redirect, url_for
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
    nationality = db.Column(db.String(100), nullable=True)
    dominant_leg = db.Column(db.String(100), nullable=True)
    is_international = db.Column(db.Boolean, nullable=False)
    is_trainer = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return f'Persona {self.name}'

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    local_team_id = db.Column(db.Integer, db.ForeignKey('equipo.id'), nullable=False)
    visitor_team_id = db.Column(db.Integer, db.ForeignKey('equipo.id'), nullable=False)

    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(5), nullable=False)

    local_team = db.relationship('Equipo', foreign_keys=[local_team_id], backref='partidos_local')
    visitor_team = db.relationship('Equipo', foreign_keys=[visitor_team_id], backref='partidos_visitantes')

class Equipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    abbreviation = db.Column(db.String(3), nullable=False)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100), nullable=False)
    identificador = db.Column(db.String(100), nullable=False)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    in_cart = db.Column(db.Boolean, nullable=True)
    cantidad = db.Column(db.Integer, default=1)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


@app.route('/')
def get_index():
    personas = Persona.query.filter_by(is_trainer=False).order_by(Persona.number.asc()).all()
    partidos = Partido.query.order_by(Partido.date.asc()).limit(3).all()
    sponsors = os.listdir('static/img/sponsors')
    videos = Video.query.order_by(Video.id.desc()).limit(4).all()
    return render_template("index.html", personas = personas, partidos = partidos, sponsors = sponsors, videos = videos)

@app.route('/plantilla')
def get_plantilla():
    personas = Persona.query.all()
    return render_template("players/plantilla.html", personas = personas)

@app.route('/login', methods=['GET', 'POST'])
def get_login():
    if request.method == "POST":
        email_get = request.form.get('email')
        password_get = request.form.get('password')
        correo = "tongoliki@gmail.com"
        contraseña = "12345"
        if email_get == correo and password_get == contraseña:
            return redirect(url_for('get_personas_admin'))
        
    return render_template("auth/login.html")

@app.route('/admin', methods=["GET", "POST"])
def get_personas_admin():
    accion = request.args.get("accion")
    tipo = request.args.get("tipo", "personas")  # Usa 'personas' como valor por defecto
    personas = Persona.query.order_by(Persona.id.asc()).all()
    equipos = Equipo.query.order_by(Equipo.id.asc()).all()
    partidos = Partido.query.order_by(Partido.id.asc()).all()
    videos = Video.query.all()

    return render_template("admin/admin_panel.html", accion=accion, tipo=tipo, personas=personas, equipos=equipos, partidos=partidos, videos=videos)

@app.route('/forms')
def get_forms():
    accion = request.args.get("accion", None)
    tipo = request.args.get("tipo", None)
    equipos = Equipo.query.all()
    personas = Persona.query.all()
    partidos = Partido.query.all()
    videos = Video.query.all()
    return render_template("components/forms.html", accion = accion, tipo = tipo, personas = personas, equipos = equipos, partidos = partidos, videos = videos)

# --- CRUD ---

# --- PERSONAS ---
# ------ AÑADIR PERSONA ------
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
        return redirect(url_for('get_personas_admin'))

    return render_template("components/forms.html", accion = "add", tipo = "personas")

# ------ LEER PERSONA ------
@app.route('/persona/<int:id>', methods=['GET', 'POST'])
def get_persona_by_id(id):
    persona = Persona.query.get(id)
    if not persona:
        return "Persona no encontrada", 404
    else:
        return render_template("players/datos_jugador.html", persona = persona)

# ------ EDITAR PERSONA ------
@app.route('/editar_persona/<int:id>', methods=['GET', 'POST'])
def editar_persona(id):
    persona = Persona.query.get(id)
    if not persona:
        return "Usuario no encontrado", 404
    if request.method == 'POST':
        persona.name = request.form.get('name')
        persona.surname = request.form.get('surname')
        persona.display_name = request.form.get('display_name')
        persona.number = int(request.form.get('number')) if request.form.get('number') else None
        persona.position = request.form.get('position')
        persona.dob = datetime.strptime(request.form.get('dob'), "%Y-%m-%d").date()
        persona.birthplace = request.form.get('birthplace')
        persona.nationality = request.form.get('nationality')
        persona.dominant_leg = request.form.get('dominant_leg')
        persona.is_international = request.form.get('is_international') == 'on'
        persona.is_trainer = request.form.get('is_trainer') == 'on'

        db.session.commit()
        return redirect(url_for('get_personas_admin'))
    
    return render_template("components/forms.html", accion = "edit", tipo = "personas", persona = persona)

# ------ BORRAR PERSONA ------
@app.route('/borrar_persona/<int:id>', methods=['GET', 'POST'])
def borrar_persona(id):
    persona = Persona.query.get(id)
    if not persona:
        return "Persona no encontrada", 404
    db.session.delete(persona)
    db.session.commit()
    return redirect(url_for('get_personas_admin'))



# --- PARTIDOS ---
# ------ AÑADIR PARTIDO ------
@app.route('/add_partido', methods=['GET', 'POST'])
def add_partido():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        local_team_id = request.form.get('local_team_id')
        visitor_team_id = request.form.get('visitor_team_id')
        date_str = request.form.get('date')
        time_str = request.form.get('time')

        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        time = time_str

        new_partido = Partido(
            name=name,
            location=location,
            local_team_id=local_team_id,
            visitor_team_id=visitor_team_id,
            date=date,
            time=time,
        )

        db.session.add(new_partido)
        db.session.commit()
        return redirect(url_for('get_personas_admin'))

    return render_template("components/forms.html", accion = "add", tipo = "partidos", equipos = Equipo.query.all())

# ------ EDITAR PARTIDO ------
@app.route('/editar_partido/<int:id>', methods=['GET', 'POST'])
def editar_partido(id):
    partido = Partido.query.get(id)
    if not partido:
        return "Partido no encontrado", 404

    if request.method == 'POST':
        partido.name = request.form.get('name')
        partido.location = request.form.get('location')
        partido.local_team_id = request.form.get('local_team_id')
        partido.visitor_team_id = request.form.get('visitor_team_id')
        partido.date = datetime.strptime(request.form.get('date'), "%Y-%m-%d").date()
        partido.time = request.form.get('time')
        db.session.commit()
        return redirect(url_for('get_personas_admin', tipo='partidos'))

    equipos = Equipo.query.all()
    return render_template("components/forms.html", accion = "edit", tipo = "partidos", partido=partido, equipos=equipos)

# ------ BORRAR PARTIDO ------
@app.route('/borrar_partido/<int:id>', methods=['POST'])
def borrar_partido(id):
    partido = Partido.query.get(id)
    if not partido:
        return "Partido no encontrado", 404
    db.session.delete(partido)
    db.session.commit()
    return redirect(url_for('get_personas_admin', tipo='partidos'))



# --- EQUIPOS ---
# ------ AÑADIR EQUIPO ------
@app.route('/add_equipo', methods=['GET', 'POST'])
def add_equipo():
    if request.method == 'POST':
        name = request.form.get('name')
        abbreviation = request.form.get('abbreviation')

        new_equipo = Equipo(
            name=name,
            abbreviation=abbreviation,
        )

        db.session.add(new_equipo)
        db.session.commit()
        return redirect(url_for('get_personas_admin'))

    return render_template("components/forms.html", accion = "add", tipo = "equipos")

# ------ EDITAR EQUIPO ------
@app.route('/editar_equipo/<int:id>', methods=['GET', 'POST'])
def editar_equipo(id):
    equipo = Equipo.query.get_or_404(id)
    if request.method == 'POST':
        equipo.name = request.form.get('name')
        equipo.abbreviation = request.form.get('abbreviation')
        db.session.commit()
        return redirect(url_for('get_personas_admin', tipo='equipos'))
    return render_template("components/forms.html", accion = "edit", tipo = "equipos", equipo = equipo)

# ------ BORRAR EQUIPO ------
@app.route('/borrar_equipo/<int:id>', methods=['POST'])
def borrar_equipo(id):
    equipo = Equipo.query.get_or_404(id)
    db.session.delete(equipo)
    db.session.commit()
    return redirect(url_for('get_personas_admin', tipo='equipos'))



# --- VIDEOS ---
# ------ AÑADIR VIDEO ------
@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    if request.method == 'POST':
        url = request.form.get('url')

        if '/' in url:
            identificador = url.split('/')[-1]
        else:
            return "URL inválida", 400

        new_video = Video(
            url=url,
            identificador=identificador
        )

        db.session.add(new_video)
        db.session.commit()
        return redirect(url_for('get_personas_admin'))

    return render_template("components/forms.html", accion = "add", tipo = "videos")


# --- EDITAR VIDEO ---
@app.route('/editar_video/<int:id>', methods=['GET', 'POST'])
def editar_video(id):
    video = Video.query.get(id)
    if not video:
        return "Vídeo no encontrado", 404

    if request.method == 'POST':
        video.url = request.form.get('url')
        db.session.commit()
        return redirect(url_for('get_personas_admin', tipo='videos'))

    return render_template("components/forms.html", accion = "edit", tipo = "videos", video = video)


# --- BORRAR VIDEO ---
@app.route('/borrar_video/<int:id>', methods=['POST'])
def borrar_video(id):
    video = Video.query.get(id)
    if not video:
        return "Vídeo no encontrado", 404
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for('get_personas_admin', tipo='videos'))




# ----------- TIENDA ------------

# ver tienda - index
user_login = False
@app.route('/tienda/', methods=['GET', 'POST'])
def mostrar_inicio():
    global user_login

    if request.method == 'POST':
        mail = request.form.get('mail')
        password = request.form.get('password')
        user = Usuario.query.filter_by(mail=mail, password=password).first()
        
        if user:
            user_login = True

    productos = Producto.query.order_by(Producto.id.asc()).all()
    return render_template("tienda/tienda_index.html", productos=productos, user_login=user_login)



# registrar usuario
@app.route('/tienda/register', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        
        new_user = Usuario(
            mail=mail,
            password=password
        )
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('mostrar_inicio'))

    return render_template("tienda/tienda_register.html")


# admin tienda
@app.route('/tienda/admin', methods=["GET", "POST"])
def get_productos_admin():
    productos = Producto.query.order_by(Producto.id.asc()).all()
    usuarios = Usuario.query.order_by(Usuario.id.asc()).all()
    return render_template("tienda/plantillas_back/admin.html", productos=productos, usuarios=usuarios)




# formulario para añadir productos

@app.route('/tienda/add_producto', methods=['GET', 'POST'])
def add_producto():
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('desc')
        price = request.form.get('price')
        
        
        new_producto = Producto(
            name=name,
            desc=desc,
            price=price
        )
        
        db.session.add(new_producto)
        db.session.commit()
        return redirect(url_for('mostrar_inicio'))

    return render_template("tienda/formularios_back/add_producto.html")


# borrar productos
@app.route('/tienda/borrar_producto/<int:id>', methods=['GET', 'POST'])
def borrar_producto(id):
    producto = Producto.query.get(id)
    if not producto:
        return "producto no encontrado", 404
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for('get_productos_admin'))



# editar productos
@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = Producto.query.get(id)
    if not producto:
        return "producto no encontrado", 404
    if request.method == 'POST':
        producto.name = request.form.get('name')
        producto.desc = request.form.get('desc')
        producto.price = request.form.get('price')
        db.session.commit()
        return redirect(url_for('get_productos_admin'))
    
    return render_template("tienda/formularios_back/editar_producto.html", producto=producto)

# añadir productos al carrito
@app.route('/añadir_al_carrito/<int:producto_id>', methods=['POST'])
def añadir_al_carrito(producto_id):
    global user_login

    if user_login:
        producto = Producto.query.get(producto_id)
        if producto:
            producto.in_cart = True
            db.session.commit()
    
    return redirect(url_for('mostrar_inicio'))

# carrito
@app.route('/tienda/carrito', methods=['GET', 'POST'])
def ver_carrito():
    global user_login

    if not user_login:
        return redirect(url_for('mostrar_inicio'))

    productos_en_carrito = Producto.query.filter_by(in_cart=True).all()
    precio_total = None

    if request.method == 'POST':
        if 'actualizar' in request.form:
            producto_id = int(request.form['actualizar'])
            cantidad = int(request.form.get(f'cantidad_{producto_id}'))
            
            producto = Producto.query.get(producto_id)
            if producto:
                producto.cantidad = cantidad
                db.session.commit()

        elif 'eliminar' in request.form:
            producto_id = int(request.form['eliminar'])
            
            producto = Producto.query.get(producto_id)
            if producto:
                producto.in_cart = False
                db.session.commit()

        elif 'checkout' in request.form:
            total = 0
            for producto in productos_en_carrito:
                total += producto.price * producto.cantidad
            precio_total = total

        return render_template("tienda/tienda_carrito.html", productos_en_carrito=productos_en_carrito, precio_total=precio_total)

    return render_template("tienda/tienda_carrito.html", productos_en_carrito=productos_en_carrito)




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)