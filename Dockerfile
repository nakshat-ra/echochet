# Use a Python base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install SSH server
RUN apt-get update && apt-get install -y openssh-server

# Enable SSH server
RUN mkdir -p /var/run/sshd

# Expose necessary ports
EXPOSE 8000 2222

# Start SSH and the app
CMD service ssh start && uvicorn main:app --host 0.0.0.0 --port 8000
