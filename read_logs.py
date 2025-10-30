# read_logs.py

from utils import parse_line
from collections import Counter
import pandas as pd
import os

def read_log_file(log_path):
    """ Lee un archivo de log y muestra el contenido del mismo en la consola"""
    data_list = []
    try:
        
        with open(log_path, 'r', encoding="utf-8") as f:
            
            for line in f:
                line = line.strip()
                if not line:
                     continue
                 
                 
            
                data = parse_line(line)
                data_list.append(data)
        
        df = pd.DataFrame(data_list)    
        
        return df
    
    except FileNotFoundError:
        print(f"Error: El archivo {log_path} no se encontro")

def analyze_logs(df):
    """ Realiza un analisis basico de los logs"""
    
    print("Resumen por tipo de evento: ")
    count = df['event'].value_counts()
    for evnt, qvt in count.items():
        print(f"{evnt}: {qvt}")
    
    if "timestamp" in df.columns:
        df_ts = df[df["timestamp"].notna()].copy()
        if not df_ts.empty:
            df_ts["hour"] = df_ts["timestamp"].dt.hour
            
            fuera = df_ts[(df_ts["hour"] < 8) | (df_ts["hour"] > 18)]
            print(f"\nEventos fuera de horario laboral (8am-6pm): {len(fuera)}")
            
            if fuera.empty:
                print("No hay eventos fuera de horario laboral.")  
            else:
                print(fuera[["timestamp","user","ip","event","raw_line"]])
    else:
        print("No hay datos de timestamp para analizar horarios.")

    
def save_report(df: pd.DataFrame, report_path: str = "reports/log_report.csv"):
    """ Guarda un reporte basico en un archivo CSV"""
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    df.to_csv(report_path, index=False)
    print(f"Reporte guardado en {report_path}")