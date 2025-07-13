# Use official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential gcc default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader vader_lexicon

# Copy project files
COPY . .

# Expose port
EXPOSE 10000

# Set environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=10000

# Start the app
CMD ["flask", "run", "--host=0.0.0.0", "--port=10000"]