#Libreria para integrar Mongo en Python
from pymongo import MongoClient

#Uri para la conexion con la base de datos remota Mongo 
uri = "mongodb+srv://desarrollo:erickh1@proyecto.dwxqnpl.mongodb.net/?retryWrites=true&w=majority&appName=Proyecto"

#Creacion del objeto que manejara las transacciones
db_client = MongoClient(uri).dbproyecto