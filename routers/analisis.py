# Importación de las bibliotecas necesarias
from fastapi import APIRouter, HTTPException  # Para definir rutas y manejar excepciones en FastAPI
from db.conexion import db_client  # Importa el cliente de la base de datos desde el módulo de conexión
from pysentimiento import create_analyzer  # Para crear analizadores de sentimientos y emociones
from openai import OpenAI  # Para interactuar con la API de OpenAI
from dotenv import load_dotenv  # Para cargar variables de entorno desde un archivo .env
import os  # Para trabajar con las variables de entorno del sistema

# Configuración del cliente de OpenAI con la clave API
client = OpenAI(
    api_key="OPEN_API_KEY",
)

# Crea el analizador de sentimientos en español
analyzer = create_analyzer(task="sentiment", lang="es")

# Crea el analizador de emociones en español
emotion_analyzer = create_analyzer(task="emotion", lang="es")

# Definición del router para las rutas de la API con prefijo "/analisis" y etiquetas
router = APIRouter(prefix="/analisis", tags=["analisis"], responses={404: {"message": "No encontrado"}})

# Funciones

# Función para obtener la última búsqueda del usuario desde la base de datos
def obtener_ultima_busqueda(usuario: str):

    #Se crea la peticion para buscar el usuario en la base de datos por Mongo
    user_document = db_client.usuarios.find_one(
        {"usuario": usuario},
        {"busquedas": {"$slice": -1}}  # Recupera la última búsqueda
    )

    #Si en el usuario no se encuentran busquedas nos mostrara que no se encontraros busquedas para este usuario
    if not user_document or "busquedas" not in user_document or not user_document["busquedas"]:
        raise HTTPException(status_code=404, detail="No se encontraron búsquedas para este usuario.")

    #Se guarda la ultima busqueda en la lista para analizarla
    ultima_busqueda = user_document["busquedas"][0]


    #Si la ultima solicitud fue latest_videos me mostrara un mensaje de No se encontraron comentarios de su búsqueda, solo videos, ya que solo se muestran videos 
    if ultima_busqueda["solicitud"] == "latest_videos":
        return {
            "message": "No se encontraron comentarios de su búsqueda, solo videos.",
        }

    #Retorna la ultima busqueda del usuario
    return {"ultima_busqueda": ultima_busqueda}


#Rutas del api

# Ruta para recuperar la última búsqueda del usuario
@router.get("/ultima_busqueda/")
async def ultima_busqueda(usuario: str):
    return obtener_ultima_busqueda(usuario)

# Ruta para realizar una pregunta basada en los comentarios obtenidos recientemente
@router.post("/pregunta/")
async def pregunta(usuario: str, pregunta: str):
    # Obtiene la última búsqueda del usuario
    ultima_busqueda = obtener_ultima_busqueda(usuario)

    # Verifica si hubo algún error al obtener la última búsqueda
    if isinstance(ultima_busqueda, dict) and "message" in ultima_busqueda:
        return ultima_busqueda

    # Crea la lista de los textos de los comentarios
    comentarios_text = []

    # Extrae los comentarios de la última búsqueda
    comentarios = ultima_busqueda["ultima_busqueda"].get("comentarios", [])

    # Agrega a la lista solo los textos de los comentarios
    for comentario in comentarios:
        if "text" in comentario:
            comentarios_text.append(comentario["text"])

    # Coloca al contexto todos los textos de los comentarios
    context = "\n".join(comentarios_text)

    # Haremos la consulta a open ai 
    try:
        # Realiza una consulta a la API de OpenAI con los comentarios como contexto
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  #Modelo con el que se va a trabajar
            temperature=0.3, # La temperatura de la respuesta que solicitemos
            messages=[
                {"role": "user", "content": f"En Base a estos Comentarios: {context} responde la Pregunta: {pregunta} "},
            ], # Se pasa el contexto de la pregunta
        )

        # De la respuesta solo cogemos el contenido del mensaje y lo guardamos en la variable
        respuesta_openai = response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)} # Si ocurre un error nos devuelve el error

    #Retorna la respuesta
    return {"respuesta": respuesta_openai}

# Ruta para obtener el análisis de sentimientos de los comentarios de la última búsqueda del usuario
@router.get("/sentimiento/")
async def sentimiento(usuario: str):

    # Obtiene la ultima busqueda del usuario
    ultima_busqueda = obtener_ultima_busqueda(usuario)

    # Verifica si hubo algún error al obtener la última búsqueda  o si esta un mensaje
    if isinstance(ultima_busqueda, dict) and "message" in ultima_busqueda:
        return ultima_busqueda

    # Se crea una lista para los comentarios
    comentarios_text = []

    # De la ultima busqueda se extraen los comentarios
    comentarios = ultima_busqueda["ultima_busqueda"].get("comentarios", [])

    #De los comentarios extraemos el Texto
    for comentario in comentarios:
        if "text" in comentario:
            comentarios_text.append(comentario["text"])

    # Inicializamos los contadores para los diferentes sentimientos
    contador_pos = 0
    contador_neg = 0
    contador_neu = 0

    # Por cada comentario va a predecir el sentimiento y añadir 1 al contador si lo encuentra
    for texto in comentarios_text:
        # Predice el sentimiento del comentario
        resultado = analyzer.predict(texto)

        # Extrae el sentimeinto del resultado
        sentimiento = resultado.output

        # Lo coloca correctamente en nuestros contadores
        if sentimiento == "POS":
            contador_pos += 1
        elif sentimiento == "NEG":
            contador_neg += 1
        elif sentimiento == "NEU":
            contador_neu += 1

    # Retorna la respuesta del analisis
    return {
        "positivos": contador_pos,
        "negativos": contador_neg,
        "neutros": contador_neu
    }

# Ruta para obtener el análisis de emociones de los comentarios de la última búsqueda del usuario
@router.get("/emocion/")
async def emocion(usuario: str):

    # Obtiene la ultima busqueda del usuario
    ultima_busqueda = obtener_ultima_busqueda(usuario)

    # Verifica si hubo algún error al obtener la última búsqueda o si esta un mensaje
    if isinstance(ultima_busqueda, dict) and "message" in ultima_busqueda:
        return ultima_busqueda

    # Se crea una lista para los comentarios
    comentarios_text = []

    # De la ultima busqueda se extraen los comentarios
    comentarios = ultima_busqueda["ultima_busqueda"].get("comentarios", [])

    #De los comentarios extraemos el Texto
    for comentario in comentarios:
        if "text" in comentario:
            comentarios_text.append(comentario["text"])

    # Diccionario para contar las diferentes emociones
    emociones = {
        "alegría": 0,
        "ira": 0,
        "sorpresa": 0,
        "disgusto": 0,
        "tristeza": 0,
        "miedo": 0,
        "otros": 0
    }

    # Por cada comentario va a predecir el sentimiento y añadir 1 al contador si lo encuentra
    for texto in comentarios_text:

        # Predice la emoción del comentario
        resultado = emotion_analyzer.predict(texto)

        # Guarda la emocion del resultado
        emocion = resultado.output

        # Compara la emocion para aumentar uno al contador
        if emocion == "joy":
            emociones["alegría"] += 1
        elif emocion == "anger":
            emociones["ira"] += 1
        elif emocion == "surprise":
            emociones["sorpresa"] += 1
        elif emocion == "disgust":
            emociones["disgusto"] += 1
        elif emocion == "sadness":
            emociones["tristeza"] += 1
        elif emocion == "fear":
            emociones["miedo"] += 1
        else:
            emociones["otros"] += 1

    # Retorna las emociones
    return emociones