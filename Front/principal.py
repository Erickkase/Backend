#Importamos Flask
from flask import Flask, render_template

#Creamos aplicacion Flask 
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("inicio_de_sesion.html")

@app.route('/Inicio')
def Inicio():
    return 'Pagina Inicio'