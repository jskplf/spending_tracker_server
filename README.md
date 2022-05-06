## Spending Tracker API and OCR Documentaion

### Build Instructions
```
# navigate to the project directory 

# Install project dependencies
pip install -m requirements.txt

# run server, should be accessible to all devices on your local network as http://yourhomeip:8888
uvicorn api:app  host=0.0.0.0 port=8888
```

go to localhost:8888/docs for full documentation 
