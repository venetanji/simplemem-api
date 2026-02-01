# FastAPI SimpleMem REST API - Implementation Summary

## Overview

This PR implements a complete FastAPI-based REST API service for SimpleMem memory management with a local-first design philosophy. The service provides a backend for the Model Context Protocol (MCP) repository and supports future remote/cloud deployments.

## High-Level Architecture

### Design Principles

1. **Local-First**: Runs entirely on local machine using LanceDB for vector storage
2. **Storage Abstraction**: Clean separation between API and storage using adapter pattern
3. **Environment-Based Config**: All configuration via environment variables
4. **Future-Proof**: Designed to support both local and remote (Neo4j) deployments

### Components

```
simplemem-api/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Environment-based configuration
│   ├── main.py              # FastAPI application with endpoints
│   ├── models.py            # Pydantic request/response models
│   └── storage.py           # Storage abstraction layer
├── .github/
│   └── copilot-instructions.md  # Development guidelines
├── .env.example             # Example environment configuration
├── .gitignore              # Git ignore rules
├── pyproject.toml          # Project metadata and dependencies
├── README.md               # Comprehensive documentation
├── requirements.lock       # Locked dependencies (uv)
└── run.py                  # Application entrypoint
```

### Storage Abstraction Layer

The `StorageAdapter` abstract base class defines a consistent interface:

- **LanceDBAdapter**: Default implementation using SimpleMem with local LanceDB
- **Neo4jAdapter**: Placeholder for future cloud/remote deployments
- **Factory Pattern**: `get_storage_adapter()` selects backend based on configuration

This design allows:
- Seamless switching between storage backends
- No client code changes when migrating from local to cloud
- Independent development of new storage adapters
- Consistent API regardless of backend

### SimpleMem Integration

Uses `simplemem` package's `SimpleMemSystem`:
- `add_dialogue(speaker, content, timestamp)` - Add single memory
- `add_dialogues(dialogues)` - Batch add memories
- `finalize()` - Process and finalize memories
- `ask(question)` - Query memories with natural language
- `get_all_memories()` - Retrieve all memory records

### Data Model

**Input (Dialogue)**:
- `speaker`: Person speaking
- `content`: What was said
- `timestamp`: When it was said (optional, ISO format)

**Output (MemoryEntry)**:
- `entry_id`: Unique identifier
- `lossless_restatement`: Processed memory content
- `keywords`: Extracted keywords
- `timestamp`: When created
- `location`: Associated location
- `persons`: People mentioned
- `entities`: Named entities
- `topic`: Memory category

## REST API Endpoints

### Core Endpoints

- **GET /** - Welcome message
- **GET /health** - Health check with initialization status
- **POST /dialogue** - Add single dialogue
- **POST /dialogues** - Batch add dialogues
- **POST /finalize** - Finalize memory storage
- **POST /query** (alias **/ask**) - Query memories, returns natural language answer
- **GET /retrieve** - Retrieve all raw memory records (optional limit)
- **GET /stats** - Get memory statistics (count, table name, db path)
- **DELETE /clear** - Clear all memories (requires confirmation=true)

### Request/Response Examples

**Add Dialogue**:
```json
POST /dialogue
{
  "speaker": "John",
  "content": "We need to finish the project by Friday",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Query Memories**:
```json
POST /query
{
  "query": "When is the project deadline?"
}

Response:
{
  "answer": "Based on your conversation with John, the project needs to be finished by Friday."
}
```

**Get Stats**:
```json
GET /stats

Response:
{
  "count": 42,
  "table_name": "memories",
  "db_path": "./simplemem_data",
  "db_type": "lancedb"
}
```

## Local Usage

### Installation

```bash
# Install uv (if not already installed)
pip install uv

# Clone repository
git clone https://github.com/venetanji/simplemem-api.git
cd simplemem-api

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip sync requirements.lock
```

### Configuration

Create `.env` file:

```bash
# Required: OpenAI-compatible API for SimpleMem
MODEL_NAME=gpt-4
API_KEY=your-openai-api-key

# Optional: Customize storage
DB_PATH=./simplemem_data
DB_TYPE=lancedb
TABLE_NAME=memories
```

### Running

```bash
python run.py
```

Server starts at `http://localhost:8000`

### MCP Integration

Set environment variable in MCP client:

```bash
export SIMPLEMEM_API_URL=http://localhost:8000
```

MCP client can now make requests to all endpoints.

## Future Remote/Cloud Support

### Neo4j Integration Plan

1. Implement `Neo4jAdapter` in `app/storage.py`
2. Add Neo4j configuration to `app/config.py`:
   - `NEO4J_URI`
   - `NEO4J_USER`
   - `NEO4J_PASSWORD`
3. Set `DB_TYPE=neo4j` in environment
4. No changes needed to API endpoints or client code

### Migration Path

**Local → Cloud**:
1. Deploy API service to cloud (AWS, GCP, Azure)
2. Set up Neo4j instance
3. Update environment variables
4. MCP clients point to cloud URL: `https://api.example.com`

**Zero client changes** - same API interface for all deployments.

## Technical Details

### Dependencies (via uv)

- **FastAPI** 0.128.0 - Web framework
- **Uvicorn** 0.40.0 - ASGI server
- **Pydantic** 2.12.5 - Data validation
- **SimpleMem** 0.1.0 - Memory management
- **LanceDB** 0.27.1 - Local vector storage

### Requirements

- Python 3.10+
- OpenAI-compatible API key (SimpleMem requires for LLM operations)
- 500MB+ disk space for LanceDB and models

### Security

- ✅ CodeQL scan: No vulnerabilities found
- ✅ Code review: All issues addressed
- ⚠️ CORS set to allow all origins (TODO: restrict in production)
- ✅ Input validation via Pydantic models
- ✅ Type-safe configuration
- ✅ Proper error handling and logging

## Development Guidelines

### Adding Dependencies

```bash
# Add to pyproject.toml [project.dependencies], then:
uv pip compile pyproject.toml -o requirements.lock
uv pip sync requirements.lock
```

### Extending Storage Backends

1. Create new adapter class inheriting from `StorageAdapter`
2. Implement all abstract methods
3. Update `get_storage_adapter()` factory
4. Add configuration to `Settings` class
5. Document in README

### Testing

```bash
# Health check
curl http://localhost:8000/health

# Add dialogue
curl -X POST http://localhost:8000/dialogue \
  -H "Content-Type: application/json" \
  -d '{"speaker": "User", "content": "Test memory"}'

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "what did I say?"}'
```

## Benefits

1. **Easy Setup**: Works out of box with sensible defaults
2. **Data Privacy**: All data stays local by default
3. **Fast Dependency Management**: uv provides reliable, reproducible builds
4. **Flexible**: Switch between storage backends without code changes
5. **MCP Compatible**: Designed specifically for MCP integration
6. **Production Ready**: Comprehensive error handling, logging, health checks
7. **Well Documented**: Extensive README and Copilot instructions
8. **Secure**: No known vulnerabilities, input validation, type safety

## Summary

This implementation provides a complete, production-ready FastAPI service for SimpleMem with:
- Local-first design using LanceDB
- Clean storage abstraction for future Neo4j support
- Full REST API matching SimpleMem capabilities
- Comprehensive documentation and examples
- Fast dependency management with uv
- Security scanning and code review completed
- Ready for both local development and cloud deployment
