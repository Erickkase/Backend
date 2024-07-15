from fastapi import FastAPI
from routers import comentarios

app = FastAPI()

#Routers
app.include_router(comentarios.router)

@app.get("/")
async def root():
    return "Proyecto Desarrollo de Sistemas" 
