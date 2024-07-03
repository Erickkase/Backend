import os
from fastapi import FastAPI, HTTPException 
from googleapiclient.discovery import build
from pydantic import BaseModel
from typing import List

app = FastAPI()
YOUTUBE_API_KEY = "AIzaSyBaMHRgO6vINzR9QuRr2CG0dhILlevjhGU"


# Función para obtener el ID del canal a partir del handle
def get_channel_id_by_handle(handle: str) -> str:
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    request = youtube.channels().list(
        part="id",
        forUsername=handle
    )
    response = request.execute()
    
    if "items" in response and len(response["items"]) > 0:
        return response["items"][0]["id"]
    else:
        # Si no encuentra el canal por nombre de usuario, intenta buscarlo como un "handle"
        request = youtube.channels().list(
            part="id",
            forUsername=handle
        )
        response = request.execute()
        if "items" in response and len(response["items"]) > 0:
            return response["items"][0]["id"]
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

@app.get("/latest_videos/")
def latest_videos(handle: str):
    channel_id = get_channel_id_by_handle(handle)
    videos = get_latest_videos(channel_id)
    return {"videos": videos}
