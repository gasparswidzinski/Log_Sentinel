# lo que hace read_logs.py

from collections import Counter
import pandas as pd


class LogAnalyzer:
    
    def __init__(self, parser):
        self.parser = parser
    
    def read_log_file(self, log_path):
        """Lee un archivo de log y devuelve un DataFrame con su contenido"""
        
        data_list = [] 
        try:
            with open(log_path,'r', encoding = "utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    data = self.parser.parse_line(line)
                    data_list.append(data)
            return pd.DataFrame(data_list)
        
        except FileNotFoundError:
            print(f"Error: El archivo {log_path} no se encontro")

    def summarize(self, df):
        """Realiza un analisis basico de los logs"""
        
        count = df['event'].value_counts()
        for evnt, qvt in count.items():
            print(f"{evnt}: {qvt}")
    
    def detect_offhour(self, df):
        
        df_ts = df[df["timestamp"].notna()].copy()
        df_ts["hour"] = df_ts["timestamp"].dt.hour
        fuera = df_ts[(df_ts["hour"] < 8) | (df_ts["hour"] > 18)]
        return fuera 