# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories and set proper permissions
RUN mkdir -p uploads data && \
    chmod 755 uploads data

# Set default environment variables
ENV HOST=0.0.0.0
ENV PORT=8000
ENV RELOAD=false
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Create a script to initialize the database and start the application
RUN echo '#!/bin/sh\n\
python init_db.py\n\
python main.py' > /app/start.sh && \
chmod +x /app/start.sh

# Expose the port from .env
EXPOSE 8000

# Run the start script
CMD ["/app/start.sh"] 