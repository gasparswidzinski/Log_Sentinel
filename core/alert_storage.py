# alert_storage.py

import os
from datetime import datetime
import pandas as pd


HISTORY_PATH = "data/alert_history.csv"

def ensure_history_dir():
    """crea la carpeta 'data/' si no existe
    no rompe si ya esta creada"""
    
    
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True) 

