### 프로젝트 세팅 후 수정사항

1. 프로젝트 세팅
```python
fastapi-setup
```

2. migrations/env.py 코드 수정
```python
# config 대체
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# target_metadata 대체
target_metadata = BaseModel.metadata
```
