import uvicorn

from fastapi_structure.managements.commands.base import Command


class Runserver(Command):
    name = "runserver"
    help = "FastAPI server 가 실행됩니다."

    def execute(self, host_port=None, host="localhost", port="8000"):
        if host_port:
            host, port = host_port.split(":")
        else:
            host, port = host, port

        uvicorn.run("main:app", host=host, port=int(port), reload=True)