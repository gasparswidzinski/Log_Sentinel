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

def history_stats(df):
    """devuelve las estadisticas basicas en el historial de alertas,
    -total de alertas:
    -conteo por tipo de alerta:
    -top ips con mas alertas:
    -top usuarios con mas alertas:
    """
    
    if df.empty:
        return {
            "total":0,
            "by_type":{},
            "top_ips":{},
            "top_users":{},
        }
    
    stats = {
        "total": len(df),
        "by_type": df['alert_type'].value_counts().to_dict(),
        "top_ips": df['ip'].value_counts().head(5).to_dict(),
        "top_users": df['user'].value_counts().head(5).to_dict(),
    }
    
    return stats

