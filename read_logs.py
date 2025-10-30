# read_logs.py

from utils import parse_line
from collections import Counter
import pandas as pd

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
        print(df.head())
        df.to_csv("reports/logs_procesados.csv", index=False)       
        
    except FileNotFoundError:
        print(f"Error: El archivo {log_path} no se encontro")
    