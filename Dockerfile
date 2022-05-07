FROM python

COPY . .

RUN pip install -r requirements.txt

# For Heroku servers only
CMD uvicorn api:app --host 0.0.0.0 --port $PORT