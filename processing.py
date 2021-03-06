import os
import pickle
import re
from PIL import Image
import pytesseract

EXPRESSIONS = {}
EXPRESSIONS['date'] = r'\d{2,2}[-.]\d{2,2}[-.]\d{2,4}'
EXPRESSIONS['total'] = r'\d+. ?\d\d '
EXPRESSIONS['address'] = r'[A-Z]{2} \d{5}'

def load_data(image: Image):
    '''
        Process an image for data using pytesseract
        returns lots of information with the most control 
        for custom piecing together the image
    '''

   
    data = pytesseract.image_to_data(image)
    return data

# This is the current method of processing the receipts 
# It relies on a global variable call [EXPRESSIONS] which 
# contains field names and corresponding regex
def process_image(image: Image):
    receipt_data = {}
    # loop through all of the receipts
    raw_text = pytesseract.image_to_string(image)
    receipt_data['raw_text'] = raw_text

    # proccess the raw text
    # 2. Go through the dictionary of reg exp keys/fields
    for k in EXPRESSIONS.keys():
        if (k == 'total'):
            if(re.findall(EXPRESSIONS[k],raw_text) != []):
                receipt_data[k] = re.findall(EXPRESSIONS[k],raw_text)[-1]
            else:
                receipt_data[k] = 'Missing'
        elif(k == 'address'):
            address = re.findall(EXPRESSIONS[k],raw_text)
            if(address != []):
                address = address[0]
                receipt_data[k] = address
            else:
                receipt_data[k] ='Missing'
        else:
            if(len(re.findall(EXPRESSIONS[k],raw_text)) ):
                receipt_data[k] = re.findall(EXPRESSIONS[k],raw_text)
            else:
                receipt_data[k] = 'Missing'
        
    receipt_data['category'] = 'Missing'
    receipt_data['store'] = raw_text.split('\n')[0]
    return receipt_data

# This is the orginal method of parsing the receipt
def process_image2(image: Image):
    """
        Run custom regex on each line of the receipt 
        and attempt to generate a transaction entry

        ```mermaid
        sequenceDiagram
        teseract->lines
        line->parser
        parser->reciept
        ```
    """
    text = pytesseract.image_to_string(image)
    lines = text.split('\n\n')
    data = {}
    data['store'] = lines[0]
    data['raw_text'] = text
    max_newlines = None
    for l in lines:
        if 'SUBTOTAL' in l.upper() or 'TOTAL':
            data['total'] = l.split()
        if 'TEND' in l:
            data['purchase_method'] = l.split()

        # Find a possible dates in the receipt
        # Reg expression only works for 00/00/00 formatted dates
        if re.search('\d\d/\d\d/\d\d', l) != None:
            for part in l.split():
                if re.search('\d\d/\d\d/\d\d', part) != None:
                    data['parsed_date'] = part
        if max_newlines == None:
            max_newlines = l
        else:
            # Is it possible for a line with no items to have the same new lines as a line with items?
            if max_newlines.count('\n') == l.count('\n'):
                pass
            if max_newlines.count('\n') < l.count('\n'):
                max_newlines = l

    # Assume that the line with the most new lines has the items sold
    data['items'] = max_newlines.split('\n')

    # Parse the item name product code and amount
    for index,i in enumerate(data['items']):
        item = {}
        item['name'] = ''
        item['product_code'] = ''
        item['amount'] = ''
        
        # Assume all letters in an item are part of an items name
        for c in i:
            # Take only letters, no spaces
            if c.isdigit() is not True:
                item['name'] += c
        
        # Find the product code of the item, it should be a long string of only numbers
        split_item = i.split()  

        # Find the amount the item cost
        for x in split_item :
            
            if x.isdecimal():
                item['product_code'] = x
            
            if '.' in x:
                item['amount'] = x

        data['items'][index] = item
    return data

def files(path : str):
    for f in os.lisdir(path):
        yield f


def dataset(path: str = 'dataset/'):
    '''
        Process all the files in the directory
    '''
    [load_data([files(path)])]

def to_pck(dataset = dataset):
    '''
        Serialize the collected data to a binary form
    '''
    pickle.dump([dataset()],open('dataset.pck','wb'))

def from_pck(path: str = 'dataset.pck'):
    '''
        Load the data back from the pickle file
    '''
    return pickle.load(open(path))