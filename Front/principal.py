#Importamos Flask
from flask import Flask, render_template

#Creamos aplicacion Flask 
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("")

@app.route('/InicioSesion')
def InicioSesion():
    return render_template("")
