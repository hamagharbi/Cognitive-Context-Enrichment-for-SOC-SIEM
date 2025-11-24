FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and rules
COPY src/ src/
COPY rules/ rules/

# Run the application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8002"]
