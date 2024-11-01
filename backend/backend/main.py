from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import stellar

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicione a rota
app.include_router(stellar.router, prefix="/api")