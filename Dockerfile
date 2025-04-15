FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /budget2025

# Install libpq-dev for llamaindex with postgres chat store integration
RUN apt-get update && apt-get install -y libpq-dev gcc

COPY pyproject.toml uv.lock ./

RUN uv venv --python 3.12

RUN uv sync --frozen

COPY ./app ./app

# Set environment variables
ENV PYTHONPATH=/budget2025 \
    PYTHONUNBUFFERED=1 
# TRANSFORMERS_OFFLINE=0 \
# HF_HUB_ENABLE_HF_TRANSFER=1


EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# activate virtual environment
CMD ["uv", "run", "streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=none"]