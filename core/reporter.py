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
        print("\n Eventos fuera de horario:")
        if df.empty:
            print(" - No se encontraron.")
            return
        print(f"{'timestamp':<20} | {'user':<10} | {'ip':<15} | {'event':<15}")
        print("-"*80)
        for _, r in df.iterrows():
            print(f"{str(r['timestamp']):<20} | {(r['user'] or '-'):<10} | {(r['ip'] or '-'):<15} | {r['event']:<15}")
