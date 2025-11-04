# guarda y muestra resultados

import os
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except ImportError:
    Console = None
console = Console()

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
                base_dir = os.path.dirname(self.report_path)
                path = os.path.join(self.outdir, filename)

            # Crear carpeta si no existe
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Guardar CSV
            df.to_csv(path, index=False)
            print(f" Reporte guardado en {path}")
            
    def show_offhours(self, df):
        console.print("\n [bold cyan]Eventos fuera de horario:")
        if df.empty:
            print(" [green] No se encontraron.")
            return
        
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Timestamp",style= "dim")
        table.add_column("User")
        table.add_column("IP")
        table.add_column("Event", style="bold")
        
        for _, r in df.iterrows():
            table.add_row(str(r['timestamp']), r['user'] or '-', r['ip'] or '-', r['event'])
        console.print(table)
        
            
    def show_bruteforce(self, df, threshold=None, window_minutes=None):
        console.print("\n Sospecha de fuerza bruta (failed_login):")
        if df.empty:
            console.print(f" - Ninguna IP superó el umbral (≥ {threshold}"
                + (f" en {window_minutes} min" if window_minutes else "") + ").")
            return

        for ip, sub in df.groupby("ip"):
            qty = len(sub)
            info = f" - IP: {ip}, intentos fallidos: {qty}"
            if window_minutes:
                info += f" (regla: ≥{threshold} en {window_minutes} min)"
            else:
                info += f" (regla: ≥{threshold})"
            print(info)
            # detalles opcionales
            for ts, user in zip(sub["timestamp"], sub["user"]):
                console.print(f"    • {ts}  user={user or '-'}")