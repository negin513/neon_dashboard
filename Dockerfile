# Use an official Python runtime as a base image
FROM python:3.8-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port bokeh application port to the world outside this container
EXPOSE 5006

# Set the command to run your Bokeh application
CMD ["bokeh", "serve", "--allow-websocket-origin=127.0.0.1:5006", "neon_dashboard"]
