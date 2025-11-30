import os

import typer

from app.core.config import settings
from fastapi_clean_archi.managements.commands.base import Command, run_alembic


class Check(Command):
    name = "check"
    help = "세팅 확인"

    def execute(self, message=typer.Argument("auto_migration")):
        print(settings.dict())
