import os
import secrets
import subprocess
import sys
from pathlib import Path

import uvicorn

BASE_DIR = Path(__file__).resolve().parent


def copy_file(source_dir, target_dir, **kwargs):
    for file_path in source_dir.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(source_dir)
            relative_path = relative_path.with_suffix(".py")
            new_file_path = target_dir / relative_path

            if os.path.isfile(new_file_path):
                print(f"⚠️  {file_path} already exists, skipping")
                continue

            new_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read().format(**kwargs)

            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"✅ Created {file_path}")


def create_core():
    secret_key = secrets.token_urlsafe(32)
    copy_file(source_dir=BASE_DIR / "templates/core",
              target_dir=BASE_DIR / "core",
              secret_key=secret_key)
    run_alembic("alembic init migrations")


def create_module(module_name: str):
    class_name = module_name.capitalize()
    module_name = module_name.lower()

    copy_file(source_dir=BASE_DIR / "templates/app_module",
              target_dir=BASE_DIR / "app" / "modules" / module_name,
              module_name=module_name,
              module_class=class_name)


def run_alembic(alembic_command: str):
    subprocess.run(alembic_command.split(" "))


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
