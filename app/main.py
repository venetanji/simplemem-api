"""
Main FastAPI application for SimpleMem REST API
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.models import (
    DialogueInput,
    DialogueBatchInput,
    QueryInput,
    QueryResponse,
    StatsResponse,
    ClearRequest,
    HealthResponse,
    MessageResponse,
    MemoryRecord,
)
from app.storage import get_storage_adapter, StorageAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage adapter instance
storage: StorageAdapter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global storage
    
    # Startup
    logger.info("Initializing SimpleMem API...")
    try:
        storage = get_storage_adapter()
        storage.initialize()
        logger.info(f"Storage initialized: {settings.db_type} at {settings.db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize storage: {e}")
        # Don't fail startup, but storage operations will fail
    
    yield
    
    # Shutdown
    logger.info("Shutting down SimpleMem API...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI-based REST API for SimpleMem memory management",
    lifespan=lifespan,
)

# Add CORS middleware for MCP client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint"""
    return MessageResponse(
        message=f"Welcome to {settings.app_name} v{settings.app_version}",
        success=True
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        simplemem_initialized=storage.is_initialized() if storage else False
    )


@app.post("/dialogue", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_dialogue(dialogue: DialogueInput):
    """
    Add a single dialogue/memory to SimpleMem
    """
    if not storage or not storage.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not initialized"
        )
    
    try:
        result = storage.add_dialogue(dialogue)
        if result.get("success"):
            return MessageResponse(message=result["message"], success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
    except Exception as e:
        logger.error(f"Error adding dialogue: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/dialogues", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_dialogues(batch: DialogueBatchInput):
    """
    Add multiple dialogues/memories to SimpleMem in batch
    """
    if not storage or not storage.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not initialized"
        )
    
    try:
        result = storage.add_dialogues(batch.dialogues)
        if result.get("success"):
            return MessageResponse(
                message=result["message"],
                success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
    except Exception as e:
        logger.error(f"Error adding dialogues: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/finalize", response_model=MessageResponse)
async def finalize():
    """
    Finalize memory storage (process pending items, commit changes)
    """
    if not storage or not storage.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not initialized"
        )
    
    try:
        result = storage.finalize()
        if result.get("success"):
            return MessageResponse(message=result["message"], success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
    except Exception as e:
        logger.error(f"Error finalizing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/query", response_model=QueryResponse)
async def query_memories(query: QueryInput):
    """
    Query memories using semantic search - returns an answer
    """
    if not storage or not storage.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not initialized"
        )
    
    try:
        answer = storage.query(query.query)
        return QueryResponse(answer=answer)
    except Exception as e:
        logger.error(f"Error querying memories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/ask", response_model=QueryResponse)
async def ask(query: QueryInput):
    """
    Alias for /query - ask questions about memories
    """
    return await query_memories(query)


@app.get("/retrieve", response_model=list[MemoryRecord])
async def retrieve_memories(limit: int = None):
    """
    Retrieve raw memories (all or limited)
    """
    if not storage or not storage.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not initialized"
        )
    
    try:
        memories = storage.retrieve_all(limit=limit)
        return memories
    except Exception as e:
        logger.error(f"Error retrieving memories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get memory statistics (count, table name, db info)
    """
    if not storage or not storage.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not initialized"
        )
    
    try:
        stats = storage.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/clear", response_model=MessageResponse)
async def clear_memories(request: ClearRequest):
    """
    Clear all memories (requires confirmation)
    """
    if not storage or not storage.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not initialized"
        )
    
    if not request.confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation required to clear memories. Set 'confirmation' to true."
        )
    
    try:
        result = storage.clear()
        if result.get("success"):
            return MessageResponse(message=result["message"], success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
    except Exception as e:
        logger.error(f"Error clearing memories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
