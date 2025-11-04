# main.py

import json
from core.parser import LogParser
from core.analyzer import LogAnalyzer
from core.reporter import LogReporter
try:
    from rich.panel import Panel
    from rich.console import Console
except ImportError:
    Console = None

def main():
    
    """ inicializacion de console rich """
    console = Console()
    
    """ se abre el archivo y se cargan las reglas desde rules.json """
    with open("rules.json",'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    """ se inicializa parser, analyzer y reporter """
    log_path = "logs/sample.log"
    parser = LogParser()
    analyzer = LogAnalyzer(parser, rules = rules)   
    reporter = LogReporter()
    
    
    try:
        
        """ lee y normaliza el log en un dataframe """
        df = analyzer.read_log_file(log_path)
        print(f"se procesaron {len(df)} lineas ")
        
        """ imprime el conteo de eventos por tipo """
        analyzer.summarize(df)
        
        """ detecta eventos fuera de horario y posibles ataques de fuerza bruta """
        fuera = analyzer.detect_offhour(df)
        brute, thr, win = analyzer.detect_bruteforce(df)
        
        print("\nEventos fuera de horario laboral:")
        
        """ muestra los resultados """
        reporter.show_offhours(fuera)
        reporter.show_bruteforce(brute,thr,win)
        
        """ guarda los reportes en archivos csv """
        reporter.save_report(df, "reports/full_log_report.csv")
        reporter.save_report(fuera, "alerts/offhours_report.csv")
        reporter.save_report(brute, "alerts/bruteforce_report.csv")
        console.print(Panel.fit("[bold green]✅ Análisis completado[/bold green]\n"
                        "Reportes guardados en [yellow]reports/[/yellow] y [yellow]alerts/[/yellow]",
                        title="[ Log Sentinel ]", border_style="green"))
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
     
            
if __name__ == "__main__":
    main()
