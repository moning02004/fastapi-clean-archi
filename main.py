from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from app.core.auth import AuthTokenMiddleware
from app.modules.recipe.interfaces.controller import router as recipe_router
from app.modules.user.interfaces.controller import router as user_router

auth_header = APIKeyHeader(name="Authorization", auto_error=False)
app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # ✅ OPTIONS 포함
    allow_headers=["*"],
)
