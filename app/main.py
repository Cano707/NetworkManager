"""Entrancepoint of application"""

import uvicorn
from fastapi import FastAPI
from app.api.v1 import api_router
from app.core import Settings
from app.database import Initializer
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost", 
    "http://localhost:3000"
]

app=FastAPI(title=Settings.PROJECT_NAME)
app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router, prefix=Settings.API_V1_STR)

if __name__ == '__main__':
    Initializer.initialize()
    uvicorn.run(app, host="localhost", port=8000)
    