FROM python

COPY . .

RUN pip install -r requirements.txt

# For Heroku localhost only, will make the api accsessible on all devices on 
# local network
CMD uvicorn api:app --host 0.0.0.0 --port $PORT