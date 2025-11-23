import os
import secrets
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import uvicorn

BASE_DIR = Path(__file__).resolve().parent

# 클린 아키텍처 템플릿
TEMPLATE = {
    "domain/entities.py": '''from dataclasses import dataclass


@dataclass
class {class_name}:
    pk: int
''',
    "services/service.py": '''from app.modules.{name}.domain.entities import {class_name}

class {class_name}Service:
    def __init__(self, repository):
        self.repository = repository
''',
    "infrastructure/models.py": '''import sqlalchemy

from app.core.db.base import BaseModel

''',
    "infrastructure/repository.py": '''from app.modules.{name}.domain.entities import {class_name}
from app.core.db.repository import Repository


class {class_name}Repository(Repository):
    def get_by_pk(self, pk: int | str):
        super().get_by_pk(pk)
''',
    "interfaces/schemas.py": '''import pydantic

class Request(pydantic.BaseModel):
    pass


class Response(pydantic.BaseModel):
    pass
''',
    "interfaces/controller.py": '''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db

router = APIRouter(prefix="/{name}", tags=["{name}s"])

"""
@router.post("/endpoint", response_model=Response)
def endpoint(request: Request, db: Session = Depends(get_db)):
    repository = Repository(db)
    service = Service(repository)

    entity = service.execute()

    # Entity → Response 변환
    return Response(args=entity.args)
"""
''',
    "tests/test_{name}.py": '''from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_{name}():
    response = client.get("/api/v1/{name}/1")
    assert response.status_code == 200
    assert response.json() == {{"id": 1, "name": "{name} sample"}}
''',
}

# core 기본 파일
CORE_TEMPLATE = {
    "core/security.py": '''from datetime import datetime, timedelta
 
import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({{"exp": expire}})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
''',
    "core/config.py": '''from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Clean"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./sqlite3.db"
    SECRET_KEY: str = "{secret_key}"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
''',
    "core/db/base.py": '''from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import as_declarative, declarative_base, declared_attr

Base = declarative_base()


@as_declarative()
class BaseModel(Base):
    pk = Column("id", Integer, primary_key=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    @declared_attr
    def __tablename__(cls):
        meta = getattr(cls, "Meta", None)
        if meta and hasattr(meta, "db_table"):
            return meta.db_table
        return cls.__name__.lower()

''',
    "core/db/session.py": '''from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={{"check_same_thread": False}})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

    ''',
    "core/db/repository.py": '''from sqlalchemy.orm import Session


class Repository:
    DB_MODEL = None

    def __init__(self, db: Session):
        self.db = db

    def get_by_pk(self, pk: int | str):
        instance = self.db.query(self.DB_MODEL).filter(self.DB_MODEL.pk == pk).first()
        return instance
'''
}


def create_core():
    core_dir = BASE_DIR / "app"
    secret_key = secrets.token_urlsafe(32)
    for path, content in CORE_TEMPLATE.items():
        file_path = core_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not file_path.exists():
            with open(file_path, "w") as f:
                f.write(content.format(secret_key=secret_key))
            print(f"✅ Created {file_path}")
        else:
            print(f"⚠️  {file_path} already exists, skipping")
    subprocess.run(["alembic", "init", "migrations"])


def create_module(module_name: str):
    module_dir = BASE_DIR / "app" / "modules" / module_name
    class_name = module_name.capitalize()

    for rel_path, content in TEMPLATE.items():
        file_path = module_dir / rel_path.format(name=module_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            print(f"⚠️  {file_path} already exists, skipping")
            continue
        with open(file_path, "w") as f:
            f.write(content.format(name=module_name, class_name=class_name))
        print(f"✅ Created {file_path}")


def run_alembic(args):
    subprocess.run(["alembic"] + args)


if __name__ == "__main__":
    command = sys.argv[1]

    if command == "start_project":
        create_core()
    else:
        if not os.path.exists(BASE_DIR / "app"):
            print(f"start_project 를 먼저 실행하세요.")
            exit(-1)

    if command == "add_module":
        module_name = sys.argv[2]
        create_module(module_name)
    elif command == "makemigrations":
        msg = sys.argv[2] if len(sys.argv) > 2 else f"auto_migration"
        run_alembic(["revision", "--autogenerate", "-m", msg])
    elif command == "migrate":
        run_alembic(["upgrade", "head"])
    elif command == "downgrade":
        step = sys.argv[2] if len(sys.argv) > 2 else "-1"
        run_alembic(["downgrade", step])
    elif command == "runserver":
        host_port = sys.argv[2] if len(sys.argv) > 2 else "localhost:8000"
        host, port = host_port.split(":")
        uvicorn.run("main:app", host=host, port=int(port), reload=True)
