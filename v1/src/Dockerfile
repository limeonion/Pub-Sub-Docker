# our base image
# FROM python:3.6-slim
# FROM gcc:4.9
FROM alpine:3.7

# install Python modules needed by the Python app
COPY requirements.txt /app/
RUN apk add --update g++ gcc
RUN apk add --update python py-pip python-dev python3 py3-pip
RUN apk add --update nodejs
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# copy files required for the app to run
COPY app.py /app/

# tell the port number the container should expose
EXPOSE 80

# run the application
CMD ["python3", "/app/app.py"]
