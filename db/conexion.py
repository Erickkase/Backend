#Libreria para integrar Mongo en Python
from pymongo import MongoClient

#Uri para la conexion con la base de datos remota Mongo 
uri = "mongodb+srv://erikkase:Iet0V954YzKiQahB@proyecto.7rpac7a.mongodb.net/?retryWrites=true&w=majority&appName=Proyecto"

#Creacion del objeto que manejara las transacciones
db_client = MongoClient(uri).dbproyecto