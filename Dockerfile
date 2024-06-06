FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends pipenv && \
    apt-get install -y --no-install-recommends libgl1-mesa-dev && \
    apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-ind && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the application code and the model directory
COPY ./app /app

# Set the working directory
WORKDIR /app

# Expose the port that the app runs on
EXPOSE 8006

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8006"]
