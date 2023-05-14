FROM python:3.10-slim

WORKDIR /app

# Copy Pipfile & entrypoint.sh
COPY Pipfile Pipfile.lock ./

# Install dependencies, Python PIP Upgrade & Install Pipenv
RUN apt-get update \
    && apt-get -y install curl gnupg2 libglib2.0-0 \
    && apt-get clean \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir pipenv \
    && pipenv install -d --system --deploy

# Copy all files
COPY . /app

# Set environment variables
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION=us-west-2

ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION

# Expose port
EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
