FROM python:3.8-slim-buster
COPY . /app
WORKDIR /app
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git
RUN apt-get install build-essential -y
RUN apt-get install python3-dev -y
RUN pip3 install -r requirements.txt
RUN python3 -m dostoevsky download fasttext-social-network-model
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
