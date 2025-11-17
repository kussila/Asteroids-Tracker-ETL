# use an official Python runtime as a parent image
FROM python:3.11-slim

# set the working directory in the container
WORKDIR /app

# copy the current directory contents into the container at /app
COPY . /app

# install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# this is the default command
CMD ["python", "main.py"]