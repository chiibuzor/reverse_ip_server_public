# Use the official Python image as a base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Create a new user 'appuser' with UID/GID 1000
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Change ownership of the working directory to 'appuser'
RUN chown -R appuser:appuser /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any dependencies required by the application
RUN pip install mysql-connector-python

# Expose the port number the app runs on
EXPOSE 8080

# Switch to 'appuser' and define the command to run your application
USER appuser
CMD ["python", "app.py"]
