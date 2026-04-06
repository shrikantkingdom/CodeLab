# FastAPI Reference

## Setup
```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

## Basic Structure
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

## Testing
```bash
pip install pytest httpx
pytest
```

## Dependencies
- Use `Depends()` for dependency injection.
- Pydantic models for request/response validation.
