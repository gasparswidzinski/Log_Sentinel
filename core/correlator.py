# correlator.py

import os
from datetime import timedelta
import pandas as pd

ALERT_DIR = "alerts"

class LogCorrelator:
    
    """
    Motor de correlación de eventos para Log Sentinel.

    - Usa el DataFrame de eventos de la corrida actual (events_df)
    - Puede usar el historial de alertas (history_df)
    - Detecta patrones como:
        * failed_login -> successful_login (correlación local)
        * brute force histórica -> successful_login actual (correlación histórica)
    """
    
    def __init__(self,events_df, history_df = None):
        #copiamos los DataFrames para evitar modificar los originales
        self.events_df = events_df.copy() if events_df is not None else pd.DataFrame()
        self.history_df = history_df.copy() if history_df is not None else pd.DataFrame()
        
        #normalizamos timestamps
        if "timestamp" in self.events_df.columns:
            self.events_df['timestamp'] = pd.to_datetime(self.events_df['timestamp'], errors='coerce')
        
        if "event_timestamp" in self.history_df.columns:
            self.history_df['event_timestamp'] = pd.to_datetime(self.history_df['event_timestamp'], errors='coerce')
            
        os.makedirs(ALERT_DIR, exist_ok=True)
        
    
    # ------------------------------------------------------------------ #
    # 1) CORRELACIÓN LOCAL: failed_login -> successful_login (misma IP/usuario)
    # ------------------------------------------------------------------ #
    
