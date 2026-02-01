# SimpleMem API

FastAPI-based REST API service for SimpleMem memory management. This service provides a backend for the Model Context Protocol (MCP) repo with local-first design and support for future remote deployments.

## Features

- 🚀 **Local-First Design**: Run entirely on your local machine with LanceDB
- 🔌 **REST API**: Full REST endpoints for memory management
- 🧠 **SimpleMem Integration**: Leverages the `simplemem` package for intelligent memory storage
- 🔄 **Storage Abstraction**: Pluggable storage backends (LanceDB now, Neo4j later)
- ⚙️ **Environment-Based Config**: Easy configuration via environment variables
- 🏥 **Health Monitoring**: Built-in health check endpoints

## Architecture Overview

### Local-First Design

The SimpleMem API is designed with a **local-first** approach:

1. **Default Storage**: Uses LanceDB for local vector storage with no external dependencies
2. **Data Privacy**: All data stays on your machine by default
3. **Zero Configuration**: Works out of the box with sensible defaults
4. **Environment Variables**: Configure database path, table name, and optional LLM settings

### Storage Abstraction

The API uses a storage adapter pattern that allows for different backends:

- **LanceDBAdapter**: Current default implementation using LanceDB for local persistence
- **Neo4jAdapter**: Placeholder for future cloud/remote deployments with Neo4j

This abstraction ensures:
- Consistent API interface regardless of backend
- Easy migration from local to cloud deployments
- Ability to support multiple storage types simultaneously

### Data Model

Memories are stored with the following schema (matching SimpleMem's MemoryEntry):
- `entry_id`: Unique identifier for the memory
- `lossless_restatement`: Processed memory content
- `keywords`: Extracted keywords
- `timestamp`: When the memory was created (ISO format string)
- `location`: Associated location
- `persons`: People mentioned
- `entities`: Named entities
- `topic`: Memory topic/category

Input dialogues require:
- `speaker`: The person speaking
- `content`: What was said
- `timestamp`: (optional) When it was said

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (fast Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/venetanji/simplemem-api.git
cd simplemem-api
```

2. Install uv if you haven't already:
```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

3. Create a virtual environment and install dependencies with uv:
```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies from lock file
uv pip sync requirements.lock
```

Alternatively, install directly without creating a venv:
```bash
uv pip install -r requirements.lock
```

### Configuration

Create a `.env` file for custom configuration (optional):

```bash
cp .env.example .env
```

Edit `.env` to customize settings:

```bash
# Storage Settings
DB_PATH=./simplemem_data
DB_TYPE=lancedb
TABLE_NAME=memories

# LLM Settings (REQUIRED for SimpleMem operations)
# SimpleMem requires an OpenAI-compatible API for embeddings and memory processing
MODEL_NAME=gpt-4
API_KEY=your-openai-api-key-here
```

**Note**: SimpleMem requires an API key for LLM operations (embeddings and memory processing). Without a valid API key, the storage will not initialize. You can use:
- OpenAI API key with models like `gpt-4`, `gpt-3.5-turbo`
- Compatible APIs (Azure OpenAI, local LLM endpoints, etc.)

### GPU/CUDA Support (Optional)

For CUDA-enabled deployments to accelerate embedding generation and model inference:

```bash
# After installing base dependencies, install PyTorch with CUDA support
# For CUDA 13.0:
uv pip install torch torchvision torchaudio --upgrade --index-url https://download.pytorch.org/whl/cu130

# For CUDA 12.1:
uv pip install torch torchvision torchaudio --upgrade --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8:
uv pip install torch torchvision torchaudio --upgrade --index-url https://download.pytorch.org/whl/cu118
```

This will replace the CPU-only PyTorch with the CUDA-enabled version. Verify GPU availability:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")
```

**Requirements**: NVIDIA GPU with appropriate CUDA toolkit installed on the system.

### Running the Service

Start the API server:

```bash
python run.py
```

Or use uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## Testing

Install dev dependencies (includes `pytest` + `httpx`) and run the test suite:

```bash
uv pip install -e '.[dev]'
uv run python -m pytest -q
```

## API Endpoints

### Health Check

```bash
GET /health
```

Returns service status and version information.

### Add Single Dialogue

```bash
POST /dialogue
Content-Type: application/json

{
  "speaker": "John",
  "content": "Had a great discussion about AI",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Add Multiple Dialogues (Batch)

```bash
POST /dialogues
Content-Type: application/json

{
  "dialogues": [
    {
      "speaker": "Alice",
      "content": "First dialogue...",
      "timestamp": "2024-01-15T10:00:00Z"
    },
    {
      "speaker": "Bob",
      "content": "Second dialogue...",
      "timestamp": "2024-01-15T10:05:00Z"
    }
  ]
}
```

### Finalize Storage

```bash
POST /finalize
```

Commits pending changes and finalizes memory storage.

### Query Memories

```bash
POST /query
Content-Type: application/json

{
  "query": "What did I discuss about AI?"
}
```

The response will be an answer generated by SimpleMem based on your stored memories:

```json
{
  "answer": "You had a great discussion about AI with John at a coffee shop..."
}
```

Or use the alias:

```bash
POST /ask
```

### Retrieve Raw Memories

```bash
GET /retrieve?limit=100
```

Returns raw memory records without semantic search.

### Get Statistics

```bash
GET /stats
```

Returns memory count, table name, database path, and type.

### Clear All Memories

```bash
DELETE /clear
Content-Type: application/json

{
  "confirmation": true
}
```

## MCP Integration

To use this API as a backend for the MCP (Model Context Protocol) repo:

1. Start the SimpleMem API service (see above)

2. Set the base URL environment variable in your MCP configuration:

```bash
export SIMPLEMEM_API_URL=http://localhost:8000
```

3. The MCP client can now make requests to the SimpleMem API endpoints

Example MCP usage:

```python
import os
import requests

base_url = os.getenv("SIMPLEMEM_API_URL", "http://localhost:8000")

# Add a memory
response = requests.post(
    f"{base_url}/dialogue",
    json={
        "speaker": "User",
        "content": "Important conversation about project deadlines",
        "timestamp": "2024-01-15T14:30:00Z"
    }
)

# Query memories
response = requests.post(
    f"{base_url}/query",
    json={
        "query": "project deadlines"
    }
)
answer = response.json()["answer"]
print(answer)
```

## Development

### Project Structure

```
simplemem-api/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic data models
│   └── storage.py           # Storage abstraction layer
├── .env.example             # Example environment variables
├── .gitignore              # Git ignore rules
├── pyproject.toml          # Project metadata and dependencies
├── README.md               # This file
├── requirements.lock       # Locked Python dependencies (uv)
└── run.py                  # Application entrypoint
```

### Adding or Updating Dependencies

This project uses `uv` for fast and reliable dependency management.

To add a new dependency:
```bash
# Add to pyproject.toml [project.dependencies] section, then:
uv pip compile pyproject.toml -o requirements.lock
uv pip sync requirements.lock
```

To update all dependencies:
```bash
uv pip compile pyproject.toml -o requirements.lock --upgrade
uv pip sync requirements.lock
```

### Extending Storage Adapters

To add a new storage backend:

1. Create a new adapter class in `app/storage.py` that inherits from `StorageAdapter`
2. Implement all abstract methods
3. Update `get_storage_adapter()` factory function
4. Add configuration options to `app/config.py`

Example:

```python
class MyCustomAdapter(StorageAdapter):
    def initialize(self) -> None:
        # Initialize your storage backend
        pass
    
    def add_dialogue(self, dialogue: DialogueInput) -> Dict[str, Any]:
        # Implement dialogue addition
        pass
    
    # ... implement other methods
```

### Testing

Run the API locally and test with curl:

```bash
# Health check
curl http://localhost:8000/health

# Add a dialogue
curl -X POST http://localhost:8000/dialogue \
  -H "Content-Type: application/json" \
  -d '{"speaker": "User", "content": "Test memory"}'

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | SimpleMem API | Application name |
| `APP_VERSION` | 0.1.0 | API version |
| `DEBUG` | false | Enable debug mode |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `DB_PATH` | ./simplemem_data | Database storage path |
| `DB_TYPE` | lancedb | Database type (lancedb, neo4j) |
| `TABLE_NAME` | memories | Table/collection name |
| `MODEL_NAME` | None | **Required**: LLM model name (e.g., gpt-4) |
| `API_KEY` | None | **Required**: API key for LLM service |
| `NEO4J_URI` | None | Neo4j connection URI |
| `NEO4J_USER` | None | Neo4j username |
| `NEO4J_PASSWORD` | None | Neo4j password |

## Future Enhancements

- [ ] Neo4j integration for cloud deployments
- [ ] Authentication and authorization
- [ ] Rate limiting
- [ ] Async batch processing
- [ ] Webhooks for memory events
- [ ] GraphQL API
- [ ] Memory export/import
- [ ] Advanced search filters
- [ ] Memory versioning

## License

This project is provided as-is for use with SimpleMem and MCP.

## Contributing

Contributions are welcome! Please ensure:
- Code follows the existing style
- New storage adapters implement the full `StorageAdapter` interface
- Documentation is updated for new features
