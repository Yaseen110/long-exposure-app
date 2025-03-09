# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the app runs on
EXPOSE 8080

# Command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
