#Importamos Flask
from flask import Flask, render_template

#Creamos aplicacion Flask 
app = Flask(__name__)

@app.route('/')
def PaginaInicial():
    return render_template("pagina_inicial.html")

@app.route('/InicioSesion')
def InicioSesion():
    return render_template("inicio_sesion.html")

@app.route('/Registrarse')
def Registrarse():
    return render_template("registrarse.html")