import json
import os
import pickle
import traceback
from typing import List
from fastapi import FastAPI, File,UploadFile

from pandas import DataFrame, read_pickle
from tqdm import tqdm
import processing
from PIL import Image
from io import BytesIO

app = FastAPI(title='OCR Api', description='An api for interacting with a receipt processing OCR')

DATASET = 'dataset/'
SERIALIZED_PATH = 'dataset.pck' # a serialized version of the results from the initial dataset

# As long as the dataset hasn't gained any new files don't reprocess it
d = []
try:
    d = pickle.load(open(SERIALIZED_PATH, 'rb'))
except:
    # Initialize the receipt image data set
    dataset = os.listdir(DATASET)
    

    d = []
    # Process each image in the dataset
    for image in tqdm(dataset, f'Loading initial dataset from {DATASET}'):
        image = f'{DATASET}{image}'
        try:
            d.append(processing.process_image(Image.open(image)))
        except:
            traceback.print_exc()
            print(f'{image} gave an error')
    
    # Serialize the dataset so that it doesn't need to re processed the next time the server starts
    pickle.dump(d,open(SERIALIZED_PATH,'wb'))
        
# Put data set results into a dataframe 
df = DataFrame(d)

app = FastAPI(title='Spending Tracker OCR API', description='An api to process a receipt through ocr',version=1.0)

@app.get('/')
async def index():
    """
        Root endpoint of the api
        - can be used to test if the endpoint is working
    
        1. Use threads to a check for one regex on whole document, multiple workers = multiple regex and matchs being found at the same time
        - each type a regex tests positive for a field give it a vote
        - assume break up the line based on the amount of votes a type gets 
        - issue is that 
    """
    return {'status_code': 200, 'message': 'Welcome to 370 backend'} 

@app.post('/ocr/')
async def upload(files: List[UploadFile] = File(..., description='Multiple images uploaded for processing ')):
    images = [await f.read() for f in files]
    data = []
    for image in images:
        data.append(processing.process_image(Image.open(BytesIO(image))))

    return {"status_code" : 200, "data": data}

@app.get('/receipt_data/')
async def receipt_data_view():
    """
        return all data collected from proccessing the free 
        receipt database with tesseract ocr
        - [Link to dataset](https://expressexpense.com/blog/free-receipt-images-ocr-machine-learning-dataset/)
    """

    df_stats = {}
    df_stats['success_rate'] = get_success()

    data = {'stats': df_stats,'contents': json.loads(df.to_json())}

    return{'status_code': 200, 'data': data}

@app.get('/sample/')
def get_sample(size: int = 5):
    """
        Returns @size number of random receipts that are in the dataset
    """

    return {'status_code': 200, 'data': json.loads(df.head(size).to_json())}


# Put this in processing and give each receipt a likelihood grade
def get_success():
    """
        Calculate and the return a list of all the success rates fro each parameter
        - Success rate = Number of times column is not missing a value / Total number of rows
    """
    out = {}
    for col in df.columns:
        rate = df[col].notnull().sum()/len(df) 
        if rate == 1 or rate == 0:
            out[col] = None
        else:
            out[col] = rate
    return out