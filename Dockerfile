# backend/Dockerfile

FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# --- NEW LINE IS HERE ---
# Run the build script during the Docker build process.
# This will create the chroma_db folder inside the final image.
RUN python build_vector_store.py

# The CMD line remains the same
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:${PORT}"]