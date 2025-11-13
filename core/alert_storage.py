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
    
    #normalizo offhours
    if offhours_df is not None and not offhours_df.empty:
        
        #utilizo las columnas originales que ya tengo, timestamp, ip, user, rawline
        off = offhours_df.copy()
        off["timestamp" ] = run_ts
        off["alert_type"] = "offhours"
        
        #se utiliza texto de reglas desde rules.json si esta disponible
        msg = None
        if isinstance(rules,dict):
            wh = rules.get("working_hours", {})
            start = wh.get("start",9)
            end = wh.get("end",18)
            msg = f"evento fuera de horario laboral ({start} - {end})"
        off["rule"] = msg or "evento fuera de horario laboral"
        
        #reordenamos/limitamos columnas
        off = off[["run_timestamp",
                   "timestamp",
                   "alert_type",
                   "ip",
                   "user",
                   "rule",
                   "raw_line"
                   ]].rename(columns={"timestamp":"event_timestamp"})
        frames.append(off)
        
        
        #normalizo bruteforce
        if bruteforce_df is not None and not bruteforce_df.empty:
            brute = bruteforce_df.copy()
            brute["run_timestamp"] = run_ts
            brute["alert_type"] = "bruteforce"
            
            #se utiliza texto de reglas desde rules.json si esta disponible
            msg = None
            if isinstance(rules,dict):
                fr = rules.get("failed_login", {})
                thr = fr.get("threshold", 3)
                win = fr.get("window_minutes")
                if win:
                    msg = f"posible fuerza bruta: >={thr} intentos fallidos en {win} minutos"
                else:
                    msg = f"posible fuerza bruta: >={thr} intentos fallidos"
            brute["rule"] = msg or "posible fuerza bruta detectada"
            
            #reordenamos/limitamos columnas
            brute = brute[["run_timestamp",
                           "timestamp",
                           "alert_type",
                           "ip",
                           "user",
                           "rule",
                           "raw_line"
                           ]].rename(columns={"timestamp":"event_timestamp"})
            frames.append(brute)
                    
          
        
    
    