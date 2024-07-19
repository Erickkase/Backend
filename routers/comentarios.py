#Librerias de Fastapi
from fastapi import APIRouter, HTTPException
#Librerias del api de Youtube
from googleapiclient.discovery import build
#Libreria para trabajar con url
from urllib.parse import urlparse, parse_qs
#Importacion del objeto que administra la base de datos
from db.conexion import db_client

#ApiKey para usar los Servicios de Youtube
YOUTUBE_API_KEY = "AIzaSyBaMHRgO6vINzR9QuRr2CG0dhILlevjhGU"

#Crea la nueva ruta para los comentarios
router=APIRouter(prefix="/comments",tags=["comments"],responses={404:{"message":"No encontrado"}})

#Funciones

# Función para obtener el ID del canal a partir del handle
def get_channel_id_by_handle(handle: str) -> str:

    #Creamos las credenciales para usar el api de Youtube
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    #Creamos la peticion para el api de youtube en la cual nos va a buscar el video mandandole en handle y que nos retorne un channel con un maximo de resultados de 1
    request = youtube.search().list(
        part="snippet",
        q=handle,
        type="channel",
        maxResults=1
    )

    #Realizamos la peticion al api
    response = request.execute()
    
    #Si la lista de resultado es mayor a cero regresamos el canal, si no regresamos el detail Canal no encontrado
    if "items" in response and len(response["items"]) > 0:
        return response["items"][0]["snippet"]["channelId"]
    else:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    
# Función para obtener los últimos videos del canal a partir del id
def get_latest_videos(channel_id: str):

    #Creamos las credenciales para usar el api de Youtube
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    
    #Creamos la peticion para el api de youtube en la cual nos va a buscar los videos del canal id con un maximo de resultados de 5 y ordenados por fecha
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=5,
        order="date"
    )

    #Realizamos la peticion al api
    response = request.execute()
    
    #Regresamos el titulo del video y la url del video usando el id
    return [{"title": item["snippet"]["title"], "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"} for item in response.get("items", []) if item["id"]["kind"] == "youtube#video"]

# Función para obtener el ID del video a partir de la URL
def get_video_id_from_url(url: str) -> str:

    #Funcion para convertir en tupla la url
    parsed_url = urlparse(url)

    #Funcion para conseguir el id del video
    video_id = parse_qs(parsed_url.query).get("v")

    #Si existe el video retorna el id, si no retorna Invalid YouTube URL
    if video_id:
        return video_id[0]
    else:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
# Función para obtener los comentarios más likeados de un video
def get_top_comments(video_id: str, num_comments: int = 5):

    #Creamos las credenciales para usar el api de Youtube
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    #Creamos la peticion para que nos traiga en tipo lista los comentarios por el video id por la relevancia que tiene es decir los likes
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=num_comments,
        order="relevance"
    )

    #Realizamos la peticion al api
    response = request.execute()
    
    #Creamos una lista de los comentarios
    comments = []

    #Agrega los comentarios con el author el texto los likes y el video url
    for item in response.get("items", []):
        top_comment = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "author": top_comment["authorDisplayName"],
            "text": top_comment["textDisplay"],
            "likes": top_comment["likeCount"],
            "video_url": f"https://www.youtube.com/watch?v={video_id}"  
        })

    #Ordena la lista de los comentarios por los likes
    comments_sorted = sorted(comments, key=lambda x: x["likes"], reverse=True)[:num_comments]
    
    #Regresa los comentarios ordenados
    return comments_sorted


#Rutas del api

#Solicitud para ultimos videos: tre los ultimos videos del canal
@router.get("/latest_videos/")
async def latest_videos(usuario: str, handle: str):

    #Llama a la funcion para recopilar el id del canal desde el handle
    channel_id = get_channel_id_by_handle(handle)

    #Llama a la funcion para recopilar los ultimos videos
    videos = get_latest_videos(channel_id)

    #Genera el modelo para guardarlo en la base de datos con la busqueda realizada
    busqueda = {
        "solicitud": "latest_videos",
        "busqueda": handle,
        "videos": videos
    }

    #Actualiza las busquedas del usuario, si el usuario no existe lo creara
    db_client.usuarios.update_one(
        {"usuario": usuario},
        {"$push": {"busquedas": busqueda}, "$setOnInsert": {"usuario": usuario}},
        upsert=True 
    )
    
    #Regresa los videos del canal
    return {"videos": videos}

# Solicitud para los comentarios más likeados del video que se le envie, si no se envia el numero de comentarios se añade automaticamente 5
@router.get("/top_comments/")
async def top_comments(usuario: str, video_url: str, num_comments: int = 5):

    #Llama a la funcion para recopilar el id del video desde la url
    video_id = get_video_id_from_url(video_url)

    #Llama a la funcion para conseguir los comentarios mas likeados del video
    comments = get_top_comments(video_id, num_comments)

    #Genera el modelo para guardarlo en la base de datos con la busqueda realizada
    busqueda = {
        "solicitud": "top_comments",
        "busqueda": video_url,
        "numero de comentarios": num_comments,
        "comentarios": comments
    }

    #Actualiza las busquedas del usuario, si el usuario no existe lo creara
    db_client.usuarios.update_one(
        {"usuario": usuario},
        {"$push": {"busquedas": busqueda}, "$setOnInsert": {"usuario": usuario}},
        upsert=True 
    )

    #Regresa los comentarios mas likeados del video
    return {"comments": comments}

#Solicitud para los comentarios mas likeados de los ultimos videos, si no se envia el numero de comentarios se añade automaticamente 5
@router.get("/top_comments_latest_videos/")
async def top_comments_latest_videos(usuario: str, handle: str, num_comments_per_video: int = 5):
    #Llama a la funcion para recopilar el id del canal desde el handle
    channel_id = get_channel_id_by_handle(handle)

    #Llama a la funcion para recopilar los ultimos videos
    videos = get_latest_videos(channel_id)
    
    #Crea donde se guardaran los comentarios de los videos
    top_comments_all_videos = []

    #Un bucle donde por cada video se encuentra su id, se recopilan los comentarios y de ahi los añade a la lista de top_comments_all_videos
    for video in videos:
        video_id = get_video_id_from_url(video["url"])
        top_comments = get_top_comments(video_id, num_comments_per_video)
        top_comments_all_videos.extend(top_comments)
    
    #Ordenamos los comentarios por los mas likeados y lo agregamos a la lista top_comments_sorted
    top_comments_sorted = sorted(top_comments_all_videos, key=lambda x: x["likes"], reverse=True)[:len(videos) * num_comments_per_video]
    
    #Genera el modelo para guardarlo en la base de datos con la busqueda realizada
    busqueda = {
        "solicitud": "top_comments_latest_videos",
        "busqueda": handle,
        "numero de comentarios por video": num_comments_per_video,
        "comentarios": top_comments_sorted
    }

    #Actualiza las busquedas del usuario, si el usuario no existe lo creara
    db_client.usuarios.update_one(
        {"usuario": usuario},
        {"$push": {"busquedas": busqueda}, "$setOnInsert": {"usuario": usuario}},
        upsert=True 
    )

    #Regresa los comentarios mas likeados del canal
    return {"top_comments": top_comments_sorted}