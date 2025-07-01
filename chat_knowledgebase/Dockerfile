# Use the official Python image as the base image
ARG PYTHON_TAG
FROM python:${PYTHON_TAG}

# Set the working directory in the container
WORKDIR /app

COPY ./requirements.txt ./

RUN apt-get update && apt-get install git -y && apt-get install curl -y

# Install any required Python packages
#RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY ./src /app

# Expose the port the app runs on
EXPOSE 8889

#HEALTHCHECK CMD curl --fail http://localhost:8889/_stcore/health

ENTRYPOINT ["streamlit", "run", "chat_knowledgebase.py", "--server.port=8889"]

# Command to run the application
#CMD ["streamlit", "run", "chat_knowledgebase.py", "--server.port=8889"]