FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv for fast package management
RUN python -m pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml requirements.cpu.lock ./
COPY app ./app
COPY run.py ./

# Install dependencies from the lockfile, then install the package itself
RUN uv pip sync --system requirements.cpu.lock \
    --index-url https://pypi.org/simple \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --index-strategy unsafe-best-match && \
  uv pip install --system --no-deps .

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
  CMD python -c "import http.client; conn = http.client.HTTPConnection('localhost', 8000); conn.request('GET', '/health'); resp = conn.getresponse(); exit(0 if resp.status == 200 else 1)" || exit 1

# Run the application using the installed script
CMD ["simplemem-api", "--host", "0.0.0.0", "--port", "8000"]
