import argparse
import re
import secrets
from importlib import resources
from pathlib import Path

from fastapi_clean_archi.managements.commands.base import copy_files, copy_file, run_alembic

template_dir = resources.files("fastapi_clean_archi.managements.templates")


def edit_file(filename, remove_line_words, add_lines, line_number):
    path = Path(filename)
    lines = path.read_text().splitlines()

    for index in range(len(lines)):
        for x in remove_line_words:
            if lines[index].startswith(x):
                lines[index] = ""
    path.write_text("\n".join(lines[:line_number] + add_lines + lines[line_number:]))


def create_core():
    secret_key = secrets.token_urlsafe(32)
    copy_files(source_dir=Path(f"{template_dir}/core"),
               target_dir=Path("./app/core"),
               secret_key=secret_key)

    copy_file(file_path=Path(f"{template_dir}/__init__.tmpl"),
              new_file_path=Path("./app/__init__.py"))

    copy_file(file_path=Path(f"{template_dir}/main.tmpl"),
              new_file_path=Path("./main.py"))

    copy_file(file_path=Path(f"{template_dir}/pytest.tmpl"),
              new_file_path=Path("./pytest.ini"))

    copy_file(file_path=Path(f"{template_dir}/manage.tmpl"),
              new_file_path=Path("./manage.py"))
    run_alembic("alembic init migrations")

    edit_file("./alembic.ini", remove_line_words=["sqlalchemy.url"], add_lines=[], line_number=0)
    edit_file("./migrations/env.py", remove_line_words=["target_metadata = "], add_lines=[
        "",
        "from app.core.config import settings",
        "config.set_main_option(\"sqlalchemy.url\", settings.DATABASE_URL)",
        "",
        "import os, importlib",
        "modules = os.listdir(\"app/modules\")",
        "for module in modules:",
        "    try:",
        "        importlib.import_module(f\"app.modules.{module}.infrastructure.models\")",
        "    except ModuleNotFoundError:",
        "        continue",
        "",
        "from fastapi_clean_archi.core.db.base import BaseModel",
        "target_metadata = BaseModel.metadata"
        "",
    ], line_number=19)
