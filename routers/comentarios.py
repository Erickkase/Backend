from fastapi import APIRouter, HTTPException
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

YOUTUBE_API_KEY = "AIzaSyBaMHRgO6vINzR9QuRr2CG0dhILlevjhGU"

router=APIRouter(prefix="/comments",tags=["comments"],responses={404:{"message":"No encontrado"}})



#Rutas del api

#Solicitud para ultimos videos
@router.get("/latest_videos/")
def latest_videos(handle: str):
    channel_id = get_channel_id_by_handle(handle)
    videos = get_latest_videos(channel_id)
    return {"videos": videos}

#Solicitud para los comentarios mas likeados
@router.get("/top_comments/")
def top_comments(video_url: str, num_comments: int = 5):
    video_id = get_video_id_from_url(video_url)
    comments = get_top_comments(video_id, num_comments)
    return {"comments": comments}

#Solicitud para los comentarios mas likeados de los ultimos videos
@router.get("/top_comments_latest_videos/")
def top_comments_latest_videos(handle: str, num_comments_per_video: int = 5):
    # Obtener el ID del canal
    channel_id = get_channel_id_by_handle(handle)
    
    # Obtener los últimos 5 videos del canal
    videos = get_latest_videos(channel_id)
    
    # Obtener los comentarios más populares de cada video
    top_comments_all_videos = []
    for video in videos:
        video_id = get_video_id_from_url(video["url"])
        top_comments = get_top_comments(video_id, num_comments_per_video)
        top_comments_all_videos.extend(top_comments)
    
    # Ordenar los comentarios por likes de manera descendente
    top_comments_sorted = sorted(top_comments_all_videos, key=lambda x: x["likes"], reverse=True)[:len(videos) * num_comments_per_video]
    
    return {"top_comments": top_comments_sorted}


#Funciones

# Función para obtener el ID del canal a partir del handle
def get_channel_id_by_handle(handle: str) -> str:
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    request = youtube.search().list(
        part="snippet",
        q=handle,
        type="channel",
        maxResults=1
    )
    response = request.execute()
    
    if "items" in response and len(response["items"]) > 0:
        return response["items"][0]["snippet"]["channelId"]
    else:
        raise HTTPException(status_code=404, detail="Channel not found")
    
# Función para obtener los últimos videos del canal
def get_latest_videos(channel_id: str):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=5,
        order="date"
    )
    response = request.execute()
    
    return [{"title": item["snippet"]["title"], "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"} for item in response.get("items", []) if item["id"]["kind"] == "youtube#video"]

# Función para obtener el ID del video a partir de la URL
def get_video_id_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    video_id = parse_qs(parsed_url.query).get("v")
    if video_id:
        return video_id[0]
    else:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
# Función para obtener los comentarios más likeados de un video
def get_top_comments(video_id: str, num_comments: int = 5):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=num_comments,  # Obtener el número específico de comentarios
        order="relevance"
    )
    response = request.execute()
    
    comments = []
    for item in response.get("items", []):
        top_comment = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "author": top_comment["authorDisplayName"],
            "text": top_comment["textDisplay"],
            "likes": top_comment["likeCount"],
            "video_url": f"https://www.youtube.com/watch?v={video_id}"  # Incluir la URL del video
        })

    comments_sorted = sorted(comments, key=lambda x: x["likes"], reverse=True)[:num_comments]
    
    return comments_sorted