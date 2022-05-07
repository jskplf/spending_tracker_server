FROM ubuntu:22.04
RUN apt-get update \
    && apt-get install tesseract-ocr -y \
    python3 \
    #python-setuptools \
    python3-pip \
    && apt-get clean \
    && apt-get autoremove

COPY . .

RUN pip3 install -r requirements.txt

# For Heroku localhost only, will make the api accsessible on all devices on 
# local network
CMD uvicorn api:app --host 0.0.0.0 --port $PORT