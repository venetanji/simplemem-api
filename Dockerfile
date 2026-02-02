FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv for fast package management
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml requirements.lock ./
COPY app ./app
COPY run.py ./

# Install dependencies using uv
RUN uv pip install --system -r requirements.lock

# Create volume mount point for models and data
VOLUME /app/models
VOLUME /app/data

# Set environment variables for model caching
ENV HF_HOME=/app/models/huggingface
ENV TRANSFORMERS_CACHE=/app/models/huggingface
ENV HF_HUB_CACHE=/app/models/huggingface/hub
ENV TORCH_HOME=/app/models/torch
ENV DB_PATH=/app/data/simplemem_data

# Expose the API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application using uvx
CMD ["python", "-m", "app.cli", "--host", "0.0.0.0", "--port", "8000"]
