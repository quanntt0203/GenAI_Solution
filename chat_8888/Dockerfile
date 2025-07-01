# Use the official Python image as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

COPY ./chat/requirements.txt ./

RUN apt-get update && apt-get install git -y && apt-get install curl -y

# Install any required Python packages
#RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY ./chat /app

# Expose the port the app runs on
EXPOSE 8888

#HEALTHCHECK CMD curl --fail http://localhost:8888/_stcore/health

ENTRYPOINT ["streamlit", "run", "chat_8888.py", "--server.port=8888"]

# Command to run the application
#CMD ["streamlit", "run", "chat_8888.py", "--server.port=8888"]