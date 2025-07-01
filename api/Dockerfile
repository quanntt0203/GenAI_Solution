# Use the official Python image as the base image
ARG PYTHON_TAG
FROM python:${PYTHON_TAG}

# Set the working directory in the container
WORKDIR /app

COPY ./requirements.txt ./

RUN apt-get update && pip install --upgrade pip
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the port the app runs on
EXPOSE 8088

# Command to run the application
CMD ["fastapi", "run", "chatbot_api.py", "--port", "8088"]