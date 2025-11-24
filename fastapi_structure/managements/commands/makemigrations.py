from fastapi_structure.managements.commands.base import Command, run_alembic


class Makemigrations(Command):
    name = "makemigrations"
    help = "db migration 파일을 생성합니다."

    def execute(self, message="auto_migration"):
        run_alembic(f"alembic revision --autogenerate -m {message}")
