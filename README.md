## FastAPI with Clean-Architecture
> 클린 아키텍처 구조를 적용한 FastAPI.

- fastapi-setup 을 통해 프로젝트를 초기화하고 manage.py 명령어를 통해 손쉽게 모듈을 추가할 수 있도록 구현.
```bash
fastapi-setup
```

- --help 를 통해 명령어를 확인할 수 있습니다.
```bash
python3 manage.py --help
```

### 커스텀 명령어 추가 방법
- `{PROJECT_DIR}/managements/commands/` 아래 Command 를 상속받아 명령어를 추가할 수 있습니다.
```bash
python3 manage.py {command_name}
```