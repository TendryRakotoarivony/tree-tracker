FROM python:3.8-slim

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt --no-cache-dir && \
    apt-get update && apt-get -y install libglib2.0-0; \
    apt-get clean

EXPOSE 8501
ENTRYPOINT ["streamlit","run"]
CMD ["Home.py"]
