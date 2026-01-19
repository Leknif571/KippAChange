FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install UV
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod +x /install.sh && /install.sh && rm /install.sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /project

# Copy dependencies files first
COPY pyproject.toml uv.lock .env ./

# Install dependencies inside the image (creates .venv)
RUN uv sync

# Add the app folder
COPY src ./src
COPY main.py ./
# Add PATH to venv for uvicorn
ENV PATH="/project/.venv/bin:${PATH}"

EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
