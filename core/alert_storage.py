# alert_storage.py

import os
from datetime import datetime
import pandas as pd


HISTORY_PATH = "data/alert_history.csv"

def ensure_history_dir():
    """crea la carpeta 'data/' si no existe
    no rompe si ya esta creada"""
    
    
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True) 

def append_alert(offhours_df, bruteforce_df, rules = None):
    
    """recibe los DataFrames de alertas actuales offhours y bruteforce,
    los normaliza a un formato comun y los agrega al archivo data/alerts_history.csv
    -offhours_df: DataFrame con las alertas offhours actuales
    -bruteforce_df: DataFrame con las alertas bruteforce actuales
    -rules: lista de reglas aplicadas (opcional)
    """
    
    ensure_history_dir()
    
    run_ts = datetime.now() #momento en el que se ejecuta el analisis
    
    frames = [] #lista de DataFrames ya normalizados
    
    
    
    