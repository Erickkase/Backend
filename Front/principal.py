# Importamos Flask
from flask import Flask, render_template, request, redirect, url_for
import requests
# import pandas as pd
import pyodbc
# import pymssql
from sqlalchemy import create_engine, Column, Integer, String 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String, Boolean

#Creamos la aplicaion flask
app = Flask(__name__)

# Configuración de la base de datos
#conexion_db = 'mssql+pyodbc://BD_CommentAnalize:12345678@DESKTOP-MPK3557/Comment_Analize?driver=ODBC+Driver+17+for+SQL+Server'
# conexión Duvard:
# conexion_db = 'mssql+pyodbc://sa:sql_123@DESKTOP-ITKPV5E\SQLEXPRESS/Comment_Analize?driver=ODBC+Driver+17+for+SQL+Server'
# conexion Erick
conexion_db = 'mssql+pyodbc://DESKTOP-QGQANK8\SQLEXPRESS/BD_CommentAnalize?driver=ODBC+Driver+17+for+SQL+Server'

#Confirma si la conexion es exitosa con la base de datos
if conexion_db:
    print("Conexión exitosa con la base de datos")
else:
    print("No se pudo realizar la conexión con la base de datos")  

# Crear motor (comunicación) de base de datos SQLAlchemy
engine = create_engine(conexion_db)

# Definir los datos
Base = declarative_base()

class Usuarios(Base):
    __tablename__ = 'Users'  # Nombre de la tabla y sus distintas columnas
    ID = Column(Integer, primary_key=True)
    Usuario = Column(String(50), nullable=False, unique=True)
    Password = Column(String(50), nullable=False)
    Nombres = Column(String(50), nullable=False)
    Apellidos = Column(String(50), nullable=False)

# Realizar consultas y transacciones con la bd
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


# Funciones

# Hace las peticiones de emociones de la ultima busqueda del usuario
def Emociones(usuario):
    respuesta1 = requests.get(f'http://127.0.0.1:8000/analisis/emocion/', params={
        'usuario': usuario,
    })
    return respuesta1.json()

# Hace las peticiones de sentimientos de la ultima busqueda del usuario
def Sentimientos(usuario):
    respuesta1 = requests.get(f'http://127.0.0.1:8000/analisis/sentimiento/', params={
        'usuario': usuario,
    })
    return respuesta1.json()


#Rutas del api

#Pagina Inicial
@app.route('/PaginaInicial')  # para poder referenciar en los botones de retorno (atrás)
@app.route('/')
def PaginaInicial():
    return render_template("pagina_inicial.html")

#Pagina de Inicio de Sesion
@app.route('/InicioSesion', methods=['GET', 'POST'])
def InicioSesion():
    if request.method == 'POST':

        #Toma los valores del formulario
        usuario = request.form.get('usuario')
        password = request.form.get('password')

        #Verificaciones
        if usuario and password:  # Verifica si se llenaron los campos
            user = db_session.query(Usuarios).filter_by(Usuario=usuario).first()  # Busca en la tabla Usuarios en el primer registro donde se encuentre el valor de usuario
            if user != None and user.Password == password:  # Verifica que tanto usuario existe y la contraseña coincidan 
                return redirect(url_for('Analisis', user=usuario)) #Enviamos el usuario tambien
            else:
                return render_template("inicio_sesion.html", error1="Usuario o contraseña incorrectos.")
        else:
            return render_template("inicio_sesion.html", error1="Por favor ingrese todos los campos.")
    return render_template("inicio_sesion.html")

#Pagina de Registro
@app.route('/Registrarse', methods=['GET', 'POST'])
def Registrarse():
    if request.method == 'POST':

        #Toma los valores del formulario
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        rpassword = request.form.get('rpassword')

        #Verificaciones
        if nombres and apellidos and usuario and password == rpassword:
            # Verificar si el usuario ya existe
            existe_usuario = db_session.query(Usuarios).filter_by(Usuario=usuario).first()
            if existe_usuario != None:
                return render_template("registrarse.html", error="Ese nombre de Usuario ya está en uso")
            elif password != rpassword:
                return render_template("registrarse.html", error="Las contraseñas no coinciden")
            elif len(password) < 8:
                return render_template("registrarse.html", error="La contraseña debe tener mínimo 8 caracteres")
            try:
                nuevo_usuario = Usuarios(Nombres=nombres, Apellidos=apellidos, Usuario=usuario, Password=password)
                db_session.add(nuevo_usuario)
                db_session.commit()
                return render_template("inicio_sesion.html")
            except Exception as e:
                print(e)
                return render_template("registrarse.html", error="Error al registrar el usuario.")
        else:
            return render_template("registrarse.html", error="Por favor complete todos los campos")
    return render_template("registrarse.html")

#Pagina de Analisis por Video
@app.route('/Analisis')
def Analisis():
    user = request.args.get('user')
    return render_template("Analisis.html", user=user)

#Pagina de Analisis por Canal
@app.route('/AnalisisCanal')
def AnalisisCanal():
    user = request.args.get('user')
    return render_template("AnalisisCanal.html", user=user)

#Pagina para Preguntar a la IA
@app.route('/Pregunta')
def Pregunta():
    user = request.args.get('user')
    return render_template("Pregunta.html", user=user)

#Pagina para ver Reportes de la Ultima Busqueda
@app.route('/Reportes')
def Reportes():
    user = request.args.get('user')

    #Busca los sentimientos de la busqueda del usuario
    sentimientos=Sentimientos(user)

    #Busca las emociones de la busqueda del usuario
    emociones=Emociones(user)

    return render_template("Reportes.html", user=user, sentiments=sentimientos, emotions=emociones)

#Metodo para Realizar la pregunta
@app.route('/RealizarPregunta', methods=['POST'])
def RealizarPregunta():

    #Toma los valores del formulario
    usuario = request.form.get('user')
    pregunta = request.form.get('question')

    #Hace la peticion al Backend mandandole los parametros
    respuesta2 = requests.post(f'http://127.0.0.1:8000/analisis/pregunta/', params={
        'usuario': usuario,
        'pregunta': pregunta,
    })

    #Guarda la respuesta en Json
    respuesta = respuesta2.json()

    #Retorna la peticion
    return render_template("Pregunta.html", user=usuario, answer=respuesta)

#Metodo para Analizar un Video
@app.route('/AnalizarVideo', methods=['POST'])
def AnalizarVideo():

    #Toma los valores del formulario
    usuario = request.form.get('user')
    video_url = request.form.get('video_url')
    num_comments = request.form.get('num_comments')
    
    #Hace la peticion al Backend mandandole los parametros
    respuesta=requests.get(f'http://127.0.0.1:8000/comments/top_comments/', params={
        'usuario': usuario,
        'video_url': video_url,
        'num_comments': num_comments
    })

    #Guarda la respuesta en Json
    comentarios = respuesta.json().get('comments', [])

    #Hace la peticion al Backend mandandole los parametros y la pregunta para la idea de negocio
    respuesta2 = requests.post(f'http://127.0.0.1:8000/analisis/pregunta/', params={
        'usuario': usuario,
        'pregunta': "Dame una idea de un negcio o algo que les podria vender",
    })

    #Guarda la respuesta en Json
    modeloNegocio = respuesta2.json()

    return render_template('Analisis.html', user=usuario, negocio=modeloNegocio, comments=comentarios)

#Metodo para Analizar un Canal
@app.route('/AnalizarCanal', methods=['POST'])
def AnalizarCanal():

    #Toma los valores del formulario
    usuario = request.form.get('user')
    canal = request.form.get('chanel')
    num_comments = request.form.get('num_comments')
    
    #Hace la peticion al Backend mandandole los parametros
    respuesta=requests.get(f'http://127.0.0.1:8000/comments/top_comments_latest_videos/', params={
        'usuario': usuario,
        'handle': canal,
        'num_comments_per_video': num_comments
    })

    #Guarda la respuesta en Json
    comentarios = respuesta.json().get('top_comments', [])

    #Hace la peticion al Backend mandandole los parametros
    respuesta2 = requests.post(f'http://127.0.0.1:8000/analisis/pregunta/', params={
        'usuario': usuario,
        'pregunta': "Dame una idea de un negocio o algo que les podria vender",
    })

    #Guarda la respuesta en Json
    modeloNegocio = respuesta2.json()

    return render_template('AnalisisCanal.html', user=usuario, negocio=modeloNegocio, comments=comentarios)


#Corre el programa
if __name__ == '__main__':
    app.run(debug=True, port=6020)