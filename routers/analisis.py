from fastapi import APIRouter, HTTPException
from db.conexion import db_client
from pysentimiento import create_analyzer
from openai import OpenAI
from dotenv import load_dotenv
import os


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


analyzer = create_analyzer(task="sentiment", lang="es")


router=APIRouter(prefix="/analisis",tags=["analisis"],responses={404:{"message":"No encontrado"}})

#Rutas del api

# Solicitud para recuperar la última búsqueda del usuario
@router.get("/ultima_busqueda/")
async def ultima_busqueda(usuario: str):
    return obtener_ultima_busqueda(usuario)

# Solicitud para realizar una pregunta basada en los comentarios obtenidos ultimamente
@router.post("/pregunta/")
async def pregunta(usuario: str, pregunta: str):
    ultima_busqueda = obtener_ultima_busqueda(usuario)

    if isinstance(ultima_busqueda, dict) and "message" in ultima_busqueda:
        return ultima_busqueda
    
    comentarios_text = []

    comentarios = ultima_busqueda["ultima_busqueda"].get("comentarios", [])

    for comentario in comentarios:
        if "text" in comentario:
            comentarios_text.append(comentario["text"])

    context = "\n".join(comentarios_text)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "user", "content": f"En Base a esto Comentarios: {context} responde la Pregunta: {pregunta}"},
            ],
        )
        respuesta_openai = response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}

    return {"respuesta": respuesta_openai}


@router.get("/sentimiento/")
async def sentimiento(usuario: str):
    ultima_busqueda = obtener_ultima_busqueda(usuario)

    if isinstance(ultima_busqueda, dict) and "message" in ultima_busqueda:
        return ultima_busqueda
    
    comentarios_text = []

    comentarios = ultima_busqueda["ultima_busqueda"].get("comentarios", [])

    for comentario in comentarios:
        if "text" in comentario:
            comentarios_text.append(comentario["text"])

    contador_pos = 0
    contador_neg = 0
    contador_neu = 0

    for texto in comentarios_text:
        resultado = analyzer.predict(texto)
        sentimiento = resultado.output

        if sentimiento == "POS":
            contador_pos += 1
        elif sentimiento == "NEG":
            contador_neg += 1
        elif sentimiento == "NEU":
            contador_neu += 1

    return {
        "positivos": contador_pos,
        "negativos": contador_neg,
        "neutros": contador_neu
    }
    

#Funciones
def obtener_ultima_busqueda(usuario: str):
    user_document = db_client.usuarios.find_one(
        {"usuario": usuario},
        {"busquedas": {"$slice": -1}} 
    )

    if not user_document or "busquedas" not in user_document or not user_document["busquedas"]:
        raise HTTPException(status_code=404, detail="No se encontraron búsquedas para este usuario.")

    ultima_busqueda = user_document["busquedas"][0]

    if ultima_busqueda["solicitud"] == "latest_videos":
        return {
            "message": "No se encontraron comentarios de su búsqueda, solo videos.",
        }

    return {"ultima_busqueda": ultima_busqueda}

