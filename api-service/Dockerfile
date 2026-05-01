FROM python:3.10-slim

WORKDIR /app

# Install dependencies first for Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the API runs on
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]