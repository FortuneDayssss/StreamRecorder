#!/bin/bash

# init directories
if [ $ENV_PROFILE = "production" or $ENV_PROFILE = "dev-docker"]; then
    echo "env: docker"
    mkdir -p "/src"
    mkdir -p "/db"
    mkdir -p "/video"
else
    echo "env: without docker"
    mkdir -p "../data/src"
    mkdir -p "../data/db"
    mkdir -p "../data/video"
fi

# update models
python3 manage.py makemigrations StreamRecorder
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:5000
