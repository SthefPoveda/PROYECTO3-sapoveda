from flask import Flask, request,render_template, redirect,session, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:Colombia2026+@localhost:3306/heladeria'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'


class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100))
    es_admin = db.Column(db.Integer, default=False)
    es_empleado = db.Column(db.Integer, default=False)

    def __init__(self,username,password,es_admin,es_empleado):
        self.username = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.es_admin = es_admin
        self.es_empleado = es_empleado
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

with app.app_context():
    db.create_all()


class Ingredientes(db.Model):
        __tablename__='ingredientes'
        id = db.Column(db.Integer, primary_key=True)
        calorias = db.Column(db.Integer, nullable=False)
        precio = db.Column(db.Integer, nullable=False)
        nombre = db.Column(db.String(50), nullable=False)
        inventario = db.Column(db.Integer, nullable=False)
        es_vegetariano = db.Column(db.Integer, nullable=False)
    
        def __init__(self, precio:int, calorias:int, nombre:str, inventario:int, es_vegetariano:bool):
            self._precio = precio
            self._calorias = calorias
            self._nombre = nombre
            self._inventario = inventario
            self._es_vegetariano = es_vegetariano

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        es_admin = request.form.get('es_admin', 0)  
        es_empleado = request.form.get('es_empleado', 0) 

        new_user = Usuarios(username=username, password=password, es_admin=es_admin, es_empleado=es_empleado)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Usuarios.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['username'] = user.username
            return redirect('/dashboard')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if session['username']:
        user = Usuarios.query.filter_by(username=session['username']).first()
        return render_template('dashboard.html',user=user)
    
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect('/login')

@app.route('/usuarios')
def mostrar_usuarios():
    usuarios = Usuarios.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/ingrediente')
def ingrediente():
   ingredientes = Ingredientes.query.all() 
   return render_template('ingredientes.html', ingredientes = ingredientes)

@app.route('/ingredientebuscar')
def ingrediente_filtro():
   ingredientebuscar = Ingredientes.query.all() 
   return render_template('ingredientebuscar.html', ingredientebuscar = ingredientebuscar)

@app.route('/buscar', methods=['GET'])
def buscar_ingrediente():
    id_ingrediente = request.args.get('id')
    ingrediente = Ingredientes.query.get(id_ingrediente)
    return render_template('resultado.html', ingredientes=ingrediente)

@app.route('/ingredientebuscar_nombre')
def ingrediente_filtro_nombre():
   ingredientebuscar_nombre = Ingredientes.query.all() 
   return render_template('buscar_nombre.html', ingredientebuscar_nombre = ingredientebuscar_nombre)

@app.route('/buscar_nombre', methods=['GET'])
def buscar_ingrediente_nombre():
    nombre_ingrediente = request.args.get('nombre')
    ingrediente_nombre = Ingredientes.query.filter_by(nombre=nombre_ingrediente).first()
    return render_template('resultado.html', ingredientes=ingrediente_nombre)


@app.route('/ingredientesano')
def ingrediente_sano():
   ingredientebuscar = Ingredientes.query.all() 
   return render_template('ingredientesano.html', ingredientebuscar = ingredientebuscar)

@app.route('/buscar_sano', methods=['GET'])
def buscar_ingrediente_sano():
    id_ingrediente = request.args.get('id')
    ingrediente = Ingredientes.query.get(id_ingrediente)
    return render_template('resultado_sano.html', ingredientes=ingrediente)

@app.route('/new', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        precio = request.form['precio']
        calorias = request.form['calorias']
        nombre = request.form['nombre']
        inventario = request.form['inventario']
        es_vegetariano = request.form['es_vegetariano']

        new_contact = Ingredientes(precio, calorias, nombre, inventario, es_vegetariano)
        db.session.add(new_contact)
        db.session.commit()

        flash('¡El ingrediente se ha ingresado satisfactoriamente!')

        return redirect(url_for('ingredientes.index'))

@app.route("/update/<string:id>", methods=["GET", "POST"])
def update(id):
    print(id)
    ingrediente = Ingredientes.query.get(id)

    if request.method == "POST":
        ingrediente.precio = request.form['precio']
        ingrediente.calorias = request.form['calorias']
        ingrediente.nombre = request.form['nombre']
        ingrediente.inventario = request.form['inventario']
        ingrediente.es_vegetariano = request.form['es_vegetariano']
        db.session.commit()

        flash('¡El ingrediente se ha actualizado satisfactoriamente!')

        return redirect('../ingrediente')

    return render_template("update.html", ingrediente=ingrediente)


@app.route("/delete/<id>", methods=["GET"])
def delete(id):
    ingrediente = Ingredientes.query.get(id)
    db.session.delete(ingrediente)
    db.session.commit()

    flash('¡El ingrediente se ha eliminado satisfactoriamente!')

    return redirect(url_for('ingredientes.index'))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

