FROM python:3.9-slim-bullseye

WORKDIR /app

# Install curl for healthchecks
RUN apt update
RUN apt install -y curl
# OpenCV dependencies
RUN apt install -y ffmpeg libsm6 libxext6

# Setup a nonroot user for security
RUN adduser --disabled-password nonroot
USER nonroot

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir --upgrade -r requirements.txt

# Copy the inference module
COPY job_tracker /app/job_tracker

# Copy the app
COPY server/main.py /app/main.py

# Expose the app's port
EXPOSE 8080

# Run the CherryPy server
ENTRYPOINT ["python"] 
CMD ["main.py"]