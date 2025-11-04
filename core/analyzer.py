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
        
    
    def detect_bruteforce(self, df):
        """
        Devuelve (result_df, threshold, window_minutes).
        - Si window_minutes es None: cuenta total por IP >= threshold.
        - Si window_minutes está definido: detecta >= threshold dentro de sliding window de window_minutes.
        """
        cfg = self.rules.get("failed_login", {})
        threshold = int(cfg.get("threshold", 5))
        window = cfg.get("window_minutes", None)

        failed = df[df["event"] == "failed_login"].copy()
        if failed.empty:
            return failed.iloc[0:0].copy(), threshold, window  # empty df, retornamos también umbrales

        # Caso simple (sin ventana)
        if not window:
            counts = failed.groupby("ip").size().reset_index(name="count")
            suspects = counts[counts["count"] >= threshold]["ip"]
            result = failed[failed["ip"].isin(suspects)].copy()
            return result, threshold, window

        # Caso con ventana temporal: uso rolling por index de tiempo
        suspects_list = []
        for ip, group in failed.groupby("ip"):
            g = group.sort_values("timestamp").set_index("timestamp")
            # Necesitamos una columna para contar; usamos 'event'
            # rolling con window de tiempo (pandas >= 0.18) funciona en index datetime
            counts_rolling = g["event"].rolling(f"{int(window)}min").count()
            if (counts_rolling >= threshold).any():
                # Tomo el primer momento en que se cumple la condición y saco la ventana asociada
                first_idx = counts_rolling[counts_rolling >= threshold].index[0]
                window_start = first_idx - pd.Timedelta(minutes=int(window))
                slice_df = g.loc[window_start:first_idx].reset_index()
                slice_df["ip"] = ip
                suspects_list.append(slice_df)

        if suspects_list:
            result = pd.concat(suspects_list, ignore_index=True)
        else:
            result = failed.iloc[0:0].copy()

        return result, threshold, window