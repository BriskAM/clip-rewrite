# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Set default environment variables
ENV HOST=0.0.0.0
ENV PORT=8000
ENV RELOAD=false
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Expose the port from .env
EXPOSE 8000

# Run the application
CMD ["python", "main.py"] 