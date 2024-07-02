# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run main.py when the container launches
CMD ["python", "main.py"]

