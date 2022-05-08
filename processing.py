import os
import pickle
import re
from PIL import Image
import pytesseract

def load_data(image: Image):
    '''
        Process an image for data using pytesseract
        returns lots of information with the most control 
        for custom piecing together the image
    '''

   
    data = pytesseract.image_to_data(image)
    return data


def process_image(image: Image):
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
    data['raw_text'] = lines
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