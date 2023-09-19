# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 (adjust this if your Flask app runs on a different port)
EXPOSE 5000

# Define the command to run your application
CMD ["python", "app.py"]
