#Importamos Flask
from flask import Flask, render_template

#Creamos aplicacion Flask 
app = Flask(__name__)

@app.route('/PaginaInicial')#para poder referenciar en los botones de retorno(atras)
@app.route('/')
def PaginaInicial():
    return render_template("pagina_inicial.html")

@app.route('/InicioSesion')
def InicioSesion():
    return render_template("inicio_sesion.html")

@app.route('/Registrarse')
def Registrarse():
    return render_template("registrarse.html")

if __name__ == '__main__':
    app.run(debug=True, port=6020)