FROM python:3.10-slim

# Install Graphviz and fonts for diagrams library
RUN apt-get update \
	&& apt-get install -y --no-install-recommends graphviz fonts-dejavu-core \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 8000 to Docker
EXPOSE 8000

# Use Uvicorn to run FastAPI, listen on all interfaces
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]