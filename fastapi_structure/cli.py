import secrets
from importlib import resources
from pathlib import Path

from fastapi_structure.managements.commands.base import copy_files, copy_file, run_alembic

template_dir = resources.files("fastapi_structure.managements.templates")


def create_core():
    secret_key = secrets.token_urlsafe(32)
    copy_files(source_dir=Path(f"{template_dir}/core"),
               target_dir=Path("./app/core"),
               secret_key=secret_key)

    copy_file(file_path=Path(f"{template_dir}/main.tmpl"),
              new_file_path=Path("./main.py"))

    copy_file(file_path=Path(f"{template_dir}/manage.tmpl"),
              new_file_path=Path("./manage.py"))
    run_alembic("alembic init migrations")
