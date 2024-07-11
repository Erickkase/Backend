#Importamos Flask
from flask import Flask, render_template
# Para leer la base de datos
# Falta commentar para que sirve cada una
# Instalar en tu entorno
# Ademas Estar seguros de que tenemos el OBC Driver 17 para SQL server
import pandas as pd
import pyodbc
# import pymssql
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String, Boolean


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

app = Flask(__name__)

@app.route('/PaginaInicial')#para poder referenciar en los botones de retorno(atras)
@app.route('/')
def PaginaInicial():
    
    conexion_exitosa = conexion() # Conexión a la BD

    return render_template("pagina_inicial.html")

@app.route('/InicioSesion')
def InicioSesion():
    return render_template("inicio_sesion.html")

@app.route('/Registrarse')
def Registrarse():
    return render_template("registrarse.html")

if __name__ == '__main__':
    app.run(debug=True, port=6020)