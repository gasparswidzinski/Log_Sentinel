# lo que hace read_logs.py

from collections import Counter
import pandas as pd


class LogAnalyzer:
    
    def __init__(self, parser, rules = None):
        self.parser = parser
        self.rules = rules or {}
    
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
            raise

    def summarize(self, df):
        """Realiza un analisis basico de los logs"""
        
        count = df['event'].value_counts()
        for evnt, qvt in count.items():
            print(f"{evnt}: {qvt}")
    
    def detect_offhour(self, df):
        
        wh = self.rules.get("working_hours", {"start":9, "end":18})
        start = int(wh.get("start",9))
        end = int(wh.get("end",18))
        df_ts = df[df["timestamp"].notna()].copy()
        if df_ts.empty: return df_ts
        df_ts["hour"] = df_ts["timestamp"].dt.hour
        fuera = df_ts[(df_ts["hour"] < start) | (df_ts["hour"] > end)]
        return fuera
        
    
    def detect_bruteforce(self,df):
        
        cfg = self.rules.get("failed_login", {})
        threshold = int(cfg.get("threshold", 5))
        failed = df[df["event"] == "failed_login"].copy()
        if failed.empty:
            return failed
        
        counts = failed.groupby("ip").size().reset_index(name='count')
        suspects = counts[counts['count'] >= threshold]
        
        return failed.merge(suspects[["ip"]], on="ip" , how="inner")
        
        