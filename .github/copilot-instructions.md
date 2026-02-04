# GitHub Copilot Instructions for SimpleMem API

## Project Overview

This is a FastAPI-based REST API service for SimpleMem memory management with a **local-first design philosophy**.

### Core Principles

1. **Local-First**: The default configuration should work entirely locally without external dependencies
2. **Storage Abstraction**: All storage operations go through the `StorageAdapter` interface
3. **Environment-Based Config**: All configuration via environment variables with sensible defaults
4. **Minimal Dependencies**: Only include essential dependencies; avoid bloat

## Architecture

### Storage Abstraction Layer

The `app/storage.py` module provides a storage abstraction:

- **Abstract Base Class**: `StorageAdapter` defines the interface all storage backends must implement
- **LanceDBAdapter**: Default implementation using LanceDB for local vector storage
- **Neo4jAdapter**: Placeholder for future cloud/remote deployments

**When adding storage adapters:**
- Inherit from `StorageAdapter`
- Implement all abstract methods
- Handle errors gracefully with proper return types
- Document configuration requirements in `config.py`
- Update the `get_storage_adapter()` factory function

### Data Models

Models in `app/models.py` define the API contract:

- Use Pydantic for validation
- Match SimpleMem's data schema for compatibility
- Include clear field descriptions
- Use Optional for nullable fields

### Configuration

`app/config.py` uses Pydantic Settings:

- Load from environment variables
- Provide sensible local defaults
- Document all settings
- Use `Optional` for settings that may not be required

## Development Guidelines

### Adding New Endpoints

1. Define request/response models in `app/models.py`
2. Implement handler in `app/main.py`
3. Use proper HTTP status codes
4. Include error handling with HTTPException
5. Add logging for debugging
6. Document in README.md

### Extending Storage

To add a new storage backend:

```python
# 1. Create adapter class in app/storage.py
class MyStorageAdapter(StorageAdapter):
    def __init__(self):
        self._initialized = False
    
    def initialize(self) -> None:
        # Setup connection/storage
        self._initialized = True
    
    # Implement all required methods
    def add_dialogue(self, dialogue: DialogueInput) -> Dict[str, Any]:
        # Implementation
        pass

# 2. Update factory function
def get_storage_adapter() -> StorageAdapter:
    if settings.db_type == "my_storage":
        return MyStorageAdapter()
    # ... existing adapters

# 3. Add config to app/config.py
class Settings(BaseSettings):
    # ... existing settings
    my_storage_setting: Optional[str] = None
```

### Error Handling

- Use try/except blocks around storage operations
- Raise HTTPException with appropriate status codes
- Log errors with context
- Return descriptive error messages

### Testing Locally

Always test changes locally:

```bash
# Start server
python run.py

# Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/dialogue -H "Content-Type: application/json" -d '{"content": "test"}'
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and returns
- Write descriptive docstrings for classes and functions
- Keep functions focused and single-purpose
- Use meaningful variable names

## Common Tasks

### Adding a New Storage Backend

1. Create adapter class inheriting from `StorageAdapter`
2. Implement all abstract methods
3. Add configuration to `Settings`
4. Update `get_storage_adapter()` factory
5. Document in README.md

### Adding a New Endpoint

1. Define models in `app/models.py`
2. Add route handler in `app/main.py`
3. Test manually with curl/httpx
4. Document in README.md API section
5. Update MCP integration docs if relevant

### Modifying Data Model

1. Update models in `app/models.py`
2. Update storage adapter implementations
3. Consider backward compatibility
4. Update API documentation

## SimpleMem Integration

The project uses the `simplemem` package:

- Provides memory storage with semantic search
- Handles embeddings and vector similarity
- May require LLM API keys for embeddings
- Check SimpleMem docs for latest API changes

## MCP Integration Notes

This API serves as a backend for the Model Context Protocol (MCP):

- Keep API responses JSON-serializable
- Use standard HTTP methods and status codes
- Support CORS for cross-origin requests
- Consider MCP client needs when designing endpoints

## Future Considerations

When implementing new features, consider:

- **Neo4j Integration**: Storage adapter for remote/cloud deployments
- **Authentication**: JWT or API key-based auth
- **Rate Limiting**: Prevent abuse of API
- **Caching**: Redis for frequently accessed data
- **Async Operations**: Long-running tasks
- **Monitoring**: Metrics and observability

## Dependencies

Keep dependencies minimal and well-justified:

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **SimpleMem**: Memory management
- **LanceDB**: Local vector storage

Only add new dependencies if absolutely necessary.

### Dependency Management with uv

This project uses `uv` for fast and reliable dependency management:

```bash
# Add a new dependency to pyproject.toml [project.dependencies], then re-lock:

# CPU (recommended default)
uv pip compile pyproject.toml -o requirements.cpu.lock \
    --overrides overrides.cpu.txt \
    --index-url https://pypi.org/simple \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --index-strategy unsafe-best-match

# CUDA-oriented lock (used by the CUDA Docker image)
uv pip compile pyproject.toml -o requirements.lock

# Update all dependencies:

# CPU (recommended default)
uv pip compile pyproject.toml -o requirements.cpu.lock --upgrade \
    --overrides overrides.cpu.txt \
    --index-url https://pypi.org/simple \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --index-strategy unsafe-best-match

# CUDA-oriented lock (used by the CUDA Docker image)
uv pip compile pyproject.toml -o requirements.lock --upgrade

# Install dependencies in a new environment (CPU default):
uv venv
source .venv/bin/activate
uv pip sync requirements.cpu.lock \
    --index-url https://pypi.org/simple \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --index-strategy unsafe-best-match
```

### GPU/CUDA Support

For CUDA-enabled deployments (optional):

```bash
# After base installation, upgrade PyTorch to CUDA version
uv pip install torch torchvision torchaudio --upgrade --index-url https://download.pytorch.org/whl/cu130
```

This accelerates embedding generation and model inference on NVIDIA GPUs.

## Testing Philosophy

- Test locally before committing
- Use real SimpleMem operations in development
- Test error cases and edge conditions
- Verify storage persistence across restarts

## Questions?

When in doubt:
1. Check existing patterns in the codebase
2. Prioritize local-first design
3. Keep it simple and maintainable
4. Document your changes
