#Importamos Flask
from flask import Flask, render_template, request
# Para leer la base de datos
# Falta commentar para que sirve cada una
# Instalar en tu entorno
# Ademas Estar seguros de que tenemos el OBC Driver 17 para SQL server
import pandas as pd
import pyodbc
#import pymssql
from sqlalchemy import create_engine, Column, Integer, String 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
#from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String, Boolean

app = Flask(__name__)


def conexion():
    # Conexion con nuestros datos
    server = 'DESKTOP-MPK3557'
    bd = 'Comment_Analize'
    user = 'BD_CommentAnalize'
    password = '12345678'
    try:
        conexion2 = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={bd};'
            f'UID={user};'
            f'PWD={password}'
        )
        print("Conexion exitosa con la BD")
    except pyodbc.Error as error:
        print("No se establecio conexion con BD")
        print(error)

# Configuración de la base de datos
DATABASE_URI = 'mssql+pyodbc://BD_CommentAnalize:12345678@DESKTOP-MPK3557/Comment_Analize?driver=ODBC+Driver+17+for+SQL+Server'

if DATABASE_URI:
    print("Conexion 2")
else:
    print(" No hay Conexion 2")  
# Crear motor de base de datos SQLAlchemy
engine = create_engine(DATABASE_URI)

Base = declarative_base()

class Usuarios(Base):
    __tablename__ = 'Users'  # Nombre de la tabla existente
    ID = Column(Integer, primary_key=True)
    Usuario = Column(String(50), nullable=False)
    Password = Column(String(50), nullable=False)
    Nombre_Completo = Column(String(50), nullable=False)

#Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

@app.route('/PaginaInicial')#para poder referenciar en los botones de retorno(atras)
@app.route('/')
def PaginaInicial():
    
    conexion_exitosa = conexion() # Conexión a la BD

    return render_template("pagina_inicial.html")

@app.route('/InicioSesion')
def InicioSesion():
    return render_template("inicio_sesion.html")

@app.route('/Registrarse',methods=['GET', 'POST'])
def Registrarse():
    if request.method == 'POST':
        nombres = request.form.get('nombres')
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        rpassword = request.form.get('rpassword')
        if nombres and usuario and password == rpassword:
            try:
                nuevo_usuario = Usuarios(Usuario=usuario, Password=password, Nombre_Completo=nombres)
                session.add(nuevo_usuario)
                session.commit()
                return render_template("inicio_sesion.html")
            except Exception as e:
                print(e)
                return render_template("registrarse.html")
        else:
            return render_template("registrarse.html")

    return render_template("registrarse.html")

if __name__ == '__main__':
    app.run(debug=True, port=6020)