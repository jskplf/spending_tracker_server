## Spending Tracker API and OCR Documentaion

### Build Instructions
1. Install on local machine 
- this installation requires you to have tesseract-ocr and any Python version > 3.6
installed on your computer
- this installation installs packages in your local development environment 
- this server may not run on a local windows environment due to an issue with uvicorn 
- there may be issues du to CORS headers when uploading a file
```
# navigate to the project directory 

# Install project dependencies
pip install -m requirements.txt

# run server, should be accessible to all devices on your local network as http://yourhomeip:8888 or http://localhost:8888 on your local machine
uvicorn api:app  --host 0.0.0.0 --port 8888
```

2. Docker build instructions
- this installation requires docker
- this is the recommended way to build and run the server
  
```
# build container 
docker build -t ocr_api .
docker run ocr_api
```

[go to for full documentation](https://spendingtracker-ocr.herokuapp.com/docs#/default/upload_ocr__post) 
