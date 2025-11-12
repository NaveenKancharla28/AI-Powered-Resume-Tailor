# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements (if you don't have one yet, we'll create next)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Install Playwright browsers inside the image (Chromium only = smaller)
RUN python -m playwright install --with-deps chromium

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Expose port 8000 for app
EXPOSE 8000

# Default command to run the app
CMD ["python", "app.py"]



