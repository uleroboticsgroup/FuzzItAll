######################################################################
#
# Dockerfile - Script to deploy the FuzzItAll web service on a Docker
#              container.
#
######################################################################

FROM python:3.9-alpine

# install support for different version control systems
RUN apk update \
    && apk add --no-cache \
    git openssh

# define working directory and switch to it
RUN adduser -D -g '' fuzzitall
WORKDIR /home/fuzzitall

# create a virtual environment and install dependencies
COPY requirements.txt requirements.txt
RUN python -m venv venv \
    && venv/bin/pip install -r requirements.txt \
    && venv/bin/pip install gunicorn

# copy application files
COPY app app
COPY entrypoint.py boot.sh ./
COPY config config

# setup deployment
RUN chmod +x boot.sh \
    && mkdir -p ./instance/tmp ./instance/log \
    && chown -R fuzzitall:fuzzitall ./
ENV FLASK_APP entrypoint.py
ENV FLASK_ENV development
ENV FIA_SETTINGS_MODULE "config.${FLASK_ENV}"

# setup the container to run the boot script
USER fuzzitall
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]