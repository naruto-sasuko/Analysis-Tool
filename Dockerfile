# Base Python image
FROM python:3.11-slim

# Prevent interactive prompts and configure Python runtime
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    STREAMLIT_SERVER_PORT=7860 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Install essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up user with UID 1000 as required by Hugging Face Spaces
RUN useradd -m -u 1000 user
WORKDIR /app

# Install Python requirements
COPY --chown=user requirements.txt /app/
USER user
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy application source code
COPY --chown=user . /app/

# Hugging Face Spaces standard port
EXPOSE 7860

# Run Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
