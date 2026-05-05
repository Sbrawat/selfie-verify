# 1. Use an official, lightweight Python Linux image
FROM python:3.10-slim

# 2. Stop Python from writing .pyc files and force it to print logs instantly
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install system-level C++ dependencies required for face_recognition (dlib) and OpenCV
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy the requirements file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy all your backend code into the container
COPY . .

# 7. Expose the port the API will run on
EXPOSE 8000

# 8. The command to start the API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]