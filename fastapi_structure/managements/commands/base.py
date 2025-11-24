import abc
import os
import subprocess
from abc import ABC


class Command(ABC):
    name: str = None
    help: str = None

    @abc.abstractmethod
    def execute(self):
        raise NotImplementedError


def run_alembic(alembic_command: str):
    subprocess.run(alembic_command.split(" "))


def copy_file(file_path, new_file_path, **kwargs):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().format(**kwargs)

    with open(new_file_path, 'w', encoding='utf-8') as f:
        f.write(data)
    print(f"✅ Created {file_path}")


def copy_files(source_dir, target_dir, **kwargs):
    for file_path in source_dir.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(source_dir)
            relative_path = relative_path.with_suffix(".py")
            new_file_path = target_dir / relative_path

            if os.path.isfile(new_file_path):
                print(f"⚠️  {file_path} already exists, skipping")
                continue

            new_file_path.parent.mkdir(parents=True, exist_ok=True)
            copy_file(file_path, new_file_path, **kwargs)
