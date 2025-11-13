# history_reader.py

import os
import pandas as pd

HISTORY_PATH = "data/alert_history.csv"

def load_history():
    """carga el historial completo de alertas desde data/alert_history.csv,
    si el archivo no existe, devuelve un DataFrame vacio"""
    
    if not os.path.exists(HISTORY_PATH):
        print("No se encontro el archivo de historial de alertas.")
        return pd.DataFrame()
    
    df = pd.read_csv(HISTORY_PATH)
    
    #normalizamos timestamp con datetime
    if "run_timestamp" in df.columns:
        df["run_timestamp"] = pd.to_datetime(df["run_timestamp"], errors='coerce')
    
    if "event_timestamp" in df.columns:
        df["event_timestamp"] = pd.to_datetime(df["event_timestamp"], errors='coerce')
        
    return df


