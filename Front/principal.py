#Importamos Flask
from flask import Flask, render_template, request
#import pandas as pd
import pyodbc
#import pymssql
from sqlalchemy import create_engine, Column, Integer, String 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
#from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String, Boolean

app = Flask(__name__)

# Configuración de la base de datos
conexion_db = 'mssql+pyodbc://BD_CommentAnalize:12345678@DESKTOP-MPK3557/Comment_Analize?driver=ODBC+Driver+17+for+SQL+Server'

if conexion_db:
    print("Conexión exitosa con la base de datos")
else:
    print("No se pudo realizar la conexion con la base de datos")  

# Crear motor(comunicación) de base de datos SQLAlchemy
engine = create_engine(conexion_db)

#Definir los datos
Base = declarative_base()

class Usuarios(Base):
    __tablename__ = 'Users'  # Nombre de la tabla y sus distintas columnas
    ID = Column(Integer, primary_key=True)
    Usuario = Column(String(50), nullable=False, unique=True)
    Password = Column(String(50), nullable=False)
    Nombres = Column(String(50), nullable=False)
    Apellidos = Column(String(50), nullable=False)

#Realizar consultas y transacciones con la bd
Session = sessionmaker(bind=engine)
session = Session() 

@app.route('/PaginaInicial')#para poder referenciar en los botones de retorno(atras)
@app.route('/')
def PaginaInicial():
    return render_template("pagina_inicial.html")

@app.route('/InicioSesion', methods=['GET', 'POST'])
def InicioSesion():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        if usuario and password:#Verifica si se llenaron los campos
            user = session.query(Usuarios).filter_by(Usuario=usuario).first()#Busca en la tabla Usuarios en el primer registro donde se encuentre el valor de usuario
            if user != None and user.Password == password:#Verifica que tanto usuario existe y la contraseña coincidan 
                return render_template("pagina_inicial.html")
            else:
                return render_template("inicio_sesion.html", error="Usuario o contraseña incorrectos.")
        else:
            return render_template("inicio_sesion.html", error="Por favor ingrese todos los campos.")
    return render_template("inicio_sesion.html")


@app.route('/Registrarse',methods=['GET', 'POST'])
def Registrarse():
    if request.method == 'POST':
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        rpassword = request.form.get('rpassword')
        if nombres and apellidos and usuario and password == rpassword:
            # Verificar si el usuario ya existe
            existe_usuario = session.query(Usuarios).filter_by(Usuario=usuario).first()
            if existe_usuario != None:
                return render_template("registrarse.html", error="El nombre de usuario ya está en uso.")
            try:
                nuevo_usuario = Usuarios(Nombres=nombres, Apellidos=apellidos, Usuario=usuario, Password=password)
                session.add(nuevo_usuario)
                session.commit()
                return render_template("inicio_sesion.html")
            except Exception as e:
                print(e)
                return render_template("registrarse.html", error="Error al registrar el usuario.")
        else:
            return render_template("registrarse.html", error="Por favor complete todos los campos y asegúrese de que las contraseñas coincidan.")
    return render_template("registrarse.html")

@app.route('/Analisis')
def Analisis():
    return(render_template("Analisis.html"))

if __name__ == '__main__':
    app.run(debug=True, port=6020)