# AGENTS.md - Agent Coding Guidelines

This document provides guidelines for AI agents working in this repository.

## Project Overview

- **Project Name**: bpm-backend (B站合集视频观看进度管理工具)
- **Type**: Python FastAPI backend
- **Database**: MySQL with SQLAlchemy/SQLModel
- **Package Manager**: uv（同时保留 `requirements.txt` 供部署环境使用）
- **API Docs**: 接口文档见 `API.md`

## Build & Development Commands

### Running the Application

```bash
# Start the development server (port 8001)
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Running Tests

Since no test framework is currently configured, install pytest:

```bash
# Install pytest
uv pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run a single test file
pytest tests/test_file.py

# Run a single test function
pytest tests/test_file.py::test_function_name

# Run tests matching a pattern
pytest -k "test_name_pattern"

# Run with verbose output
pytest -v
```

### Linting & Type Checking

Install recommended tools:

```bash
uv pip install ruff mypy
```

```bash
# Run ruff linter
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Run mypy type checker
mypy .

# Format code with ruff
ruff format .
```

## Code Style Guidelines

### General Principles

- Use **Python 3.12+** features (type hints, structural pattern matching)
- Follow **PEP 8** style guide
- Keep functions small and focused (single responsibility)
- Use descriptive names for variables and functions

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Functions/variables | snake_case | `get_collection_from_db`, `season_id` |
| Classes | PascalCase | `Collection`, `Video` |
| Constants | UPPER_SNAKE_CASE | `BILIBILI_API_BASE` |
| Database tables | snake_case (plural) | `videos`, `collections` |

### Type Hints

- **Always use type hints** for function parameters and return types
- Use `Optional[X]` instead of `X | None` for compatibility
- Import types from `typing` module (List, Dict, Any, Optional)

```python
# Good
def get_collection_from_db(session: Session, season_id: int) -> List[Tuple[Collection, Video]]:
    ...

# Avoid
def get_collection_from_db(session, season_id):
    ...
```

### Import Organization

Order imports in three sections (separate with blank lines):

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
from typing import List, Optional, Tuple
from datetime import datetime

from sqlmodel import Session, select
from fastapi import Depends, HTTPException, status

from models.collection import Collection
from services.collection_service import create_collection_to_db
```

### File Structure

```
project/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration settings
├── database.py          # Database engine and session
├── .env.template        # 环境变量模板（复制为 .env 后填写）
├── API.md               # API 接口文档
├── models/              # SQLModel ORM classes
│   ├── collection.py
│   └── video.py
├── services/            # Business logic layer
│   ├── collection_service.py
│   └── video_service.py
├── apis/                # API route handlers
│   └── collection_video/
│       └── router.py
└── utils/               # Utility functions
    └── bilibiliApi.py
```

### Error Handling

- Use FastAPI's `HTTPException` for HTTP errors
- Catch specific exceptions before generic ones
- Return meaningful error messages to clients

```python
from fastapi import HTTPException, status

# Good
try:
    result = get_collection_from_db(session, season_id)
except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="系统繁忙，请稍后再试")

# Avoid bare except clauses
```

### Database Patterns

- Use SQLModel for ORM models
- Define `__tablename__` explicitly in lowercase plural
- Use `session.flush()` after writes, `session.commit()` to finalize
- Use dependency injection for session: `session: Session = Depends(get_session)`

```python
class Video(SQLModel, table=True):
    __tablename__ = "videos"
    
    bvid: str = Field(max_length=12, sa_column=Column(CHAR(12), primary_key=True))
    title: str = Field(max_length=50)
```

### API Route Patterns

- Use async/await for route handlers
- Return consistent response format:
  ```python
  {
      "status": "success",
      "code": 200,
      "message": "操作描述",
      "data": {...}
  }
  ```
- Use appropriate HTTP status codes (201 CREATED, 200 OK, etc.)

### Pydantic Models

- Use for request/response validation
- Define in router files for endpoint-specific models

```python
class CreateCollectionRequest(BaseModel):
    bvid: str
```

### Configuration

- Use `.env` file for environment variables
- Use `python-dotenv` for loading
- Never hardcode secrets in code

```python
from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")  # with default
```

## Testing Guidelines

- Place tests in a `tests/` directory
- Use `pytest` with `pytest-asyncio` for async tests
- Use `httpx` for making test requests to FastAPI
- Follow naming: `test_<module>_<function>.py`

## Working with Git

- Create feature branches for new features
- Write clear commit messages
- Run linting before committing:
  ```bash
  ruff check . && ruff format . && mypy .
  ```

## Common Issues

- **Database connection**: Ensure MySQL is running and `.env` is configured
- **Port conflicts**: Default port is 8001 (configurable in `main.py`)
- **Import errors**: Ensure you're running from project root with activated venv
- **API docs**: Endpoint details are in `API.md`
- **Logs**: `main.py` creates `logs/app.log` on startup
