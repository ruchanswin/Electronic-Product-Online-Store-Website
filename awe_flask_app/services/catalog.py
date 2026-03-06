# catalog.py
from utils.file_io import load_data
import os

PRODUCTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "products.json")

def load_products():
    return load_data(PRODUCTS_FILE)
