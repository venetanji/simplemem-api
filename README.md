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

Memories are stored with the following schema (matching SimpleMem):
- `lossless_restatement`: Processed memory content
- `keywords`: Extracted keywords
- `timestamp`: When the memory was created
- `location`: Associated location
- `persons`: People mentioned
- `entities`: Named entities
- `topic`: Memory topic/category
- `vector`: Embedding vector for semantic search

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/venetanji/simplemem-api.git
cd simplemem-api
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
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

# LLM Settings (optional, for embeddings)
MODEL_NAME=gpt-4
API_KEY=your-api-key-here
```

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
  "content": "Had a great discussion about AI with John",
  "timestamp": "2024-01-15T10:30:00Z",
  "location": "Coffee Shop",
  "persons": ["John"],
  "topic": "AI"
}
```

### Add Multiple Dialogues (Batch)

```bash
POST /dialogues
Content-Type: application/json

{
  "dialogues": [
    {
      "content": "First dialogue...",
      "topic": "Topic 1"
    },
    {
      "content": "Second dialogue...",
      "topic": "Topic 2"
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
  "query": "What did I discuss about AI?",
  "limit": 10,
  "threshold": 0.7
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
        "content": "Important conversation about project deadlines",
        "topic": "Work"
    }
)

# Query memories
response = requests.post(
    f"{base_url}/query",
    json={
        "query": "project deadlines",
        "limit": 5
    }
)
memories = response.json()
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
├── requirements.txt        # Python dependencies
└── run.py                  # Application entrypoint
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
  -d '{"content": "Test memory"}'

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 5}'
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
| `MODEL_NAME` | None | LLM model name for embeddings |
| `API_KEY` | None | API key for LLM service |
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
