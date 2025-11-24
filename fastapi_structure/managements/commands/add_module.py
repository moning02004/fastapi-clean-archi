from importlib import resources

from fastapi_structure.managements.commands.base import Command, copy_files

template_dir = resources.files("fastapi_structure.managements.templates")


class AddModule(Command):
    name = "add_module"
    help = "구조화된 모듈을 추가합니다."

    def execute(self, module_name=None):
        class_name = module_name.capitalize()
        module_name = module_name.lower()

        copy_files(source_dir=f"{template_dir}/app_module",
                   target_dir=f"./app/modules/{module_name}",
                   module_name=module_name,
                   module_class=class_name)
