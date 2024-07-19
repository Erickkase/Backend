from fastapi import FastAPI
from routers import comentarios,analisis
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#CORS
origins = [
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Routers
app.include_router(comentarios.router)
app.include_router(analisis.router)

@app.get("/")
async def root():
    return "Proyecto Desarrollo de Sistemas" 
