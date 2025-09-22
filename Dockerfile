# backend/Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir makes the image smaller
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
# This includes your `app` folder, `build_vector_store.py`, etc.
COPY . .

# Command to run the application using Gunicorn
# Render will automatically inject the correct PORT environment variable
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:${PORT}"]```

---

### 3. `requirements.txt`
*(Place this file in the `backend/` directory)*

**Purpose:** A complete list of all the Python libraries your project needs.