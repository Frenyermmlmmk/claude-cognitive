# API Layer

**Purpose:** REST API endpoints for task management
**Entry Point:** `src/main.py`
**Status:** Active

---

## Quick Reference

**Endpoints:**
- `GET /health` - Health check
- `GET /tasks` - List all tasks
- `POST /tasks` - Create task
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

---

## Architecture

```
Request → FastAPI Router → Task Manager → Database
                                ↓
                        Response (JSON)
```

---

## Core Routes

### Health Check
```python
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### Create Task
```python
@app.post("/tasks")
def create_task(task: TaskCreate):
    return task_manager.create(task)
```

---

## Request/Response Format

**Create Task:**
```json
// Request
{
  "title": "Example task",
  "description": "Optional description"
}

// Response
{
  "id": 1,
  "title": "Example task",
  "description": "Optional description",
  "completed": false,
  "created_at": "2024-12-30T12:00:00"
}
```

---

## Error Handling

**Common Errors:**
- `404`: Task not found
- `422`: Validation error (invalid input)
- `500`: Server error

---

## Testing

**Unit Tests:**
```bash
pytest tests/test_api.py
```

---

**Last Updated:** 2024-12-30
