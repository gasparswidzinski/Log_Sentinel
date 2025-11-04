# guarda y muestra resultados

import os

class LogReporter:
    
    def __init__(self, report_path: str = "reports/log_report.csv"):
        self.report_path = report_path
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
    
    def save_report(self, df, filename="log_report.csv"):
            """
            Guarda un DataFrame en CSV.
            Si 'filename' es una ruta absoluta o contiene '/', se usa tal cual.
            Si no, se guarda dentro del directorio 'outdir'.
            """
            # Si filename incluye una ruta (por ejemplo 'reports/alertas.csv'), úsala directamente
            if os.path.dirname(filename):
                path = filename
            else:
                path = os.path.join(self.outdir, filename)

            # Crear carpeta si no existe
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Guardar CSV
            df.to_csv(path, index=False)
            print(f" Reporte guardado en {path}")
            
    def show_offhours(self, df):
        print("\n Eventos fuera de horario:")
        if df.empty:
            print(" - No se encontraron.")
            return
        print(f"{'timestamp':<20} | {'user':<10} | {'ip':<15} | {'event':<15}")
        print("-"*80)
        for _, r in df.iterrows():
            print(f"{str(r['timestamp']):<20} | {(r['user'] or '-'):<10} | {(r['ip'] or '-'):<15} | {r['event']:<15}")
            
    def show_bruteforce(self, df):
        print(" \n sospecha de fuerza bruta (failed_login):")
        if df.empty:
            print(" ninguna IP supero el umbral")
            return
        else:
            for ip,sub in df.groupby("ip"):
                print(f" - IP: {ip}, intentos fallidos: {len(sub)}")
