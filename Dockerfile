# Use an official Python runtime as a parent image
FROM python:3.10.11

# Set the working directory in the container to /app
WORKDIR /app

# Add Pipfiles
COPY Pipfile Pipfile.lock ./

# Install project dependencies
RUN pip install pipenv && pipenv install --system --deploy

# Install Pytest
RUN pip install pytest
RUN pip install pylint
RUN pip install black
# Copy the rest of the working directory contents into the container at /app
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run main.py when the container launches
CMD ["python", "src/main.py"]
