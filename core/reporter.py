# guarda y muestra resultados

import os

class LogReporter:
    
    def __init__(self, report_path: str = "reports/log_report.csv"):
        self.report_path = report_path
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
    
    def save_report(self, df):
        """ Guarda el DataFrame en un archivo CSV"""
        try:
            df.to_csv(self.report_path, index=False)
            print(f"Reporte guardado en {self.report_path}")
        except Exception as e:
            print(f"Error al guardar el reporte: {e}")
    
    def show_offhours(self, df):
        
        if df.empty:
            print("No hay eventos fuera de horario laboral.\n")
            return
        else:
            for _, row in df.iterrows():
                print(f"- {row['timestamp']} | user={row['user'] or '-'} | ip={row['ip'] or '-'} | {row['event'] or '-'} ")